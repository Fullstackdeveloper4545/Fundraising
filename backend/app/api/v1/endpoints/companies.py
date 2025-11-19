from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.models.user import User
from app.models.company import Company, CompanyCreate, CompanyResponse, CompanyPartnership, PartnershipCreate
from app.services.company_service import CompanyService
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new company"""
    try:
        supabase = get_supabase()
        company_service = CompanyService(supabase)
        
        # Only admins can create companies
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can create companies")
        
        # Create company
        company = await company_service.create_company(company_data)
        
        return CompanyResponse(
            id=company.id,
            name=company.name,
            contact_email=company.contact_email,
            website=company.website,
            logo_url=company.logo_url,
            description=company.description,
            is_partner=company.is_partner,
            partnership_tier=company.partnership_tier,
            created_at=company.created_at,
            partnerships=None,
            grants=None
        )
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CompanyResponse])
async def get_companies():
    """Get all companies"""
    try:
        supabase = get_supabase()
        company_service = CompanyService(supabase)
        
        companies = await company_service.get_companies()
        
        company_responses = []
        for company in companies:
            company_responses.append(CompanyResponse(
                id=company.id,
                name=company.name,
                contact_email=company.contact_email,
                website=company.website,
                logo_url=company.logo_url,
                description=company.description,
                is_partner=company.is_partner,
                partnership_tier=company.partnership_tier,
                created_at=company.created_at,
                partnerships=None,
                grants=None
            ))
        
        return company_responses
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{company_id}/partnership", response_model=CompanyPartnership)
async def create_partnership(
    company_id: int,
    partnership_data: PartnershipCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a partnership for a company"""
    try:
        supabase = get_supabase()
        company_service = CompanyService(supabase)
        
        # Create partnership
        partnership = await company_service.create_partnership(company_id, partnership_data)
        
        return partnership
    except Exception as e:
        logger.error(f"Error creating partnership: {e}")
        raise HTTPException(status_code=400, detail=str(e))
