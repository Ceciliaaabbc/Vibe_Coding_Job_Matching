import httpx

from app.services.connectors.base import BaseJobConnector, JobSearchQuery
from app.services.connectors.relevance import relevance_score, search_terms_from_keywords


class TheMuseConnector(BaseJobConnector):
    access_method = "public_api"
    base_url = "https://www.themuse.com/api/public/jobs"

    async def search(self, query: JobSearchQuery) -> list[dict]:
        search_terms = search_terms_from_keywords(query.keywords)
        jobs = []
        async with httpx.AsyncClient(timeout=20) as client:
            for page in range(1, 4):
                response = await client.get(self.base_url, params={"page": page})
                response.raise_for_status()
                payload = response.json()
                for item in payload.get("results", []):
                    title = item.get("name") or "Untitled role"
                    description = item.get("contents") or title
                    company = (item.get("company") or {}).get("name") or "Unknown company"
                    locations = ", ".join(location.get("name", "") for location in item.get("locations", []))
                    categories = " ".join(category.get("name", "") for category in item.get("categories", []))
                    levels = " ".join(level.get("name", "") for level in item.get("levels", []))
                    relevance = relevance_score(search_terms, title, description, company, categories, levels)
                    if search_terms and relevance == 0:
                        continue
                    refs = item.get("refs") or {}
                    jobs.append(
                        {
                            "external_id": str(item.get("id") or refs.get("landing_page") or ""),
                            "company": company,
                            "title": title,
                            "location": locations or None,
                            "url": refs.get("landing_page"),
                            "raw_description": description,
                            "source_name": "The Muse",
                            "relevance": relevance,
                        }
                    )
        return sorted(jobs, key=lambda job: job["relevance"], reverse=True)
