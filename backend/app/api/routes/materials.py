from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import ApplicationMaterial
from app.models.enums import MaterialStatus
from app.schemas.material import MaterialRead, MaterialUpdate

router = APIRouter()


@router.get("/{material_id}", response_model=MaterialRead)
def get_material(material_id: str, db: Session = Depends(get_db)) -> ApplicationMaterial:
    material = db.get(ApplicationMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found.")
    return material


@router.get("", response_model=list[MaterialRead])
def list_materials(job_id: str | None = None, db: Session = Depends(get_db)) -> list[ApplicationMaterial]:
    statement = select(ApplicationMaterial).order_by(ApplicationMaterial.created_at.desc())
    if job_id:
        statement = statement.where(ApplicationMaterial.job_id == job_id)
    return list(db.scalars(statement).all())


@router.put("/{material_id}", response_model=MaterialRead)
def update_material(material_id: str, payload: MaterialUpdate, db: Session = Depends(get_db)) -> ApplicationMaterial:
    material = db.get(ApplicationMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found.")
    material.content = payload.content
    material.version += 1
    material.status = MaterialStatus.EDITED.value
    db.commit()
    db.refresh(material)
    return material
