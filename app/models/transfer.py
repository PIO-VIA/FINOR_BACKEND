import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    source_rubric_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rubrics.id", ondelete="RESTRICT"), nullable=False
    )
    destination_rubric_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rubrics.id", ondelete="RESTRICT"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    is_repaid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
