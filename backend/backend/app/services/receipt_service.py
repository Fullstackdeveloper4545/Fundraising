from typing import Optional, List
from datetime import datetime
import logging

from app.models.receipt import Receipt
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ReceiptService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def get_payment_receipt(self, payment_id: int) -> Optional[Receipt]:
        """Get receipt for a specific payment"""
        try:
            result = self.supabase.table("receipts").select("*").eq("payment_id", payment_id).execute()
            
            if not result.data:
                return None
            
            return Receipt(**result.data[0])
        except Exception as e:
            logger.error(f"Error getting payment receipt: {e}")
            return None

    async def get_user_receipts(self, user_id: int) -> List[Receipt]:
        """Get receipts for a user"""
        try:
            # Get receipts through payments made by user
            result = self.supabase.table("receipts").select("*, campaign_payments!inner(*)").eq("campaign_payments.donor_id", user_id).execute()
            
            receipts = []
            if result.data:
                for receipt_data in result.data:
                    receipts.append(Receipt(**receipt_data))
            
            return receipts
        except Exception as e:
            logger.error(f"Error getting user receipts: {e}")
            return []
