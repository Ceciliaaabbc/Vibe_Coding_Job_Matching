from pydantic import BaseModel

from app.schemas.job import JobRead, MatchRead
from app.schemas.material import MaterialRead


class ApplicationRead(BaseModel):
    id: str
    job_id: str
    resume_id: str | None
    match_score_id: str | None
    status: str
    confirmed_by_user: bool
    application_note: str | None

    model_config = {"from_attributes": True}


class ApplicationDetail(BaseModel):
    application: ApplicationRead
    job: JobRead
    match: MatchRead | None
    materials: list[MaterialRead]
