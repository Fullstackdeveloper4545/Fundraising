from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging

from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.models.user import User
from app.models.receipt import Receipt, ReceiptResponse
from app.services.receipt_service import ReceiptService
from app.core.exceptions import NotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/payment/{payment_id}", response_model=ReceiptResponse)
async def get_payment_receipt(
    payment_id: int,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get receipt for a payment"""
    try:
        supabase = get_supabase()
        receipt_service = ReceiptService(supabase)
        
        receipt = await receipt_service.get_payment_receipt(payment_id)
        if not receipt:
            raise NotFoundException("Receipt not found")
        
        return ReceiptResponse(
            id=receipt.id,
            payment_id=receipt.payment_id,
            receipt_uuid=receipt.receipt_uuid,
            generated_at=receipt.generated_at,
            receipt_url=receipt.receipt_url,
            data=receipt.data
        )
    except Exception as e:
        logger.error(f"Error getting payment receipt: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[ReceiptResponse])
async def get_user_receipts(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get receipts for a user"""
    try:
        # Check if user is requesting their own receipts or is admin
        if user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view these receipts")
        
        supabase = get_supabase()
        receipt_service = ReceiptService(supabase)
        
        receipts = await receipt_service.get_user_receipts(user_id)
        
        receipt_responses = []
        for receipt in receipts:
            receipt_responses.append(ReceiptResponse(
                id=receipt.id,
                payment_id=receipt.payment_id,
                receipt_uuid=receipt.receipt_uuid,
                generated_at=receipt.generated_at,
                receipt_url=receipt.receipt_url,
                data=receipt.data
            ))
        
        return receipt_responses
    except Exception as e:
        logger.error(f"Error getting user receipts: {e}")
        raise HTTPException(status_code=400, detail=str(e))
