from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class ReferralStatus(str, Enum):
    SENT = "sent"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class Referral(BaseModel):
    id: Optional[int] = None
    campaign_id: int
    invited_email: Optional[str] = None
    invited_phone: Optional[str] = None
    token: str
    status: ReferralStatus = ReferralStatus.SENT
    sent_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @validator('invited_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower() if v else v

    @validator('invited_phone')
    def validate_phone(cls, v):
        if v and len(v.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')) < 10:
            raise ValueError('Invalid phone number format')
        return v


class ReferralCreate(BaseModel):
    campaign_id: int
    invited_email: Optional[str] = None
    invited_phone: Optional[str] = None

    @validator('invited_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower() if v else v

    @validator('invited_phone')
    def validate_phone(cls, v):
        if v and len(v.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')) < 10:
            raise ValueError('Invalid phone number format')
        return v

    @validator('campaign_id')
    def validate_campaign_id(cls, v):
        if v <= 0:
            raise ValueError('Invalid campaign ID')
        return v


class ReferralUpdate(BaseModel):
    status: Optional[ReferralStatus] = None


class ReferralResponse(BaseModel):
    id: int
    campaign_id: int
    invited_email: Optional[str]
    invited_phone: Optional[str]
    token: str
    status: ReferralStatus
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]
    created_at: datetime


class ReferralStats(BaseModel):
    total_sent: int
    total_accepted: int
    total_expired: int
    acceptance_rate: float
