from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title='ai-rag-job-matcher')

class AnalyzeRequest(BaseModel):
    text: str

@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}

@app.post('/analyze')
def analyze(payload: AnalyzeRequest) -> dict:
    keywords = ['LLM', 'RAG', 'agent', 'embedding', 'ChromaDB', 'OpenAI', 'Qwen', 'DeepSeek', 'model evaluation']
    hits = [keyword for keyword in keywords if keyword.lower() in payload.text.lower()]
    return {'matched_keywords': hits, 'score': min(100, len(hits) * 15)}
