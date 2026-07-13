"""Add predictions table.

Revision ID: 0001
Revises:
Create Date: 2026-07-13
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("area", sa.Float(), nullable=False),
        sa.Column("bedrooms", sa.Integer(), nullable=False),
        sa.Column("bathrooms", sa.Integer(), nullable=False),
        sa.Column("stories", sa.Integer(), nullable=False),
        sa.Column("parking", sa.Integer(), nullable=False),
        sa.Column("has_pool", sa.String(length=5), nullable=False),
        sa.Column("has_garage", sa.String(length=5), nullable=False),
        sa.Column("has_ac", sa.String(length=5), nullable=False),
        sa.Column("predicted_price", sa.Float(), nullable=False),
        sa.Column("confidence_low", sa.Float(), nullable=False),
        sa.Column("confidence_high", sa.Float(), nullable=False),
        sa.Column("model_used", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_predictions_id"), "predictions", ["id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_predictions_id"), table_name="predictions")
    op.drop_table("predictions")
