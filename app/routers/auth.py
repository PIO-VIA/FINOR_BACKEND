from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.dependencies import get_db, get_current_treasurer
from app.schemas.auth import (
    InvestorLoginRequest,
    InvestorLoginResponse,
    TokenResponse,
    TreasurerLoginRequest,
)
from app.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.schemas.response import GenericResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/treasurer/login", response_model=GenericResponse[TokenResponse])
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
    return GenericResponse(
        message="Login successful",
        data=TokenResponse(access_token=token)
    )


@router.post("/investor/login", response_model=GenericResponse[InvestorLoginResponse])
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
    return GenericResponse(
        message="Login successful",
        data=InvestorLoginResponse.model_validate(user)
    )


@router.patch("/me", response_model=GenericResponse[UserRead])
async def update_my_profile(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_treasurer),
):
    user = await crud.user.update_user(
        db, current_user, body.name, body.email, body.password
    )
    await db.commit()
    return GenericResponse(
        message="Profile updated successfully",
        data=UserRead.model_validate(user)
    )
