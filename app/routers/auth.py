from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.dependencies import get_db
from app.schemas.auth import (
    InvestorLoginRequest,
    InvestorLoginResponse,
    TokenResponse,
    TreasurerLoginRequest,
)
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/treasurer/login", response_model=TokenResponse)
async def treasurer_login(
    body: TreasurerLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await crud.user.get_treasurer_by_email(db, body.email)
    if user is None or not verify_password(body.password, user.password_hash or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(access_token=token)


@router.post("/investor/login", response_model=InvestorLoginResponse)
async def investor_login(
    body: InvestorLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await crud.user.get_user_by_access_code(db, body.access_code)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal code not found.",
        )
    return InvestorLoginResponse.model_validate(user)
