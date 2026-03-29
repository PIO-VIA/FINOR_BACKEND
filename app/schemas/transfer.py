from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TransferCreate(BaseModel):
    source_rubric_id: str
    destination_rubric_id: str
    amount: float
    reason: str
    date: datetime


class TransferRepaid(BaseModel):
    pass


class TransferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_rubric_id: str
    destination_rubric_id: str
    amount: float
    reason: str
    is_repaid: bool
    date: datetime
    created_at: datetime
