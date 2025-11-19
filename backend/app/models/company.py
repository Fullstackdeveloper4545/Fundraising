from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class Company(BaseModel):
    id: Optional[int] = None
    name: str
    contact_email: Optional[EmailStr] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    is_partner: bool = False
    partnership_tier: Optional[str] = None
    created_at: Optional[datetime] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Company name must be at least 2 characters long')
        return v.strip()

    @validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v

    @validator('logo_url')
    def validate_logo_url(cls, v):
        if v and len(v) > 1024:
            raise ValueError('Logo URL cannot exceed 1024 characters')
        return v


class CompanyCreate(BaseModel):
    name: str
    contact_email: Optional[EmailStr] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Company name must be at least 2 characters long')
        return v.strip()

    @validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v

    @validator('logo_url')
    def validate_logo_url(cls, v):
        if v and len(v) > 1024:
            raise ValueError('Logo URL cannot exceed 1024 characters')
        return v


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    is_partner: Optional[bool] = None
    partnership_tier: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Company name must be at least 2 characters long')
        return v.strip() if v else v

    @validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v

    @validator('logo_url')
    def validate_logo_url(cls, v):
        if v and len(v) > 1024:
            raise ValueError('Logo URL cannot exceed 1024 characters')
        return v


class CompanyPartnership(BaseModel):
    id: Optional[int] = None
    company_id: int
    partnership_type: str  # 'banner_ad', 'grant_provider', 'sponsor'
    cost: Optional[Decimal] = None
    duration_months: Optional[int] = None
    banner_url: Optional[str] = None
    banner_position: Optional[str] = None
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @validator('partnership_type')
    def validate_partnership_type(cls, v):
        allowed_types = ['banner_ad', 'grant_provider', 'sponsor']
        if v not in allowed_types:
            raise ValueError(f'Partnership type must be one of: {", ".join(allowed_types)}')
        return v

    @validator('cost')
    def validate_cost(cls, v):
        if v and v < 0:
            raise ValueError('Cost cannot be negative')
        return v

    @validator('duration_months')
    def validate_duration_months(cls, v):
        if v and v <= 0:
            raise ValueError('Duration must be positive')
        return v


class PartnershipCreate(BaseModel):
    company_id: int
    partnership_type: str
    cost: Optional[Decimal] = None
    duration_months: Optional[int] = None
    banner_url: Optional[str] = None
    banner_position: Optional[str] = None

    @validator('partnership_type')
    def validate_partnership_type(cls, v):
        allowed_types = ['banner_ad', 'grant_provider', 'sponsor']
        if v not in allowed_types:
            raise ValueError(f'Partnership type must be one of: {", ".join(allowed_types)}')
        return v

    @validator('cost')
    def validate_cost(cls, v):
        if v and v < 0:
            raise ValueError('Cost cannot be negative')
        return v

    @validator('duration_months')
    def validate_duration_months(cls, v):
        if v and v <= 0:
            raise ValueError('Duration must be positive')
        return v


class Grant(BaseModel):
    id: Optional[int] = None
    company_id: int
    title: str
    description: str
    amount: Decimal
    requirements: Optional[str] = None
    application_deadline: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Grant title must be at least 5 characters long')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 20:
            raise ValueError('Grant description must be at least 20 characters long')
        return v.strip()

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Grant amount must be greater than 0')
        return v


class CompanyResponse(BaseModel):
    id: int
    name: str
    contact_email: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    description: Optional[str]
    is_partner: bool
    partnership_tier: Optional[str]
    created_at: datetime
    partnerships: Optional[List[CompanyPartnership]] = None
    grants: Optional[List[Grant]] = None
