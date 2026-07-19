from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.entities import ApplicationMaterial, User
from app.models.enums import MaterialStatus
from app.schemas.material import MaterialRead, MaterialUpdate

router = APIRouter()


@router.get("/{material_id}", response_model=MaterialRead)
def get_material(
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationMaterial:
    material = db.scalar(
        select(ApplicationMaterial).where(
            ApplicationMaterial.id == material_id, ApplicationMaterial.user_id == current_user.id
        )
    )
    if not material:
        raise HTTPException(status_code=404, detail="Material not found.")
    return material


@router.get("", response_model=list[MaterialRead])
def list_materials(
    job_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ApplicationMaterial]:
    statement = (
        select(ApplicationMaterial)
        .where(ApplicationMaterial.user_id == current_user.id)
        .order_by(ApplicationMaterial.created_at.desc())
    )
    if job_id:
        statement = statement.where(ApplicationMaterial.job_id == job_id)
    return list(db.scalars(statement).all())


@router.put("/{material_id}", response_model=MaterialRead)
def update_material(
    material_id: str,
    payload: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationMaterial:
    material = db.scalar(
        select(ApplicationMaterial).where(
            ApplicationMaterial.id == material_id, ApplicationMaterial.user_id == current_user.id
        )
    )
    if not material:
        raise HTTPException(status_code=404, detail="Material not found.")
    material.content = payload.content
    material.version += 1
    material.status = MaterialStatus.EDITED.value
    db.commit()
    db.refresh(material)
    return material
