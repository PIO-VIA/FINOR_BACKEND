"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-29

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("INVESTOR", "TREASURER", name="roleenum"),
            nullable=False,
        ),
        sa.Column("access_code", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("access_code"),
    )
    op.create_index("ix_users_access_code", "users", ["access_code"], unique=True)

    op.create_table(
        "rubrics",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("initial_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "investments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("investor_id", sa.String(length=36), nullable=False),
        sa.Column("rubric_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("bank_receipt_code", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "VALIDATED", "REJECTED", name="investmentstatusenum"),
            nullable=False,
        ),
        sa.Column("validation_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["rubric_id"], ["rubrics.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bank_receipt_code"),
    )
    op.create_index(
        "ix_investments_bank_receipt_code",
        "investments",
        ["bank_receipt_code"],
        unique=True,
    )

    op.create_table(
        "expenses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("rubric_id", sa.String(length=36), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("receipt_number", sa.String(length=100), nullable=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("treasurer_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["rubric_id"], ["rubrics.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["treasurer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "transfers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_rubric_id", sa.String(length=36), nullable=False),
        sa.Column("destination_rubric_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("is_repaid", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["destination_rubric_id"], ["rubrics.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["source_rubric_id"], ["rubrics.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transfers")
    op.drop_table("expenses")
    op.drop_index("ix_investments_bank_receipt_code", table_name="investments")
    op.drop_table("investments")
    op.drop_table("rubrics")
    op.drop_index("ix_users_access_code", table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS investmentstatusenum")
    op.execute("DROP TYPE IF EXISTS roleenum")
