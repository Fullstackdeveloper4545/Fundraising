"""
Internal User model for database operations
This model includes all fields that exist in the database
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"
    COMPANY = "company"
    DONOR = "donor"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserInternal(BaseModel):
    """Internal user model with all database fields"""
    id: Optional[int] = None
    email: EmailStr
    password_hash: Optional[str] = None
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    status: UserStatus = UserStatus.ACTIVE
    is_verified: bool = False
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None
    referral_count: int = 0
    verification_token: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

    @validator('phone')
    def validate_phone(cls, v):
        if v and len(v.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')) < 10:
            raise ValueError('Invalid phone number format')
        return v

    def to_public_user(self):
        """Convert to public user model (without sensitive data)"""
        from app.models.user import User
        return User(
            id=self.id,
            email=self.email,
            password_hash=None,  # Never expose password hash
            first_name=self.first_name,
            last_name=self.last_name,
            phone=self.phone,
            role=self.role,
            status=self.status,
            is_verified=self.is_verified,
            referral_code=self.referral_code,
            referred_by=self.referred_by,
            referral_count=self.referral_count,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
