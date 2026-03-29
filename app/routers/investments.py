from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.dependencies import get_current_treasurer, get_db
from app.models.investment import InvestmentStatusEnum
from app.models.user import RoleEnum, User
from app.schemas.investment import (
    InvestmentCreate,
    InvestmentCreateResponse,
    InvestmentRead,
    InvestmentReject,
)
from app.security import generate_investor_code

from app.schemas.response import GenericResponse

router = APIRouter(prefix="/investments", tags=["Investments"])


@router.post(
    "/", response_model=GenericResponse[InvestmentCreateResponse], status_code=status.HTTP_201_CREATED
)
async def declare_investment(
    body: InvestmentCreate,
    db: AsyncSession = Depends(get_db),
):
    existing_receipt = await crud.investment.get_investment_by_receipt_code(
        db, body.bank_receipt_code
    )
    if existing_receipt:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This bank receipt code has already been declared.",
        )

    rubric = await crud.rubric.get_rubric_by_id(db, body.rubric_id)
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found."
        )

    is_new_investor = False
    if body.access_code:
        # Returning investor: find by access_code
        investor = await crud.user.get_user_by_access_code(db, body.access_code)
        if investor is None or investor.role != RoleEnum.INVESTOR:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investor code not found.",
            )
    else:
        # First-time investor: name is mandatory
        if not body.investor_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Investor name is required for the first investment.",
            )
        
        # Check if an investor with this name already exists
        investor = await crud.user.get_user_by_name(db, body.investor_name)
        if investor:
            is_new_investor = False
        else:
            is_new_investor = True
            existing_codes = await crud.user.get_all_access_codes(db)
            new_code = generate_investor_code(existing_codes)
            investor = await crud.user.create_investor(db, body.investor_name, new_code)

    investment = await crud.investment.create_investment(
        db,
        investor_id=investor.id,
        rubric_id=body.rubric_id,
        amount=body.amount,
        bank_receipt_code=body.bank_receipt_code,
    )
    await db.commit()

    message = (
        "First investment declared. Welcome! Please keep your access code."
        if is_new_investor
        else "Investment declared successfully."
    )

    return GenericResponse(
        message=message,
        data=InvestmentCreateResponse(
            investment=InvestmentRead.model_validate(investment),
            access_code=investor.access_code,
            is_new_investor=is_new_investor,
        )
    )


@router.get("/", response_model=GenericResponse[list[InvestmentRead]])
async def list_investments(
    status_filter: InvestmentStatusEnum | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    investments = await crud.investment.get_all_investments(db, status=status_filter)
    return GenericResponse(
        data=[InvestmentRead.model_validate(i) for i in investments]
    )


@router.get("/{investment_id}", response_model=GenericResponse[InvestmentRead])
async def get_investment(
    investment_id: str,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    investment = await crud.investment.get_investment_by_id(db, investment_id)
    if investment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found."
        )
    return GenericResponse(
        data=InvestmentRead.model_validate(investment)
    )


@router.patch("/{investment_id}/validate", response_model=GenericResponse[InvestmentRead])
async def validate_investment(
    investment_id: str,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    investment = await crud.investment.get_investment_by_id(db, investment_id)
    if investment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found."
        )
    if investment.status != InvestmentStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot validate an investment with status '{investment.status.value}'.",
        )
    investment = await crud.investment.validate_investment(db, investment)
    await db.commit()
    return GenericResponse(
        message="Investment validated successfully",
        data=InvestmentRead.model_validate(investment)
    )


@router.patch("/{investment_id}/reject", response_model=GenericResponse[InvestmentRead])
async def reject_investment(
    investment_id: str,
    body: InvestmentReject,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    investment = await crud.investment.get_investment_by_id(db, investment_id)
    if investment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found."
        )
    if investment.status != InvestmentStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot reject an investment with status '{investment.status.value}'.",
        )
    investment = await crud.investment.reject_investment(
        db, investment, body.rejection_reason
    )
    await db.commit()
    return GenericResponse(
        message="Investment rejected",
        data=InvestmentRead.model_validate(investment)
    )
