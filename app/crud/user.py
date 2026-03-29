from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RoleEnum, User
from app.security import hash_password


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_access_code(db: AsyncSession, access_code: str) -> User | None:
    result = await db.execute(
        select(User).where(User.access_code == access_code)
    )
    return result.scalar_one_or_none()


async def get_treasurer_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).where(User.access_code == email, User.role == RoleEnum.TREASURER)
    )
    return result.scalar_one_or_none()


async def get_all_access_codes(db: AsyncSession) -> set[str]:
    result = await db.execute(
        select(User.access_code).where(User.role == RoleEnum.INVESTOR)
    )
    return {row[0] for row in result.all() if row[0]}


async def create_investor(db: AsyncSession, name: str, access_code: str) -> User:
    investor = User(name=name, role=RoleEnum.INVESTOR, access_code=access_code)
    db.add(investor)
    await db.flush()
    await db.refresh(investor)
    return investor


async def create_treasurer(
    db: AsyncSession, name: str, email: str, password: str
) -> User:
    treasurer = User(
        name=name,
        role=RoleEnum.TREASURER,
        access_code=email,
        password_hash=hash_password(password),
    )
    db.add(treasurer)
    await db.flush()
    await db.refresh(treasurer)
    return treasurer


async def get_investors(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).where(User.role == RoleEnum.INVESTOR))
    return list(result.scalars().all())


async def update_user(
    db: AsyncSession,
    user: User,
    name: str | None = None,
    email: str | None = None,
    password: str | None = None,
) -> User:
    if name is not None:
        user.name = name
    if email is not None:
        user.access_code = email
    if password is not None:
        user.password_hash = hash_password(password)

    await db.flush()
    await db.refresh(user)
    return user
