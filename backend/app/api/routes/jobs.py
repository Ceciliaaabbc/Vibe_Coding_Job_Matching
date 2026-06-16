from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Application, ApplicationMaterial, Job, JobSource, MatchScore, Resume
from app.models.enums import ApplicationStatus, MaterialType
from app.schemas.job import JobDiscoverRequest, JobImportRequest, JobRead
from app.services.agents.material_agent import MaterialAgent
from app.services.agents.matching_agent import MatchingAgent
from app.services.connectors.arbeitnow import ArbeitnowConnector
from app.services.connectors.base import JobSearchQuery
from app.services.connectors.remotive import RemotiveConnector
from app.services.connectors.remoteok import RemoteOKConnector
from app.services.connectors.the_muse import TheMuseConnector
from app.services.parsers.jd_parser import JDParser
from app.services.vector_store.vector_service import VectorStoreService

router = APIRouter()


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.created_at.desc())).all())


@router.post("/discover", response_model=list[JobRead])
async def discover_jobs(payload: JobDiscoverRequest, db: Session = Depends(get_db)) -> list[Job]:
    keywords = [part for part in payload.keywords.split() if part]
    query = JobSearchQuery(keywords=keywords, location=payload.location)

    connectors = [RemotiveConnector(), ArbeitnowConnector(), RemoteOKConnector(), TheMuseConnector()]
    discovered: list[dict] = []
    errors: list[str] = []
    for connector in connectors:
        try:
            discovered.extend(await connector.search(query))
        except Exception as exc:
            errors.append(f"{connector.__class__.__name__}: {exc}")

    if not discovered and errors:
        raise HTTPException(
            status_code=502,
            detail="Public job sources are unavailable. No demo or fake jobs were loaded.",
        )

    discovered = _dedupe_discovered_jobs(discovered)
    discovered = sorted(discovered, key=lambda item: item.get("relevance", 0), reverse=True)

    jobs: list[Job] = []
    for item in discovered[: payload.limit]:
        source = _get_or_create_source(db, item.get("source_name") or "Unknown Public Source")
        job = await _upsert_discovered_job(db, source, item)
        jobs.append(job)
    db.commit()
    return jobs


@router.post("/import-text", response_model=JobRead)
async def import_job(payload: JobImportRequest, db: Session = Depends(get_db)) -> Job:
    existing = None
    if payload.url:
        existing = db.scalar(select(Job).where(Job.url == str(payload.url)))
    if existing:
        return existing

    job = Job(
        company=payload.company,
        title=payload.title,
        location=payload.location,
        url=str(payload.url) if payload.url else None,
        raw_description=payload.raw_description,
    )
    job.parsed_jd_json = JDParser().parse(payload.raw_description)
    db.add(job)
    db.commit()
    db.refresh(job)
    chunks = VectorStoreService.chunk_text(payload.raw_description)
    try:
        await VectorStoreService().upsert_texts(
            "job_descriptions",
            chunks,
            [f"{job.id}:{index}" for index, _ in enumerate(chunks)],
            [{"job_id": job.id, "company": job.company, "title": job.title, "chunk_index": index} for index, _ in enumerate(chunks)],
        )
    except Exception:
        job.parsed_jd_json = {**job.parsed_jd_json, "vector_index_warning": "ChromaDB indexing failed; job was saved."}
        db.commit()
        db.refresh(job)
    return job


