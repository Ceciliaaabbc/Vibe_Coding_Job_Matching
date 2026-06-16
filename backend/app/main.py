from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import applications, dashboard, jobs, materials, resumes
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
    app.include_router(applications.router, prefix="/applications", tags=["applications"])
    app.include_router(materials.router, prefix="/materials", tags=["materials"])
    app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
