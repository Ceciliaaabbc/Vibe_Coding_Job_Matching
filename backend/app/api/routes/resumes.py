from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.entities import Resume, User
from app.schemas.resume import (
    CareerDirectionRead,
    ProjectCreateRequest,
    ProjectCreateResponse,
    ResumeOptimizeRequest,
    ResumeOptimizeResponse,
    ResumeRead,
)
from app.services.parsers.resume_parser import ResumeParser
from app.services.resume.directions import CAREER_DIRECTIONS
from app.services.resume.optimizer import ResumeOptimizer
from app.services.vector_store.vector_service import VectorStoreService

router = APIRouter()


@router.post("/upload", response_model=ResumeRead)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resume:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix.lower()
    file_name = f"{uuid4()}{suffix}"
    file_path = upload_dir / file_name
    file_path.write_bytes(await file.read())

    raw_text = ResumeParser().parse(str(file_path))
    parsed = {
        "skills": [],
        "projects": [],
        "education": [],
        "work_experience": [],
        "keywords": [],
        "note": "Structured LLM extraction will be added in the provider implementation.",
    }
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename or file_name,
        file_type=suffix.removeprefix("."),
        file_path=str(file_path),
        raw_text=raw_text,
        parsed_json=parsed,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    chunks = VectorStoreService.chunk_text(raw_text)
    try:
        await VectorStoreService().upsert_texts(
            "resume_chunks",
            chunks,
            [f"{resume.id}:{index}" for index, _ in enumerate(chunks)],
            [
                {"resume_id": resume.id, "user_id": current_user.id, "chunk_index": index}
                for index, _ in enumerate(chunks)
            ],
        )
    except Exception:
        parsed["vector_index_warning"] = "ChromaDB indexing failed; resume upload was saved."
        resume.parsed_json = parsed
        db.commit()
        db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeRead])
def list_resumes(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Resume]:
    resumes = list(
        db.scalars(select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc())).all()
    )
    for resume in resumes:
        resume.raw_text = None
    return resumes


@router.get("/directions", response_model=list[CareerDirectionRead])
def list_career_directions() -> list[dict]:
    return [
        {
            "id": direction.id,
            "name": direction.name,
            "headline": direction.headline,
            "core_skills": direction.core_skills,
            "keywords": direction.keywords,
        }
        for direction in CAREER_DIRECTIONS
    ]


@router.post("/optimize", response_model=ResumeOptimizeResponse)
async def optimize_resume(
    payload: ResumeOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    resume = db.scalar(select(Resume).where(Resume.id == payload.resume_id, Resume.user_id == current_user.id))
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    optimizer = ResumeOptimizer()
    try:
        if payload.use_llm:
            return await optimizer.generate_with_llm(resume.raw_text, payload.direction_id, payload.job_description)
        return optimizer.generate(resume.raw_text, payload.direction_id, payload.job_description)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/projects", response_model=ProjectCreateResponse)
def create_direction_project(
    payload: ProjectCreateRequest, current_user: User = Depends(get_current_user)
) -> dict:
    try:
        return ResumeOptimizer().create_project_template(payload.direction_id, Path("/app/generated_projects"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