@router.post("/{job_id}/match/{resume_id}")
async def match_job(job_id: str, resume_id: str, db: Session = Depends(get_db)) -> dict:
    job = db.get(Job, job_id)
    resume = db.get(Resume, resume_id)
    if not job or not resume:
        raise HTTPException(status_code=404, detail="Job or resume not found.")

    rag_context: list[str] = []
    semantic_score = None
    try:
        vector_result = await VectorStoreService().query("resume_chunks", job.raw_description, n_results=4)
        rag_context = vector_result.documents
        if vector_result.distances:
            best_distance = min(vector_result.distances)
            semantic_score = max(0, min(100, round(100 / (1 + best_distance))))
    except Exception:
        rag_context = []

    result = MatchingAgent().score(resume, job, semantic_score=semantic_score, rag_context=rag_context)
    match_score = MatchScore(
        resume_id=resume.id,
        job_id=job.id,
        score=result["score"],
        keyword_score=result["keyword_score"],
        semantic_score=result["semantic_score"],
        requirement_score=result["requirement_score"],
        matched_skills_json={"items": result["matched_skills"]},
        missing_skills_json={"items": result["missing_skills"]},
        reasons_json={"items": result["reasons"]},
        recommendation=result["recommendation"],
    )
    db.add(match_score)
    db.flush()

    status = ApplicationStatus.PENDING_CONFIRMATION.value if result["score"] >= 70 else ApplicationStatus.SCORED.value
    application = db.scalar(select(Application).where(Application.job_id == job.id, Application.resume_id == resume.id))
    if application is None:
        application = Application(
            resume_id=resume.id,
            job_id=job.id,
            match_score_id=match_score.id,
            status=status,
        )
    else:
        application.match_score_id = match_score.id
        application.status = status
    db.add(application)

    cover_letter = await MaterialAgent().draft_cover_letter(resume, job, result)
    material = db.scalar(
        select(ApplicationMaterial).where(
            ApplicationMaterial.job_id == job.id,
            ApplicationMaterial.resume_id == resume.id,
            ApplicationMaterial.material_type == MaterialType.COVER_LETTER.value,
        )
    )
    if material is None:
        material = ApplicationMaterial(
            job_id=job.id,
            resume_id=resume.id,
            material_type=MaterialType.COVER_LETTER.value,
            content=cover_letter,
        )
    else:
        material.content = cover_letter
    db.add(material)
    db.flush()
    application.cover_letter_id = material.id
    application.application_note = MaterialAgent().draft_application_note(job, result)
    db.commit()
    return {
        "match": result,
        "application_id": application.id,
        "cover_letter_id": material.id,
        "rag_context": rag_context,
    }


def _get_or_create_source(db: Session, name: str) -> JobSource:
    source = db.scalar(select(JobSource).where(JobSource.name == name))
    if source:
        return source
    source = JobSource(name=name, source_type="job_board", access_method="public_api", base_url=None)
    db.add(source)
    db.flush()
    return source


def _dedupe_discovered_jobs(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped = []
    for item in items:
        key = item.get("url") or f"{item.get('source_name')}:{item.get('external_id')}"
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


async def _upsert_discovered_job(db: Session, source: JobSource, item: dict) -> Job:
    external_id = item.get("external_id")
    url = item.get("url")
    statement = select(Job).where(Job.source_id == source.id, Job.external_id == external_id)
    job = db.scalar(statement)
    if job is None and url:
        job = db.scalar(select(Job).where(Job.url == url))

    raw_description = item.get("raw_description") or "No description provided."
    if job is None:
        job = Job(
            source_id=source.id,
            external_id=external_id,
            company=item.get("company") or "Unknown company",
            title=item.get("title") or "Untitled role",
            location=item.get("location"),
            url=url,
            raw_description=raw_description,
            parsed_jd_json=JDParser().parse(raw_description),
        )
        db.add(job)
        db.flush()
        await _index_job_description(job)
    return job


async def _index_job_description(job: Job) -> None:
    chunks = VectorStoreService.chunk_text(job.raw_description)
    try:
        await VectorStoreService().upsert_texts(
            "job_descriptions",
            chunks,
            [f"{job.id}:{index}" for index, _ in enumerate(chunks)],
            [{"job_id": job.id, "company": job.company, "title": job.title, "chunk_index": index} for index, _ in enumerate(chunks)],
        )
    except Exception:
        return
