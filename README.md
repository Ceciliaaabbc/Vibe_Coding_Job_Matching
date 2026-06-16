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
