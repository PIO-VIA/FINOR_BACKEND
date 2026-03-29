from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.dependencies import get_current_treasurer, get_db
from app.models.user import User
from app.schemas.rubric import RubricBalance, RubricCreate, RubricRead, RubricUpdate

router = APIRouter(prefix="/rubrics", tags=["Rubrics"])


@router.post("/", response_model=RubricRead, status_code=status.HTTP_201_CREATED)
async def create_rubric(
    body: RubricCreate,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    existing = await crud.rubric.get_rubric_by_name(db, body.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A rubric named '{body.name}' already exists.",
        )
    rubric = await crud.rubric.create_rubric(
        db, body.name, body.description, body.initial_balance
    )
    await db.commit()
    return RubricRead.model_validate(rubric)


@router.get("/", response_model=list[RubricRead])
async def list_rubrics(db: AsyncSession = Depends(get_db)):
    rubrics = await crud.rubric.get_all_rubrics(db)
    return [RubricRead.model_validate(r) for r in rubrics]


@router.get("/{rubric_id}", response_model=RubricRead)
async def get_rubric(rubric_id: str, db: AsyncSession = Depends(get_db)):
    rubric = await crud.rubric.get_rubric_by_id(db, rubric_id)
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found."
        )
    return RubricRead.model_validate(rubric)


@router.patch("/{rubric_id}", response_model=RubricRead)
async def update_rubric(
    rubric_id: str,
    body: RubricUpdate,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    rubric = await crud.rubric.get_rubric_by_id(db, rubric_id)
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found."
        )
    rubric = await crud.rubric.update_rubric(db, rubric, body.name, body.description)
    await db.commit()
    return RubricRead.model_validate(rubric)


@router.get("/{rubric_id}/balance", response_model=RubricBalance)
async def get_rubric_balance(rubric_id: str, db: AsyncSession = Depends(get_db)):
    rubric = await crud.rubric.get_rubric_by_id(db, rubric_id)
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found."
        )
    total_invested = await crud.investment.get_total_validated_for_rubric(db, rubric_id)
    total_expenses = await crud.expense.get_total_expenses_for_rubric(db, rubric_id)
    total_out = await crud.transfer.get_total_transferred_out(db, rubric_id)
    total_in = await crud.transfer.get_total_transferred_in(db, rubric_id)
    current_balance = (
        float(rubric.initial_balance) + total_invested - total_expenses - total_out + total_in
    )
    return RubricBalance(
        rubric_id=rubric.id,
        rubric_name=rubric.name,
        initial_balance=float(rubric.initial_balance),
        total_invested=total_invested,
        total_expenses=total_expenses,
        total_transferred_out=total_out,
        total_transferred_in=total_in,
        current_balance=current_balance,
    )


@router.delete("/{rubric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rubric(
    rubric_id: str,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    rubric = await crud.rubric.get_rubric_by_id(db, rubric_id)
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found."
        )
    await crud.rubric.delete_rubric(db, rubric)
    await db.commit()
