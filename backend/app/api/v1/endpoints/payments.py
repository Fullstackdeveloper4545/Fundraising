from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging

from app.core.database import get_supabase
from app.core.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.payment import Payment, PaymentCreate, PaymentResponse, PaymentStatus, PaymentMethod
from app.services.payment_service import PaymentService
from app.core.exceptions import NotFoundException, ValidationException, PaymentException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a new payment/donation"""
    try:
        supabase = get_supabase()
        payment_service = PaymentService(supabase)
        
        # Only donors can donate, but admins can also create payments
        if current_user is None or (getattr(current_user, "role", None) not in ["donor", "admin"]):
            raise HTTPException(status_code=403, detail="Only donors and admins are allowed to create payments")

        # Create payment
        payment = await payment_service.create_payment(payment_data, current_user)
        
        # Send donation confirmation email
        try:
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            # Get campaign details for the email
            campaign_result = supabase.table("campaigns").select("title, user_id").eq("id", payment.campaign_id).execute()
            if campaign_result.data:
                campaign_title = campaign_result.data[0]["title"]
                campaign_owner_id = campaign_result.data[0]["user_id"]
                
                # Get campaign owner details
                owner_result = supabase.table("users").select("first_name, last_name").eq("id", campaign_owner_id).execute()
                if owner_result.data:
                    owner_name = f"{owner_result.data[0]['first_name']} {owner_result.data[0]['last_name']}"
                else:
                    owner_name = "Campaign Owner"
                
                donor_name = payment.donor_name or "Anonymous Donor"
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <h2 style="color: #4F46E5;">💝 Thank You for Your Donation!</h2>
                        <p>Hello {donor_name},</p>
                        <p>Thank you for your generous donation to support <strong>{campaign_title}</strong>!</p>
                        <p><strong>Donation Details:</strong></p>
                        <ul>
                            <li>Amount: ${payment.amount}</li>
                            <li>Campaign: {campaign_title}</li>
                            <li>Campaign Owner: {owner_name}</li>
                            <li>Payment Method: {payment.method.replace('_', ' ').title()}</li>
                            <li>Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC</li>
                        </ul>
                        <p>Your support makes a real difference in helping students achieve their goals.</p>
                        <p>A receipt has been generated and is available for your records.</p>
                        <p>Thank you for supporting student fundraisers!</p>
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                        <p style="color: #6c757d; font-size: 14px;">
                            Best regards,<br>
                            The Fundraising Platform Team
                        </p>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
                Thank You for Your Donation!
                
                Hello {donor_name},
                
                Thank you for your generous donation to support {campaign_title}!
                
                Donation Details:
                - Amount: ${payment.amount}
                - Campaign: {campaign_title}
                - Campaign Owner: {owner_name}
                - Payment Method: {payment.method.replace('_', ' ').title()}
                - Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC
                
                Your support makes a real difference in helping students achieve their goals.
                
                A receipt has been generated and is available for your records.
                
                Thank you for supporting student fundraisers!
                
                Best regards,
                The Fundraising Platform Team
                """
                
                await email_service.send_email(
                    payment.donor_email,
                    "💝 Thank You for Your Donation - Fundraising Platform",
                    html_content,
                    text_content
                )
                logger.info(f"Donation confirmation email sent to {payment.donor_email}")
        except Exception as email_error:
            logger.warning(f"Failed to send donation confirmation email to {payment.donor_email}: {email_error}")
            # Don't fail payment creation if email fails
        
        return PaymentResponse(
            id=payment.id,
            campaign_id=payment.campaign_id,
            donor_email=payment.donor_email,
            donor_name=payment.donor_name,
            amount=payment.amount,
            method=payment.method,
            status=payment.status,
            transaction_id=payment.transaction_id,
            is_anonymous=payment.is_anonymous,
            message=payment.message,
            created_at=payment.created_at,
            processed_at=payment.processed_at
        )
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/campaign/{campaign_id}", response_model=List[PaymentResponse])
async def get_campaign_payments(
    campaign_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get payments for a specific campaign"""
    try:
        supabase = get_supabase()
        payment_service = PaymentService(supabase)
        
        payments = await payment_service.get_campaign_payments(campaign_id)
        
        payment_responses = []
        for payment in payments:
            payment_responses.append(PaymentResponse(
                id=payment.id,
                campaign_id=payment.campaign_id,
                donor_email=payment.donor_email,
                donor_name=payment.donor_name,
                amount=payment.amount,
                method=payment.method,
                status=payment.status,
                transaction_id=payment.transaction_id,
                is_anonymous=payment.is_anonymous,
                message=payment.message,
                created_at=payment.created_at,
                processed_at=payment.processed_at
            ))
        
        return payment_responses
    except Exception as e:
        logger.error(f"Error getting campaign payments: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get a specific payment"""
    try:
        supabase = get_supabase()
        payment_service = PaymentService(supabase)
        
        payment = await payment_service.get_payment_by_id(payment_id)
        if not payment:
            raise NotFoundException("Payment not found")
        
        return PaymentResponse(
            id=payment.id,
            campaign_id=payment.campaign_id,
            donor_email=payment.donor_email,
            donor_name=payment.donor_name,
            amount=payment.amount,
            method=payment.method,
            status=payment.status,
            transaction_id=payment.transaction_id,
            is_anonymous=payment.is_anonymous,
            message=payment.message,
            created_at=payment.created_at,
            processed_at=payment.processed_at
        )
    except Exception as e:
        logger.error(f"Error getting payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/process")
async def process_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user)
):
    """Process a payment (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        supabase = get_supabase()
        payment_service = PaymentService(supabase)
        
        result = await payment_service.process_payment(payment_id)
        if not result:
            raise PaymentException("Failed to process payment")
        
        return {"message": "Payment processed successfully"}
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user)
):
    """Refund a payment"""
    try:
        supabase = get_supabase()
        payment_service = PaymentService(supabase)
        
        # Check if user is authorized to refund
        payment = await payment_service.get_payment_by_id(payment_id)
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Only campaign owner or admin can refund
        campaign = await payment_service.get_campaign_by_payment_id(payment_id)
        if not campaign:
            raise NotFoundException("Campaign not found")
        
        if campaign.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to refund this payment")
        
        result = await payment_service.refund_payment(payment_id)
        if not result:
            raise PaymentException("Failed to refund payment")
        
        return {"message": "Payment refunded successfully"}
    except Exception as e:
        logger.error(f"Error refunding payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[PaymentResponse])
async def get_user_payments(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get payments made by a user"""
    try:
        # Check if user is requesting their own payments or is admin
        if user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view these payments")
        
        supabase = get_supabase()
        payment_service = PaymentService(supabase)
        
        payments = await payment_service.get_user_payments(user_id)
        
        payment_responses = []
        for payment in payments:
            payment_responses.append(PaymentResponse(
                id=payment.id,
                campaign_id=payment.campaign_id,
                donor_email=payment.donor_email,
                donor_name=payment.donor_name,
                amount=payment.amount,
                method=payment.method,
                status=payment.status,
                transaction_id=payment.transaction_id,
                is_anonymous=payment.is_anonymous,
                message=payment.message,
                created_at=payment.created_at,
                processed_at=payment.processed_at
            ))
        
        return payment_responses
    except Exception as e:
        logger.error(f"Error getting user payments: {e}")
        raise HTTPException(status_code=400, detail=str(e))
