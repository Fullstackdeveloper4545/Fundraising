from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
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


class User(BaseModel):
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


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    referral_code: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if v and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserProfile(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    status: UserStatus
    is_verified: bool
    referral_code: Optional[str] = None
    referral_count: int
    created_at: datetime
    total_donations: Optional[float] = None
    total_raised: Optional[float] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    is_verified: bool
    created_at: datetime
