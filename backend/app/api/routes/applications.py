from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.entities import Application, ApplicationMaterial, Job, MatchScore, User
from app.models.enums import ApplicationStatus
from app.schemas.application import ApplicationDetail, ApplicationRead
from app.services.agents.application_control_agent import ApplicationControlAgent

router = APIRouter()


@router.get("/pending", response_model=list[ApplicationRead])
def pending_applications(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Application]:
    return list(
        db.scalars(
            select(Application)
            .where(
                Application.status == ApplicationStatus.PENDING_CONFIRMATION.value,
                Application.user_id == current_user.id,
            )
            .order_by(Application.created_at.desc())
        ).all()
    )


@router.get("/{application_id}", response_model=ApplicationDetail)
def get_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    application = db.scalar(
        select(Application).where(Application.id == application_id, Application.user_id == current_user.id)
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    job = db.scalar(select(Job).where(Job.id == application.job_id, Job.user_id == current_user.id))
    match = (
        db.scalar(
            select(MatchScore).where(MatchScore.id == application.match_score_id, MatchScore.user_id == current_user.id)
        )
        if application.match_score_id
        else None
    )
    materials = list(
        db.scalars(
            select(ApplicationMaterial)
            .where(
                ApplicationMaterial.job_id == application.job_id,
                ApplicationMaterial.user_id == current_user.id,
            )
            .order_by(ApplicationMaterial.created_at.desc())
        ).all()
    )
    return {"application": application, "job": job, "match": match, "materials": materials}


@router.post("/{application_id}/confirm", response_model=ApplicationRead)
def confirm_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Application:
    application = db.scalar(
        select(Application).where(Application.id == application_id, Application.user_id == current_user.id)
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    return ApplicationControlAgent().confirm(db, application)


@router.post("/{application_id}/skip", response_model=ApplicationRead)
def skip_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Application:
    application = db.scalar(
        select(Application).where(Application.id == application_id, Application.user_id == current_user.id)
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    return ApplicationControlAgent().skip(db, application)
