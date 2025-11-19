from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class CampaignDuration(str, Enum):
    ONE_MONTH = "1"
    THREE_MONTHS = "3"
    SIX_MONTHS = "6"
    TWELVE_MONTHS = "12"


class Campaign(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: str
    description: str
    goal_amount: Decimal
    current_amount: Decimal = Decimal('0.00')
    status: CampaignStatus = CampaignStatus.DRAFT
    duration_months: CampaignDuration
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    story: Optional[str] = None
    is_featured: bool = False
    referral_requirement_met: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters long')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 20:
            raise ValueError('Description must be at least 20 characters long')
        return v.strip()

    @validator('goal_amount')
    def validate_goal_amount(cls, v):
        if v <= 0:
            raise ValueError('Goal amount must be greater than 0')
        if v > 100000:  # $100,000 max
            raise ValueError('Goal amount cannot exceed $100,000')
        return v


class CampaignCreate(BaseModel):
    title: str
    description: str
    goal_amount: Decimal
    duration_months: CampaignDuration
    category: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    story: Optional[str] = None

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters long')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 20:
            raise ValueError('Description must be at least 20 characters long')
        return v.strip()

    @validator('goal_amount')
    def validate_goal_amount(cls, v):
        if v <= 0:
            raise ValueError('Goal amount must be greater than 0')
        if v > 100000:
            raise ValueError('Goal amount cannot exceed $100,000')
        return v


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goal_amount: Optional[Decimal] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    story: Optional[str] = None
    status: Optional[CampaignStatus] = None

    @validator('title')
    def validate_title(cls, v):
        if v and len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters long')
        return v.strip() if v else v

    @validator('description')
    def validate_description(cls, v):
        if v and len(v.strip()) < 20:
            raise ValueError('Description must be at least 20 characters long')
        return v.strip() if v else v

    @validator('goal_amount')
    def validate_goal_amount(cls, v):
        if v and v <= 0:
            raise ValueError('Goal amount must be greater than 0')
        if v and v > 100000:
            raise ValueError('Goal amount cannot exceed $100,000')
        return v


class CampaignResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    goal_amount: Decimal
    current_amount: Decimal
    status: CampaignStatus
    duration_months: CampaignDuration
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    category: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    story: Optional[str]
    is_featured: bool
    referral_requirement_met: bool
    created_at: datetime
    updated_at: datetime
    progress_percentage: float
    days_remaining: Optional[int] = None
    donor_count: int = 0
