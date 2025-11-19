from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime


class Receipt(BaseModel):
    id: Optional[int] = None
    payment_id: int
    receipt_uuid: str
    generated_at: Optional[datetime] = None
    receipt_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    @validator('receipt_uuid')
    def validate_receipt_uuid(cls, v):
        if not v or len(v) != 36:
            raise ValueError('Invalid receipt UUID format')
        return v

    @validator('receipt_url')
    def validate_receipt_url(cls, v):
        if v and len(v) > 1024:
            raise ValueError('Receipt URL cannot exceed 1024 characters')
        return v


class ReceiptCreate(BaseModel):
    payment_id: int
    data: Optional[Dict[str, Any]] = None

    @validator('payment_id')
    def validate_payment_id(cls, v):
        if v <= 0:
            raise ValueError('Invalid payment ID')
        return v


class ReceiptUpdate(BaseModel):
    receipt_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    @validator('receipt_url')
    def validate_receipt_url(cls, v):
        if v and len(v) > 1024:
            raise ValueError('Receipt URL cannot exceed 1024 characters')
        return v


class ReceiptResponse(BaseModel):
    id: int
    payment_id: int
    receipt_uuid: str
    generated_at: datetime
    receipt_url: Optional[str]
    data: Optional[Dict[str, Any]]
