from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.dependencies import get_current_treasurer, get_db
from app.models.user import User
from app.schemas.transfer import TransferCreate, TransferRead

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("/", response_model=TransferRead, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    body: TransferCreate,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    if body.source_rubric_id == body.destination_rubric_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Source and destination rubrics must be different.",
        )
    source = await crud.rubric.get_rubric_by_id(db, body.source_rubric_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source rubric not found."
        )
    destination = await crud.rubric.get_rubric_by_id(db, body.destination_rubric_id)
    if destination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination rubric not found.",
        )
    transfer = await crud.transfer.create_transfer(
        db,
        source_rubric_id=body.source_rubric_id,
        destination_rubric_id=body.destination_rubric_id,
        amount=body.amount,
        reason=body.reason,
        date=body.date,
    )
    await db.commit()
    return TransferRead.model_validate(transfer)


@router.get("/", response_model=list[TransferRead])
async def list_transfers(
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    transfers = await crud.transfer.get_all_transfers(db)
    return [TransferRead.model_validate(t) for t in transfers]


@router.get("/{transfer_id}", response_model=TransferRead)
async def get_transfer(
    transfer_id: str,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    transfer = await crud.transfer.get_transfer_by_id(db, transfer_id)
    if transfer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found."
        )
    return TransferRead.model_validate(transfer)


@router.patch("/{transfer_id}/repaid", response_model=TransferRead)
async def mark_transfer_repaid(
    transfer_id: str,
    db: AsyncSession = Depends(get_db),
    current_treasurer: User = Depends(get_current_treasurer),
):
    transfer = await crud.transfer.get_transfer_by_id(db, transfer_id)
    if transfer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found."
        )
    if transfer.is_repaid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This transfer is already marked as repaid.",
        )
    transfer = await crud.transfer.mark_transfer_repaid(db, transfer)
    await db.commit()
    return TransferRead.model_validate(transfer)
