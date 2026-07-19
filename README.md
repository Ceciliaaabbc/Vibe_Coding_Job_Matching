# Job Application Agent

An AI-assisted job application workflow for finding roles, parsing job descriptions, matching them against a resume, generating application materials, and managing user-confirmed applications.

The system is designed around compliance guardrails:

- No captcha bypassing.
- No login risk-control bypassing.
- No unconfirmed bulk applications.
- Every job must enter a pending confirmation state before application.
- Restricted job sites are handled with external links and semi-automatic user workflows only.
- Data sources should be official APIs, RSS feeds, public pages, or user-authorized imports.

## Stack

- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL
- Frontend: React, Vite, TypeScript
- Vector store: ChromaDB
- Resume parsing: PyMuPDF, python-docx
- LLM providers: OpenAI, DeepSeek, Qwen-compatible APIs
- Deployment: Docker Compose

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- ChromaDB: http://localhost:8001

The backend container runs:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Database schema changes should be added as Alembic revisions under `backend/alembic/versions`.

## Automated verification

The GitHub Actions CI pipeline verifies database migrations, backend unit/API integration tests, the TypeScript production build, and a complete Playwright browser workflow.

Backend tests require a dedicated PostgreSQL database:

```bash
cd backend
export TEST_DATABASE_URL=postgresql+psycopg://job_agent:job_agent@localhost:5432/job_agent_test
export DATABASE_URL="$TEST_DATABASE_URL"
export VECTOR_STORE_ENABLED=false
pytest -q
```

The browser test covers resume upload, manual job import, matching, generated-material review, user confirmation, and the final applied state. After installing both backend and frontend dependencies and applying migrations, run:

```bash
cd frontend
npx playwright install chromium
DATABASE_URL=postgresql+psycopg://job_agent:job_agent@localhost:5432/job_agent_e2e \
VECTOR_STORE_ENABLED=false \
CORS_ORIGINS='["http://127.0.0.1:5173"]' \
npm run test:e2e
```

Setting `VECTOR_STORE_ENABLED=false` makes CI deterministic and offline. Normal Docker Compose development keeps ChromaDB enabled.

## Current Scope

This is the initial project scaffold. It includes:

- FastAPI app structure
- PostgreSQL models
- Resume upload API
- Manual job import API
- JD parsing service boundary
- Matching service boundary
- Application confirmation guardrails
- React dashboard and workflow screens
- Docker deployment files
