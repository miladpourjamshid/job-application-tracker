"""Add companies, contacts, interviews, and application history.

Revision ID: 20260828_03
Revises: 20260828_02
"""

import sqlalchemy as sa

from alembic import op

revision = "20260828_03"
down_revision = "20260828_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("industry", sa.String(length=160), nullable=True),
        sa.UniqueConstraint("name", name="uq_companies_name"),
    )
    op.create_index("ix_companies_name", "companies", ["name"])

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("role", sa.String(length=160), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["company_id"], ["companies.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_contacts_company_id", "contacts", ["company_id"])

    with op.batch_alter_table("job_applications") as batch_op:
        batch_op.add_column(sa.Column("company_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_job_applications_company_id", ["company_id"])
        batch_op.create_foreign_key(
            "fk_job_applications_company_id",
            "companies",
            ["company_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_table(
        "application_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["application_id"], ["job_applications.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_application_history_application_id",
        "application_history",
        ["application_id"],
    )

    op.create_table(
        "interviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=True),
        sa.Column("interview_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"], ["job_applications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"], ["contacts.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_interviews_application_id", "interviews", ["application_id"]
    )
    op.create_index("ix_interviews_contact_id", "interviews", ["contact_id"])


def downgrade() -> None:
    op.drop_index("ix_interviews_contact_id", table_name="interviews")
    op.drop_index("ix_interviews_application_id", table_name="interviews")
    op.drop_table("interviews")

    op.drop_index(
        "ix_application_history_application_id",
        table_name="application_history",
    )
    op.drop_table("application_history")

    with op.batch_alter_table("job_applications") as batch_op:
        batch_op.drop_constraint(
            "fk_job_applications_company_id", type_="foreignkey"
        )
        batch_op.drop_index("ix_job_applications_company_id")
        batch_op.drop_column("company_id")

    op.drop_index("ix_contacts_company_id", table_name="contacts")
    op.drop_table("contacts")

    op.drop_index("ix_companies_name", table_name="companies")
    op.drop_table("companies")
