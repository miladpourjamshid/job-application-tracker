"""Add required user ownership to job applications.

Revision ID: 20260829_05
Revises: 20260829_04
"""

import sqlalchemy as sa

from alembic import op

revision = "20260829_05"
down_revision = "20260829_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("job_applications", sa.Column("user_id", sa.Integer(), nullable=True))

    bind = op.get_bind()
    users = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("email", sa.String()),
        sa.column("password_hash", sa.String()),
        sa.column("is_active", sa.Boolean()),
    )
    applications = sa.table(
        "job_applications",
        sa.column("id", sa.Integer()),
        sa.column("user_id", sa.Integer()),
    )

    legacy_user = bind.execute(
        sa.select(users.c.id).where(users.c.email == "legacy@local.invalid")
    ).scalar_one_or_none()
    if legacy_user is None:
        bind.execute(
            users.insert().values(
                email="legacy@local.invalid",
                password_hash="disabled",
                is_active=False,
            )
        )
        legacy_user = bind.execute(
            sa.select(users.c.id).where(users.c.email == "legacy@local.invalid")
        ).scalar_one()

    bind.execute(
        applications.update()
        .where(applications.c.user_id.is_(None))
        .values(user_id=legacy_user)
    )

    with op.batch_alter_table("job_applications") as batch_op:
        batch_op.create_foreign_key(
            "fk_job_applications_user_id",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_index("ix_job_applications_user_id", ["user_id"])
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("job_applications") as batch_op:
        batch_op.drop_constraint("fk_job_applications_user_id", type_="foreignkey")
        batch_op.drop_index("ix_job_applications_user_id")
        batch_op.drop_column("user_id")
