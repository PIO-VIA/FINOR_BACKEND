"""
Seed script: creates the first Treasurer account.
Run once after `alembic upgrade head`:

    python seed.py

Reads credentials from environment variables defined in .env.
"""

import asyncio

from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.user import RoleEnum, User
from app.security import hash_password


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(
                User.access_code == settings.first_treasurer_email,
                User.role == RoleEnum.TREASURER,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Treasurer '{settings.first_treasurer_email}' already exists. Skipping.")
            return

        treasurer = User(
            name=settings.first_treasurer_name,
            role=RoleEnum.TREASURER,
            access_code=settings.first_treasurer_email,
            password_hash=hash_password(settings.first_treasurer_password),
        )
        db.add(treasurer)
        await db.commit()
        print(
            f"Treasurer created: name='{settings.first_treasurer_name}'"
            f" email='{settings.first_treasurer_email}'"
        )


if __name__ == "__main__":
    asyncio.run(main())
