from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.investment import InvestmentStatusEnum


class InvestmentCreate(BaseModel):
    investor_name: str
    rubric_id: str
    amount: float
    bank_receipt_code: str
    access_code: str | None = None


class InvestmentValidate(BaseModel):
    pass


class InvestmentReject(BaseModel):
    rejection_reason: str


class InvestmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    investor_id: str
    rubric_id: str
    amount: float
    bank_receipt_code: str
    status: InvestmentStatusEnum
    validation_date: datetime | None
    rejection_reason: str | None
    created_at: datetime


class InvestmentCreateResponse(BaseModel):
    investment: InvestmentRead
    access_code: str
    is_new_investor: bool
