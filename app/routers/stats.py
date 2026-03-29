from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.dependencies import get_db
from app.schemas.stats import GlobalStats

from app.schemas.response import GenericResponse

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/global", response_model=GenericResponse[GlobalStats])
async def get_global_stats(db: AsyncSession = Depends(get_db)):
    total_invested = await crud.investment.get_global_total_invested(db)
    total_spent = await crud.expense.get_global_total_spent(db)
    execution_rate = (total_spent / total_invested * 100) if total_invested > 0 else 0.0
    return GenericResponse(
        data=GlobalStats(
            total_invested=total_invested,
            total_spent=total_spent,
            execution_rate=round(execution_rate, 2),
        )
    )
