from typing import Optional, List
from datetime import datetime
import logging

from app.models.company import Company, CompanyCreate, CompanyPartnership, PartnershipCreate
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class CompanyService:
    def __init__(self, supabase):
        self.supabase = supabase

    async def create_company(self, company_data: CompanyCreate) -> Company:
        """Create a new company"""
        try:
            # Create company data
            company_dict = {
                "name": company_data.name,
                "contact_email": company_data.contact_email,
                "website": company_data.website,
                "logo_url": company_data.logo_url,
                "description": company_data.description,
                "is_partner": False,
                "partnership_tier": None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert company into database
            result = self.supabase.table("companies").insert(company_dict).execute()
            
            if not result.data:
                raise ValidationException("Failed to create company")
            
            company_data_dict = result.data[0]
            return Company(**company_data_dict)
            
        except Exception as e:
            logger.error(f"Error creating company: {e}")
            raise ValidationException(f"Failed to create company: {str(e)}")

    async def get_companies(self) -> List[Company]:
        """Get all companies"""
        try:
            result = self.supabase.table("companies").select("*").order("created_at", desc=True).execute()
            
            companies = []
            if result.data:
                for company_data in result.data:
                    companies.append(Company(**company_data))
            
            return companies
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return []

    async def create_partnership(self, company_id: int, partnership_data: PartnershipCreate) -> CompanyPartnership:
        """Create a partnership for a company"""
        try:
            # Create partnership data
            partnership_dict = {
                "company_id": company_id,
                "partnership_type": partnership_data.partnership_type,
                "cost": float(partnership_data.cost) if partnership_data.cost else None,
                "duration_months": partnership_data.duration_months,
                "banner_url": partnership_data.banner_url,
                "banner_position": partnership_data.banner_position,
                "is_active": True,
                "start_date": datetime.utcnow().isoformat(),
                "end_date": None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert partnership into database
            result = self.supabase.table("company_partnerships").insert(partnership_dict).execute()
            
            if not result.data:
                raise ValidationException("Failed to create partnership")
            
            partnership_data_dict = result.data[0]
            return CompanyPartnership(**partnership_data_dict)
            
        except Exception as e:
            logger.error(f"Error creating partnership: {e}")
            raise ValidationException(f"Failed to create partnership: {str(e)}")
