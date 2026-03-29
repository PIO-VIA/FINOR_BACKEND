from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investment import Investment, InvestmentStatusEnum


async def get_investment_by_id(
    db: AsyncSession, investment_id: str
) -> Investment | None:
    result = await db.execute(
        select(Investment).where(Investment.id == investment_id)
    )
    return result.scalar_one_or_none()


async def get_investment_by_receipt_code(
    db: AsyncSession, bank_receipt_code: str
) -> Investment | None:
    result = await db.execute(
        select(Investment).where(Investment.bank_receipt_code == bank_receipt_code)
    )
    return result.scalar_one_or_none()


async def get_all_investments(
    db: AsyncSession,
    status: InvestmentStatusEnum | None = None,
) -> list[Investment]:
    query = select(Investment).order_by(Investment.created_at.desc())
    if status is not None:
        query = query.where(Investment.status == status)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_investments_by_investor(
    db: AsyncSession, investor_id: str
) -> list[Investment]:
    result = await db.execute(
        select(Investment)
        .where(Investment.investor_id == investor_id)
        .order_by(Investment.created_at.desc())
    )
    return list(result.scalars().all())


async def create_investment(
    db: AsyncSession,
    investor_id: str,
    rubric_id: str,
    amount: float,
    bank_receipt_code: str,
) -> Investment:
    investment = Investment(
        investor_id=investor_id,
        rubric_id=rubric_id,
        amount=amount,
        bank_receipt_code=bank_receipt_code,
        status=InvestmentStatusEnum.PENDING,
    )
    db.add(investment)
    await db.flush()
    await db.refresh(investment)
    return investment


async def validate_investment(db: AsyncSession, investment: Investment) -> Investment:
    investment.status = InvestmentStatusEnum.VALIDATED
    investment.validation_date = datetime.now(timezone.utc)
    investment.rejection_reason = None
    await db.flush()
    await db.refresh(investment)
    return investment


async def reject_investment(
    db: AsyncSession, investment: Investment, reason: str
) -> Investment:
    investment.status = InvestmentStatusEnum.REJECTED
    investment.rejection_reason = reason
    investment.validation_date = None
    await db.flush()
    await db.refresh(investment)
    return investment


async def get_total_validated_for_rubric(
    db: AsyncSession, rubric_id: str
) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Investment.amount), 0)).where(
            Investment.rubric_id == rubric_id,
            Investment.status == InvestmentStatusEnum.VALIDATED,
        )
    )
    return float(result.scalar())


async def get_global_total_invested(db: AsyncSession) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Investment.amount), 0)).where(
            Investment.status == InvestmentStatusEnum.VALIDATED
        )
    )
    return float(result.scalar())
