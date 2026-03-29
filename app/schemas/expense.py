from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    rubric_id: str
    description: str
    amount: float
    receipt_number: str | None = None
    date: datetime


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    rubric_id: str
    description: str
    amount: float
    receipt_number: str | None
    date: datetime
    treasurer_id: str
    created_at: datetime
