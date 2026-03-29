from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TreasurerLoginRequest(BaseModel):
    email: str
    password: str


class InvestorLoginRequest(BaseModel):
    access_code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class InvestorLoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    access_code: str
    created_at: datetime
