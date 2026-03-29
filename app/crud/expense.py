from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense


async def get_expense_by_id(db: AsyncSession, expense_id: str) -> Expense | None:
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    return result.scalar_one_or_none()


async def get_all_expenses(
    db: AsyncSession, rubric_id: str | None = None
) -> list[Expense]:
    query = select(Expense).order_by(Expense.date.desc())
    if rubric_id is not None:
        query = query.where(Expense.rubric_id == rubric_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_expense(
    db: AsyncSession,
    rubric_id: str,
    description: str,
    amount: float,
    receipt_number: str | None,
    date,
    treasurer_id: str,
) -> Expense:
    expense = Expense(
        rubric_id=rubric_id,
        description=description,
        amount=amount,
        receipt_number=receipt_number,
        date=date,
        treasurer_id=treasurer_id,
    )
    db.add(expense)
    await db.flush()
    await db.refresh(expense)
    return expense


async def get_total_expenses_for_rubric(db: AsyncSession, rubric_id: str) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.rubric_id == rubric_id
        )
    )
    return float(result.scalar())


async def get_global_total_spent(db: AsyncSession) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0))
    )
    return float(result.scalar())
