from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class Shoutout(BaseModel):
    id: Optional[int] = None
    campaign_id: int
    donor_id: Optional[int] = None
    display_name: Optional[str] = None
    message: Optional[str] = None
    visible: bool = True
    created_at: Optional[datetime] = None

    @validator('message')
    def validate_message(cls, v):
        if v and len(v.strip()) > 512:
            raise ValueError('Message cannot exceed 512 characters')
        return v.strip() if v else v

    @validator('display_name')
    def validate_display_name(cls, v):
        if v and len(v.strip()) > 191:
            raise ValueError('Display name cannot exceed 191 characters')
        return v.strip() if v else v


class ShoutoutCreate(BaseModel):
    campaign_id: int
    donor_id: Optional[int] = None
    display_name: Optional[str] = None
    message: Optional[str] = None

    @validator('message')
    def validate_message(cls, v):
        if v and len(v.strip()) > 512:
            raise ValueError('Message cannot exceed 512 characters')
        return v.strip() if v else v

    @validator('display_name')
    def validate_display_name(cls, v):
        if v and len(v.strip()) > 191:
            raise ValueError('Display name cannot exceed 191 characters')
        return v.strip() if v else v

    @validator('campaign_id')
    def validate_campaign_id(cls, v):
        if v <= 0:
            raise ValueError('Invalid campaign ID')
        return v


class ShoutoutUpdate(BaseModel):
    display_name: Optional[str] = None
    message: Optional[str] = None
    visible: Optional[bool] = None

    @validator('message')
    def validate_message(cls, v):
        if v and len(v.strip()) > 512:
            raise ValueError('Message cannot exceed 512 characters')
        return v.strip() if v else v

    @validator('display_name')
    def validate_display_name(cls, v):
        if v and len(v.strip()) > 191:
            raise ValueError('Display name cannot exceed 191 characters')
        return v.strip() if v else v


class ShoutoutResponse(BaseModel):
    id: int
    campaign_id: int
    donor_id: Optional[int]
    display_name: Optional[str]
    message: Optional[str]
    visible: bool
    created_at: datetime
