"""Create the initial job applications schema.

Revision ID: 20260828_01
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "20260828_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=160), nullable=False),
        sa.Column("location", sa.String(length=160), nullable=True),
        sa.Column("job_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("applied_date", sa.Date(), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("job_applications")
