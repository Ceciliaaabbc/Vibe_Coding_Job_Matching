from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.entities import Application, ApplicationEvent
from app.models.enums import ApplicationStatus


class ApplicationControlAgent:
    def confirm(self, db: Session, application: Application) -> Application:
        if application.status == ApplicationStatus.APPLIED.value:
            raise HTTPException(status_code=409, detail="This job has already been marked as applied.")
        if application.status != ApplicationStatus.PENDING_CONFIRMATION.value:
            raise HTTPException(status_code=400, detail="Only pending applications can be confirmed.")

        now = datetime.utcnow()
        application.status = ApplicationStatus.APPLIED.value
        application.confirmed_by_user = True
        application.confirmed_at = now
        application.applied_at = now
        db.add(
            ApplicationEvent(
                application_id=application.id,
                event_type="user_confirmed",
                event_payload_json={"status": application.status},
            )
        )
        db.commit()
        db.refresh(application)
        return application

    def skip(self, db: Session, application: Application) -> Application:
        application.status = ApplicationStatus.SKIPPED.value
        db.add(
            ApplicationEvent(
                application_id=application.id,
                event_type="user_skipped",
                event_payload_json={"status": application.status},
            )
        )
        db.commit()
        db.refresh(application)
        return application

