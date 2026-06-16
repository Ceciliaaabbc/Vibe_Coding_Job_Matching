# ai-rag-job-matcher

A production-style RAG system that ranks job descriptions against a candidate profile and explains match gaps.

## Why this project exists
This project is designed to strengthen a resume for **AI / ML Engineer** roles.

## Core features
- Demonstrates Python
- Demonstrates FastAPI
- Demonstrates LLM
- Demonstrates RAG
- Demonstrates embeddings
- Demonstrates vector databases

## Run locally
From the main `AgentProject` folder:

```bash
cd backend/generated_projects/ai-rag-job-matcher
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8010
```

Then open:

- API: http://localhost:8010
- Docs: http://localhost:8010/docs
