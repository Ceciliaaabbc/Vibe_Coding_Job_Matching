from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Application, Job
from app.models.enums import ApplicationStatus

router = APIRouter()


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict:
    total_jobs = db.scalar(select(func.count(Job.id))) or 0
    pending = db.scalar(
        select(func.count(Application.id)).where(Application.status == ApplicationStatus.PENDING_CONFIRMATION.value)
    ) or 0
    applied = db.scalar(select(func.count(Application.id)).where(Application.status == ApplicationStatus.APPLIED.value)) or 0
    interviewing = db.scalar(
        select(func.count(Application.id)).where(Application.status == ApplicationStatus.INTERVIEWING.value)
    ) or 0
    interview_rate = round((interviewing / applied) * 100, 2) if applied else 0
    return {
        "total_jobs": total_jobs,
        "high_match_pending": pending,
        "applied": applied,
        "interviewing": interviewing,
        "interview_rate": interview_rate,
    }

