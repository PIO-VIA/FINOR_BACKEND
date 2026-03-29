import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User))
        users = res.scalars().all()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"ID: {u.id}, Name: {u.name}, AccessCode: {u.access_code}, Role: {u.role}")

if __name__ == "__main__":
    asyncio.run(main())
