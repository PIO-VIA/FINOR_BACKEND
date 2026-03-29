from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.dependencies import get_current_investor, get_current_treasurer, get_db
from app.models.expense import Expense
from app.models.investment import Investment, InvestmentStatusEnum
from app.models.user import User
from app.schemas.investment import InvestmentRead
from app.schemas.user import UserRead, UserUpdate
from app.schemas.stats import InvestorImpactItem
from app.schemas.response import GenericResponse

router = APIRouter(prefix="/investors", tags=["Investors"])


@router.get("/", response_model=GenericResponse[list[UserRead]])
async def list_investors(
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    """Allow treasurer to see all investors with their codes."""
    investors = await crud.user.get_investors(db)
    return GenericResponse(
        data=[UserRead.model_validate(i) for i in investors]
    )


@router.get("/me/history", response_model=GenericResponse[list[InvestmentRead]])
async def get_my_history(
    access_code: str = Query(..., description="Your personal INV-XXXX code"),
    db: AsyncSession = Depends(get_db),
):
    investor: User = await get_current_investor(access_code, db)
    investments = await crud.investment.get_investments_by_investor(db, investor.id)
    return GenericResponse(
        data=[InvestmentRead.model_validate(i) for i in investments]
    )


@router.get("/me/impact", response_model=GenericResponse[list[InvestorImpactItem]])
async def get_my_impact(
    access_code: str = Query(..., description="Your personal INV-XXXX code"),
    db: AsyncSession = Depends(get_db),
):
    investor: User = await get_current_investor(access_code, db)

    investments = await crud.investment.get_investments_by_investor(db, investor.id)

    rubric_ids = list(
        {inv.rubric_id for inv in investments if inv.status == InvestmentStatusEnum.VALIDATED}
    )

    impact_items = []
    for rubric_id in rubric_ids:
        rubric = await crud.rubric.get_rubric_by_id(db, rubric_id)
        if rubric is None:
            continue

        amount_invested_result = await db.execute(
            select(func.coalesce(func.sum(Investment.amount), 0)).where(
                Investment.investor_id == investor.id,
                Investment.rubric_id == rubric_id,
                Investment.status == InvestmentStatusEnum.VALIDATED,
            )
        )
        amount_invested = float(amount_invested_result.scalar())

        total_spent_result = await db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.rubric_id == rubric_id
            )
        )
        total_spent_in_rubric = float(total_spent_result.scalar())

        impact_items.append(
            InvestorImpactItem(
                rubric_id=rubric.id,
                rubric_name=rubric.name,
                amount_invested=amount_invested,
                total_spent_in_rubric=total_spent_in_rubric,
            )
        )

    return GenericResponse(data=impact_items)


@router.patch("/me", response_model=GenericResponse[UserRead])
async def update_my_profile(
    body: UserUpdate,
    access_code: str = Query(..., description="Your personal INV-XXXX code"),
    db: AsyncSession = Depends(get_db),
):
    """Allow investor to update their personal info (except access_code)."""
    investor: User = await get_current_investor(access_code, db)
    
    # We ignore email/password for investors as they don't have them
    updated_user = await crud.user.update_user(
        db, investor, name=body.name, phone=body.phone
    )
    await db.commit()
    return GenericResponse(
        message="Profile updated successfully",
        data=UserRead.model_validate(updated_user)
    )
