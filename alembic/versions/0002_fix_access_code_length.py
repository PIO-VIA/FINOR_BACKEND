"""fix access_code length

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-29

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter column access_code from 10 to 255
    op.alter_column(
        "users",
        "access_code",
        existing_type=sa.String(length=10),
        type_=sa.String(length=255),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "access_code",
        existing_type=sa.String(length=255),
        type_=sa.String(length=10),
        existing_nullable=True,
    )
