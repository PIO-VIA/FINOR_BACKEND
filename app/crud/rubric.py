from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rubric import Rubric


async def get_rubric_by_id(db: AsyncSession, rubric_id: str) -> Rubric | None:
    result = await db.execute(select(Rubric).where(Rubric.id == rubric_id))
    return result.scalar_one_or_none()


async def get_rubric_by_name(db: AsyncSession, name: str) -> Rubric | None:
    result = await db.execute(select(Rubric).where(Rubric.name == name))
    return result.scalar_one_or_none()


async def get_all_rubrics(db: AsyncSession) -> list[Rubric]:
    result = await db.execute(select(Rubric).order_by(Rubric.created_at))
    return list(result.scalars().all())


async def create_rubric(
    db: AsyncSession,
    name: str,
    description: str | None,
    initial_balance: float,
) -> Rubric:
    rubric = Rubric(name=name, description=description, initial_balance=initial_balance)
    db.add(rubric)
    await db.flush()
    await db.refresh(rubric)
    return rubric


async def update_rubric(
    db: AsyncSession,
    rubric: Rubric,
    name: str | None,
    description: str | None,
) -> Rubric:
    if name is not None:
        rubric.name = name
    if description is not None:
        rubric.description = description
    await db.flush()
    await db.refresh(rubric)
    return rubric


async def delete_rubric(db: AsyncSession, rubric: Rubric) -> None:
    await db.delete(rubric)
    await db.flush()
