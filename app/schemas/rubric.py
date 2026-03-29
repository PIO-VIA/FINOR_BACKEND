from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RubricCreate(BaseModel):
    name: str
    description: str | None = None
    initial_balance: float = 0.0


class RubricUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RubricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    initial_balance: float
    created_at: datetime


class RubricBalance(BaseModel):
    rubric_id: str
    rubric_name: str
    initial_balance: float
    total_invested: float
    total_expenses: float
    total_transferred_out: float
    total_transferred_in: float
    current_balance: float
