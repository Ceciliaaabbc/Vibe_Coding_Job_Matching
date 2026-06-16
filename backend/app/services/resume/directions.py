from dataclasses import dataclass


@dataclass(frozen=True)
class CareerDirection:
    id: str
    name: str
    headline: str
    core_skills: list[str]
    keywords: list[str]
    project_name: str
    project_pitch: str


CAREER_DIRECTIONS: list[CareerDirection] = [
    CareerDirection(
        id="ai-ml",
        name="AI / ML Engineer",
        headline="AI engineer focused on LLM applications, RAG systems, evaluation, and production ML workflows.",
        core_skills=["Python", "FastAPI", "LLM", "RAG", "embeddings", "vector databases", "PyTorch", "evaluation"],
        keywords=["LLM", "RAG", "agent", "embedding", "ChromaDB", "OpenAI", "Qwen", "DeepSeek", "model evaluation"],
        project_name="ai-rag-job-matcher",
        project_pitch="A production-style RAG system that ranks job descriptions against a candidate profile and explains match gaps.",
    ),
    CareerDirection(
        id="full-stack",
        name="Full Stack Engineer",
        headline="Full stack engineer building end-to-end product workflows with React, APIs, databases, and deployment.",
        core_skills=["React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "Docker", "REST APIs", "UI state"],
        keywords=["React", "TypeScript", "FastAPI", "PostgreSQL", "Docker", "authentication", "dashboard", "CRUD"],
        project_name="fullstack-application-tracker",
        project_pitch="A full-stack dashboard for tracking applications, statuses, analytics, and editable application materials.",
    ),
    CareerDirection(
        id="backend",
        name="Backend Engineer",
        headline="Backend engineer focused on API design, data modeling, background workflows, and reliable service boundaries.",
        core_skills=["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Alembic", "Redis", "Docker", "API design"],
        keywords=["REST", "database schema", "migration", "queue", "observability", "tests", "service layer"],
        project_name="backend-job-ingestion-pipeline",
        project_pitch="A backend pipeline that ingests jobs from public APIs, deduplicates records, and exposes searchable APIs.",
    ),
    CareerDirection(
        id="infra-devops",
        name="Infrastructure / DevOps Engineer",
        headline="Infrastructure engineer focused on containers, CI/CD, service reliability, and deployment automation.",
        core_skills=["Docker", "PostgreSQL", "CI/CD", "Linux", "observability", "cloud deployment", "Terraform", "Kubernetes"],
        keywords=["containerization", "deployment", "monitoring", "health checks", "automation", "infra as code"],
        project_name="deployable-agent-platform",
        project_pitch="A Dockerized agent platform with health checks, environment management, migrations, and deployment scripts.",
    ),
    CareerDirection(
        id="frontend",
        name="Frontend Engineer",
        headline="Frontend engineer focused on polished product UI, interaction flows, state management, and API integration.",
        core_skills=["React", "TypeScript", "CSS", "accessibility", "responsive UI", "forms", "dashboard UX", "API integration"],
        keywords=["React", "TypeScript", "component design", "forms", "responsive layout", "accessibility", "UX"],
        project_name="resume-job-workbench-ui",
        project_pitch="A responsive React workbench for browsing jobs, editing generated materials, and confirming applications.",
    ),
    CareerDirection(
        id="data",
        name="Data Engineer / Analytics Engineer",
        headline="Data engineer focused on ingestion, transformation, data quality, analytics models, and reliable reporting.",
        core_skills=["Python", "SQL", "PostgreSQL", "ETL", "data modeling", "analytics", "dbt", "Airflow"],
        keywords=["ETL", "data pipeline", "SQL", "analytics", "dashboard", "data quality", "warehouse"],
        project_name="job-market-analytics-pipeline",
        project_pitch="A data pipeline that normalizes job data, extracts skill trends, and reports market demand by role.",
    ),
    CareerDirection(
        id="security",
        name="Security Engineer",
        headline="Security-minded engineer focused on secure application design, auth flows, privacy, and risk-aware automation.",
        core_skills=["application security", "OAuth", "secrets management", "threat modeling", "Python", "logging", "policy"],
        keywords=["security", "auth", "privacy", "risk controls", "rate limits", "audit log", "threat model"],
        project_name="safe-automation-policy-gateway",
        project_pitch="A policy gateway that prevents unsafe automation, logs sensitive actions, and enforces confirmation flows.",
    ),
    CareerDirection(
        id="mobile",
        name="Mobile Engineer",
        headline="Mobile-oriented engineer focused on app UX, API-backed workflows, and cross-platform product delivery.",
        core_skills=["React Native", "TypeScript", "mobile UX", "API integration", "offline state", "push notifications"],
        keywords=["React Native", "mobile app", "offline-first", "state management", "notifications", "UX"],
        project_name="mobile-job-application-companion",
        project_pitch="A mobile companion app concept for tracking applications, reminders, and interview preparation.",
    ),
]


def get_direction(direction_id: str) -> CareerDirection:
    for direction in CAREER_DIRECTIONS:
        if direction.id == direction_id:
            return direction
    raise ValueError(f"Unknown career direction: {direction_id}")
