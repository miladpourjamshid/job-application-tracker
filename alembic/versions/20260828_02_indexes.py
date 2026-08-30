"""Add indexes used by application queries.

Revision ID: 20260828_02
Revises: 20260828_01
"""

from alembic import op

revision = "20260828_02"
down_revision = "20260828_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_job_applications_company", "job_applications", ["company"])
    op.create_index("ix_job_applications_status", "job_applications", ["status"])
    op.create_index(
        "ix_job_applications_applied_date",
        "job_applications",
        ["applied_date"],
    )
    op.create_index("ix_job_applications_deadline", "job_applications", ["deadline"])


def downgrade() -> None:
    op.drop_index("ix_job_applications_deadline", table_name="job_applications")
    op.drop_index(
        "ix_job_applications_applied_date",
        table_name="job_applications",
    )
    op.drop_index("ix_job_applications_status", table_name="job_applications")
    op.drop_index("ix_job_applications_company", table_name="job_applications")
