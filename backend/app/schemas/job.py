from pydantic import BaseModel, Field, HttpUrl


class JobImportRequest(BaseModel):
    company: str
    title: str
    location: str | None = None
    url: HttpUrl | None = None
    raw_description: str = Field(min_length=20)


class JobDiscoverRequest(BaseModel):
    keywords: str = "AI Engineer"
    location: str | None = None
    limit: int = Field(default=50, ge=1, le=200)


class JobRead(BaseModel):
    id: str
    company: str
    title: str
    location: str | None
    url: str | None
    raw_description: str
    parsed_jd_json: dict

    model_config = {"from_attributes": True}


class MatchRead(BaseModel):
    id: str
    score: int
    keyword_score: int
    semantic_score: int
    requirement_score: int
    matched_skills_json: dict
    missing_skills_json: dict
    reasons_json: dict
    recommendation: str

    model_config = {"from_attributes": True}
