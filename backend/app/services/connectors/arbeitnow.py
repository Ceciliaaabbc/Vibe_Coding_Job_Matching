import httpx

from app.services.connectors.base import BaseJobConnector, JobSearchQuery
from app.services.connectors.relevance import relevance_score, search_terms_from_keywords


class ArbeitnowConnector(BaseJobConnector):
    access_method = "public_api"
    base_url = "https://www.arbeitnow.com/api/job-board-api"

    async def search(self, query: JobSearchQuery) -> list[dict]:
        search_terms = search_terms_from_keywords(query.keywords)
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self.base_url)
            response.raise_for_status()
            payload = response.json()

        jobs = []
        for item in payload.get("data", []):
            title = item.get("title") or "Untitled role"
            description = item.get("description") or title
            company = item.get("company_name") or "Unknown company"
            tags = " ".join(item.get("tags") or [])
            relevance = relevance_score(search_terms, title, description, company, tags)
            if search_terms and relevance == 0:
                continue
            jobs.append(
                {
                    "external_id": str(item.get("slug") or item.get("url") or ""),
                    "company": company,
                    "title": title,
                    "location": item.get("location") or ("Remote" if item.get("remote") else None),
                    "url": item.get("url"),
                    "raw_description": description,
                    "source_name": "Arbeitnow",
                    "relevance": relevance,
                }
            )
        return sorted(jobs, key=lambda job: job["relevance"], reverse=True)
