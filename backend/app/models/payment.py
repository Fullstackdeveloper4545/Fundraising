from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from decimal import Decimal


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    SQUARE = "square"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Payment(BaseModel):
    id: Optional[int] = None
    campaign_id: int
    donor_id: Optional[int] = None
    donor_email: str
    donor_name: Optional[str] = None
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    is_anonymous: bool = False
    message: Optional[str] = None
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 10000:  # $10,000 max per donation
            raise ValueError('Amount cannot exceed $10,000 per donation')
        return v

    @validator('donor_email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Valid email is required')
        return v.lower()


class PaymentCreate(BaseModel):
    campaign_id: int
    donor_email: str
    donor_name: Optional[str] = None
    amount: Decimal
    method: PaymentMethod
    is_anonymous: bool = False
    message: Optional[str] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 10000:
            raise ValueError('Amount cannot exceed $10,000 per donation')
        return v

    @validator('donor_email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Valid email is required')
        return v.lower()


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None


class PaymentResponse(BaseModel):
    id: int
    campaign_id: int
    donor_email: str
    donor_name: Optional[str]
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus
    transaction_id: Optional[str]
    is_anonymous: bool
    message: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]


class PayoutRequest(BaseModel):
    campaign_id: int
    method: PaymentMethod
    destination: Dict[str, Any]  # Payment destination details
    amount: Decimal

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v


class PayoutResponse(BaseModel):
    id: int
    campaign_id: int
    method: PaymentMethod
    destination: Dict[str, Any]
    amount: Decimal
    status: PaymentStatus
    created_at: datetime
    processed_at: Optional[datetime]
