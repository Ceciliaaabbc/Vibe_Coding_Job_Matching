from pydantic import BaseModel


class ResumeRead(BaseModel):
    id: str
    file_name: str
    file_type: str
    raw_text: str | None = None
    parsed_json: dict

    model_config = {"from_attributes": True}


class CareerDirectionRead(BaseModel):
    id: str
    name: str
    headline: str
    core_skills: list[str]
    keywords: list[str]


class ResumeOptimizeRequest(BaseModel):
    resume_id: str
    direction_id: str
    job_description: str | None = None
    use_llm: bool = True


class ResumeOptimizeResponse(BaseModel):
    direction: dict
    resume_markdown: str
    missing_skills: list[str]
    emphasized_keywords: list[str]
    project_needed: bool
    recommended_project: dict
    notes: list[str]


class ProjectCreateRequest(BaseModel):
    direction_id: str


class ProjectCreateResponse(BaseModel):
    project_name: str
    project_path: str
    files: list[str]
    github_pitch: str
