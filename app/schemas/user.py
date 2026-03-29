from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import RoleEnum


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    role: RoleEnum
    access_code: str | None
    created_at: datetime


class InvestorCreate(BaseModel):
    """Used when an investor declares an investment for the first time."""
    name: str


class TreasurerCreate(BaseModel):
    """Used by a seeding script or admin to create a treasurer account."""
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
