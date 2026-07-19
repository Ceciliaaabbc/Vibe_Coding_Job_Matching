from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Job Application Agent"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://job_agent:job_agent@localhost:5432/job_agent"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    vector_store_enabled: bool = True
    upload_dir: str = "uploads"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4.1-mini"
    default_embedding_model: str = "text-embedding-3-small"
    openai_base_url: str = "https://api.openai.com/v1"
    deepseek_base_url: str = "https://api.deepseek.com"
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ollama_base_url: str = "http://ollama:11434/v1"
    openai_api_key: str | None = None
    deepseek_api_key: str | None = None
    qwen_api_key: str | None = None
    ollama_api_key: str = "ollama"
    match_threshold: int = 70
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
