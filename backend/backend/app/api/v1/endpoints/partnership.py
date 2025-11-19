from fastapi import APIRouter, HTTPException, status
import logging
from typing import Dict, Any
from pydantic import BaseModel, EmailStr

from app.services.email_service import EmailService

router = APIRouter()
logger = logging.getLogger(__name__)


class PartnershipRequest(BaseModel):
    company: str
    contact: str
    email: EmailStr
    message: str = ""


@router.post("/request")
async def request_partnership(partnership_data: PartnershipRequest):
    """Handle partnership request and send email notification"""
    try:
        email_service = EmailService()
        
        # Send email to fundraising2121@gmail.com
        success = await email_service.send_partnership_request(
            company_name=partnership_data.company,
            contact_name=partnership_data.contact,
            contact_email=partnership_data.email,
            message=partnership_data.message
        )
        
        if not success:
            logger.error(f"Failed to send partnership request email for {partnership_data.company}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to send partnership request. Please try again later."
            )
        
        logger.info(f"Partnership request sent successfully for {partnership_data.company}")
        
        return {
            "success": True,
            "message": "Partnership request submitted successfully. We'll get back to you soon!"
        }
        
    except Exception as e:
        logger.error(f"Error processing partnership request: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )
