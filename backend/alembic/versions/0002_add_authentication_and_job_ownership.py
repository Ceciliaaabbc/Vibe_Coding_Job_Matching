"""add authentication and job ownership

Revision ID: 0002_auth_ownership
Revises: 0001_initial_schema
Create Date: 2026-07-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_auth_ownership"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))
    op.execute("UPDATE users SET password_hash = '!' WHERE password_hash IS NULL")
    op.alter_column("users", "password_hash", nullable=False)

    op.add_column("jobs", sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.create_foreign_key("fk_jobs_user_id", "jobs", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])

    legacy_user_id = "00000000-0000-0000-0000-000000000001"
    op.execute(
        f"""
        INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
        VALUES ('{legacy_user_id}', 'legacy-import@local.invalid', 'Legacy Import', '!', NOW(), NOW())
        ON CONFLICT (email) DO NOTHING
        """
    )
    for table in ("resumes", "candidate_profiles", "match_scores", "applications", "application_materials"):
        op.execute(f"UPDATE {table} SET user_id = '{legacy_user_id}' WHERE user_id IS NULL")
        op.alter_column(table, "user_id", nullable=False)
    op.execute(f"UPDATE jobs SET user_id = '{legacy_user_id}' WHERE user_id IS NULL")
    op.alter_column("jobs", "user_id", nullable=False)
    op.drop_constraint("uq_jobs_source_external", "jobs", type_="unique")
    op.create_unique_constraint("uq_jobs_user_source_external", "jobs", ["user_id", "source_id", "external_id"])


def downgrade() -> None:
    for table in ("resumes", "candidate_profiles", "match_scores", "applications", "application_materials"):
        op.alter_column(table, "user_id", nullable=True)
    op.drop_constraint("uq_jobs_user_source_external", "jobs", type_="unique")
    op.create_unique_constraint("uq_jobs_source_external", "jobs", ["source_id", "external_id"])
    op.drop_index("ix_jobs_user_id", table_name="jobs")
    op.drop_constraint("fk_jobs_user_id", "jobs", type_="foreignkey")
    op.drop_column("jobs", "user_id")
    op.drop_column("users", "password_hash")
