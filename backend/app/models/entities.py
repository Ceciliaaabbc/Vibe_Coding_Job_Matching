from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ApplicationStatus, MaterialStatus, MaterialType


def now() -> datetime:
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(32))
    file_path: Mapped[str] = mapped_column(String(1024))
    raw_text: Mapped[str] = mapped_column(Text)
    parsed_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    resume_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("resumes.id"))
    name: Mapped[str | None] = mapped_column(String(255))
    headline: Mapped[str | None] = mapped_column(String(500))
    skills_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    experience_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    education_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    projects_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    keywords_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    target_roles_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class JobSource(Base):
    __tablename__ = "job_sources"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), unique=True)
    source_type: Mapped[str] = mapped_column(String(80))
    base_url: Mapped[str | None] = mapped_column(String(1024))
    access_method: Mapped[str] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_jobs_source_external"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("job_sources.id"), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    remote_type: Mapped[str | None] = mapped_column(String(80))
    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    salary_text: Mapped[str | None] = mapped_column(String(255))
    job_type: Mapped[str | None] = mapped_column(String(80))
    url: Mapped[str | None] = mapped_column(String(2048), index=True)
    raw_description: Mapped[str] = mapped_column(Text)
    parsed_jd_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    applications: Mapped[list["Application"]] = relationship(back_populates="job")


class MatchScore(Base):
    __tablename__ = "match_scores"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    resume_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("resumes.id"))
    job_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("jobs.id"))
    score: Mapped[int] = mapped_column(Integer)
    keyword_score: Mapped[int] = mapped_column(Integer)
    semantic_score: Mapped[int] = mapped_column(Integer)
    requirement_score: Mapped[int] = mapped_column(Integer)
    matched_skills_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    missing_skills_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    reasons_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    recommendation: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_applications_user_job"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    resume_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("resumes.id"), nullable=True)
    job_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("jobs.id"))
    match_score_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("match_scores.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(80), default=ApplicationStatus.DISCOVERED.value)
    cover_letter_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    application_note: Mapped[str | None] = mapped_column(Text)
    confirmed_by_user: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime)
    interview_at: Mapped[datetime | None] = mapped_column(DateTime)
    offer_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    job: Mapped[Job] = relationship(back_populates="applications")


class ApplicationMaterial(Base):
    __tablename__ = "application_materials"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    job_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("jobs.id"))
    resume_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("resumes.id"), nullable=True)
    material_type: Mapped[str] = mapped_column(String(80), default=MaterialType.COVER_LETTER.value)
    content: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(80), default=MaterialStatus.DRAFT.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    application_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("applications.id"))
    event_type: Mapped[str] = mapped_column(String(80))
    event_payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

