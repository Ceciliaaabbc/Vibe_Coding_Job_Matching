"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "job_sources",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(80), nullable=False),
        sa.Column("base_url", sa.String(1024), nullable=True),
        sa.Column("access_method", sa.String(80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_unique_constraint("uq_job_sources_name", "job_sources", ["name"])

    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(32), nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("parsed_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("job_sources.id"), nullable=True),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("remote_type", sa.String(80), nullable=True),
        sa.Column("salary_min", sa.Float(), nullable=True),
        sa.Column("salary_max", sa.Float(), nullable=True),
        sa.Column("salary_text", sa.String(255), nullable=True),
        sa.Column("job_type", sa.String(80), nullable=True),
        sa.Column("url", sa.String(2048), nullable=True),
        sa.Column("raw_description", sa.Text(), nullable=False),
        sa.Column("parsed_jd_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_jobs_url", "jobs", ["url"])
    op.create_unique_constraint("uq_jobs_source_external", "jobs", ["source_id", "external_id"])

    op.create_table(
        "candidate_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("resumes.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("headline", sa.String(500), nullable=True),
        sa.Column("skills_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("experience_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("education_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("projects_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("keywords_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("target_roles_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "match_scores",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("resumes.id"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("keyword_score", sa.Integer(), nullable=False),
        sa.Column("semantic_score", sa.Integer(), nullable=False),
        sa.Column("requirement_score", sa.Integer(), nullable=False),
        sa.Column("matched_skills_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("missing_skills_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reasons_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recommendation", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resume_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("resumes.id"), nullable=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("match_score_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("match_scores.id"), nullable=True),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("cover_letter_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("application_note", sa.Text(), nullable=True),
        sa.Column("confirmed_by_user", sa.Boolean(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("applied_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("interview_at", sa.DateTime(), nullable=True),
        sa.Column("offer_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_unique_constraint("uq_applications_user_job", "applications", ["user_id", "job_id"])

    op.create_table(
        "application_materials",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("resumes.id"), nullable=True),
        sa.Column("material_type", sa.String(80), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "application_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("application_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("event_payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("application_events")
    op.drop_table("application_materials")
    op.drop_constraint("uq_applications_user_job", "applications", type_="unique")
    op.drop_table("applications")
    op.drop_table("match_scores")
    op.drop_table("candidate_profiles")
    op.drop_constraint("uq_jobs_source_external", "jobs", type_="unique")
    op.drop_index("ix_jobs_url", table_name="jobs")
    op.drop_table("jobs")
    op.drop_constraint("uq_job_sources_name", "job_sources", type_="unique")
    op.drop_table("job_sources")
    op.drop_table("resumes")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

