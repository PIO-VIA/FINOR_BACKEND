from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transfer import Transfer


async def get_transfer_by_id(db: AsyncSession, transfer_id: str) -> Transfer | None:
    result = await db.execute(select(Transfer).where(Transfer.id == transfer_id))
    return result.scalar_one_or_none()


async def get_all_transfers(db: AsyncSession) -> list[Transfer]:
    result = await db.execute(select(Transfer).order_by(Transfer.date.desc()))
    return list(result.scalars().all())


async def create_transfer(
    db: AsyncSession,
    source_rubric_id: str,
    destination_rubric_id: str,
    amount: float,
    reason: str,
    date,
) -> Transfer:
    transfer = Transfer(
        source_rubric_id=source_rubric_id,
        destination_rubric_id=destination_rubric_id,
        amount=amount,
        reason=reason,
        date=date,
    )
    db.add(transfer)
    await db.flush()
    await db.refresh(transfer)
    return transfer


async def mark_transfer_repaid(db: AsyncSession, transfer: Transfer) -> Transfer:
    transfer.is_repaid = True
    await db.flush()
    await db.refresh(transfer)
    return transfer


async def get_total_transferred_out(db: AsyncSession, rubric_id: str) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Transfer.amount), 0)).where(
            Transfer.source_rubric_id == rubric_id
        )
    )
    return float(result.scalar())


async def get_total_transferred_in(db: AsyncSession, rubric_id: str) -> float:
    result = await db.execute(
        select(func.coalesce(func.sum(Transfer.amount), 0)).where(
            Transfer.destination_rubric_id == rubric_id
        )
    )
    return float(result.scalar())
