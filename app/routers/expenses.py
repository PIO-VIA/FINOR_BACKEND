from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.dependencies import get_current_treasurer, get_db
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseRead

from app.schemas.response import GenericResponse

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=GenericResponse[ExpenseRead], status_code=status.HTTP_201_CREATED)
async def create_expense(
    body: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    rubric = await crud.rubric.get_rubric_by_id(db, body.rubric_id)
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found."
        )
    expense = await crud.expense.create_expense(
        db,
        rubric_id=body.rubric_id,
        description=body.description,
        amount=body.amount,
        receipt_number=body.receipt_number,
        date=body.date,
        treasurer_id=current_treasurer.id,
    )
    await db.commit()
    return GenericResponse(
        message="Expense recorded successfully",
        data=ExpenseRead.model_validate(expense)
    )


@router.get("/", response_model=GenericResponse[list[ExpenseRead]])
async def list_expenses(
    rubric_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    expenses = await crud.expense.get_all_expenses(db, rubric_id=rubric_id)
    return GenericResponse(
        data=[ExpenseRead.model_validate(e) for e in expenses]
    )


@router.get("/{expense_id}", response_model=GenericResponse[ExpenseRead])
async def get_expense(
    expense_id: str,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    expense = await crud.expense.get_expense_by_id(db, expense_id)
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found."
        )
    return GenericResponse(
        data=ExpenseRead.model_validate(expense)
    )
