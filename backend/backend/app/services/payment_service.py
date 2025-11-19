from typing import Optional, List
from datetime import datetime
import logging
from decimal import Decimal

from app.models.payment import Payment, PaymentCreate, PaymentStatus, PaymentMethod
from app.core.exceptions import NotFoundException, ValidationException, PaymentException

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def create_payment(self, payment_data: PaymentCreate, current_user=None) -> Payment:
        """Create a new payment"""
        try:
            # Set donor_id if user is logged in
            donor_id = current_user.id if current_user else None
            
            # Create payment data
            payment_dict = {
                "campaign_id": payment_data.campaign_id,
                "donor_id": donor_id,
                "donor_email": payment_data.donor_email,
                "donor_name": payment_data.donor_name,
                "amount": float(payment_data.amount),
                "method": payment_data.method.value,
                "status": PaymentStatus.PENDING.value,
                "is_anonymous": payment_data.is_anonymous,
                "message": payment_data.message,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert payment into database
            result = self.supabase.table("campaign_payments").insert(payment_dict).execute()
            
            if not result.data:
                raise ValidationException("Failed to create payment")
            
            payment_data_dict = result.data[0]
            return Payment(**payment_data_dict)
            
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            raise ValidationException(f"Failed to create payment: {str(e)}")

    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        try:
            result = self.supabase.table("campaign_payments").select("*").eq("id", payment_id).execute()
            
            if not result.data:
                return None
            
            return Payment(**result.data[0])
        except Exception as e:
            logger.error(f"Error getting payment by ID: {e}")
            return None

    async def get_campaign_payments(self, campaign_id: int) -> List[Payment]:
        """Get payments for a specific campaign"""
        try:
            result = self.supabase.table("campaign_payments").select("*").eq("campaign_id", campaign_id).order("created_at", desc=True).execute()
            
            payments = []
            if result.data:
                for payment_data in result.data:
                    payments.append(Payment(**payment_data))
            
            return payments
        except Exception as e:
            logger.error(f"Error getting campaign payments: {e}")
            return []

    async def get_user_payments(self, user_id: int) -> List[Payment]:
        """Get payments made by a user"""
        try:
            result = self.supabase.table("campaign_payments").select("*").eq("donor_id", user_id).order("created_at", desc=True).execute()
            
            payments = []
            if result.data:
                for payment_data in result.data:
                    payments.append(Payment(**payment_data))
            
            return payments
        except Exception as e:
            logger.error(f"Error getting user payments: {e}")
            return []

    async def process_payment(self, payment_id: int) -> bool:
        """Process a payment"""
        try:
            # Update payment status to processing
            result = self.supabase.table("campaign_payments").update({
                "status": PaymentStatus.PROCESSING.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", payment_id).execute()
            
            if not result.data:
                return False
            
            # Here you would integrate with payment gateways (Stripe, PayPal, Square)
            # For now, we'll simulate successful processing
            await self._simulate_payment_processing(payment_id)
            
            return True
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False

    async def _simulate_payment_processing(self, payment_id: int):
        """Simulate payment processing"""
        try:
            # Get payment details
            payment = await self.get_payment_by_id(payment_id)
            if not payment:
                return False
            
            # Simulate processing delay
            import asyncio
            await asyncio.sleep(2)
            
            # Update payment status to completed
            result = self.supabase.table("campaign_payments").update({
                "status": PaymentStatus.COMPLETED.value,
                "transaction_id": f"txn_{payment_id}_{datetime.utcnow().timestamp()}",
                "processed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", payment_id).execute()
            
            if result.data:
                # Update campaign amount
                await self._update_campaign_amount(payment.campaign_id, payment.amount)
                
                # Generate receipt
                await self._generate_receipt(payment_id)
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error simulating payment processing: {e}")
            return False

    async def _update_campaign_amount(self, campaign_id: int, amount: Decimal):
        """Update campaign current amount"""
        try:
            # Get current campaign amount
            result = self.supabase.table("campaigns").select("current_amount").eq("id", campaign_id).execute()
            
            if not result.data:
                return False
            
            current_amount = Decimal(str(result.data[0]["current_amount"]))
            new_amount = current_amount + amount
            
            # Update campaign amount
            self.supabase.table("campaigns").update({
                "current_amount": float(new_amount),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", campaign_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating campaign amount: {e}")
            return False

    async def _generate_receipt(self, payment_id: int):
        """Generate receipt for payment"""
        try:
            from app.core.security import generate_receipt_uuid
            
            receipt_uuid = generate_receipt_uuid()
            
            # Create receipt
            receipt_dict = {
                "payment_id": payment_id,
                "receipt_uuid": receipt_uuid,
                "generated_at": datetime.utcnow().isoformat(),
                "data": {
                    "payment_id": payment_id,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
            result = self.supabase.table("receipts").insert(receipt_dict).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error generating receipt: {e}")
            return False

    async def refund_payment(self, payment_id: int) -> bool:
        """Refund a payment"""
        try:
            # Get payment details
            payment = await self.get_payment_by_id(payment_id)
            if not payment:
                return False
            
            # Check if payment can be refunded
            if payment.status != PaymentStatus.COMPLETED:
                raise PaymentException("Only completed payments can be refunded")
            
            # Update payment status to refunded
            result = self.supabase.table("campaign_payments").update({
                "status": PaymentStatus.REFUNDED.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", payment_id).execute()
            
            if result.data:
                # Subtract amount from campaign
                await self._subtract_campaign_amount(payment.campaign_id, payment.amount)
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error refunding payment: {e}")
            return False

    async def _subtract_campaign_amount(self, campaign_id: int, amount: Decimal):
        """Subtract amount from campaign current amount"""
        try:
            # Get current campaign amount
            result = self.supabase.table("campaigns").select("current_amount").eq("id", campaign_id).execute()
            
            if not result.data:
                return False
            
            current_amount = Decimal(str(result.data[0]["current_amount"]))
            new_amount = max(Decimal('0'), current_amount - amount)  # Don't go below 0
            
            # Update campaign amount
            self.supabase.table("campaigns").update({
                "current_amount": float(new_amount),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", campaign_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error subtracting campaign amount: {e}")
            return False

    async def get_campaign_by_payment_id(self, payment_id: int):
        """Get campaign by payment ID"""
        try:
            result = self.supabase.table("campaign_payments").select("campaign_id").eq("id", payment_id).execute()
            
            if not result.data:
                return None
            
            campaign_id = result.data[0]["campaign_id"]
            
            # Get campaign details
            campaign_result = self.supabase.table("campaigns").select("*").eq("id", campaign_id).execute()
            
            if not campaign_result.data:
                return None
            
            return campaign_result.data[0]
        except Exception as e:
            logger.error(f"Error getting campaign by payment ID: {e}")
            return None
