import httpx

from app.services.connectors.base import BaseJobConnector, JobSearchQuery
from app.services.connectors.relevance import relevance_score, search_terms_from_keywords


class RemotiveConnector(BaseJobConnector):
    access_method = "public_api"
    base_url = "https://remotive.com/api/remote-jobs"

    async def search(self, query: JobSearchQuery) -> list[dict]:
        params = {"search": " ".join(query.keywords)}
        search_terms = search_terms_from_keywords(query.keywords)
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()

        jobs = []
        for item in payload.get("jobs", []):
            title = item.get("title") or "Untitled role"
            description = item.get("description") or title
            relevance = relevance_score(search_terms, title, description)
            if search_terms and relevance == 0:
                continue
            jobs.append(
                {
                    "external_id": str(item.get("id") or ""),
                    "company": item.get("company_name") or "Unknown company",
                    "title": title,
                    "location": item.get("candidate_required_location") or "Remote",
                    "url": item.get("url"),
                    "raw_description": description,
                    "source_name": "Remotive",
                    "relevance": relevance,
                }
            )
        return sorted(jobs, key=lambda job: job["relevance"], reverse=True)
