from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class Milestone(BaseModel):
    id: Optional[int] = None
    campaign_id: int
    title: str
    threshold_amount: Decimal
    achieved_at: Optional[datetime] = None
    is_auto: bool = True
    created_at: Optional[datetime] = None

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v.strip()

    @validator('threshold_amount')
    def validate_threshold_amount(cls, v):
        if v <= 0:
            raise ValueError('Threshold amount must be greater than 0')
        return v


class MilestoneCreate(BaseModel):
    campaign_id: int
    title: str
    threshold_amount: Decimal
    is_auto: bool = True

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v.strip()

    @validator('threshold_amount')
    def validate_threshold_amount(cls, v):
        if v <= 0:
            raise ValueError('Threshold amount must be greater than 0')
        return v

    @validator('campaign_id')
    def validate_campaign_id(cls, v):
        if v <= 0:
            raise ValueError('Invalid campaign ID')
        return v


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    threshold_amount: Optional[Decimal] = None

    @validator('title')
    def validate_title(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v.strip() if v else v

    @validator('threshold_amount')
    def validate_threshold_amount(cls, v):
        if v and v <= 0:
            raise ValueError('Threshold amount must be greater than 0')
        return v


class MilestoneResponse(BaseModel):
    id: int
    campaign_id: int
    title: str
    threshold_amount: Decimal
    achieved_at: Optional[datetime]
    is_auto: bool
    created_at: datetime
    is_achieved: bool
