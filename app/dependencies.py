from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.user import RoleEnum, User
from app.security import decode_access_token

bearer_scheme = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_treasurer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload or payload.get("role") != RoleEnum.TREASURER.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Treasurer access required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or user.role != RoleEnum.TREASURER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Treasurer account not found.",
        )

    return user


async def get_current_investor(
    access_code: str,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Used in routes where the investor authenticates by providing
    their access_code as a query parameter or in the request body.
    """
    result = await db.execute(
        select(User).where(
            User.access_code == access_code,
            User.role == RoleEnum.INVESTOR,
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor not found. Check your personal code.",
        )

    return user
