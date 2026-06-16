from pydantic import BaseModel


class MaterialUpdate(BaseModel):
    content: str


class MaterialRead(BaseModel):
    id: str
    job_id: str
    resume_id: str | None
    material_type: str
    content: str
    version: int
    status: str

    model_config = {"from_attributes": True}

