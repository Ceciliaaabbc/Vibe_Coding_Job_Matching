from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class JobSearchQuery:
    keywords: list[str]
    location: str | None = None
    remote: bool | None = None
    salary_min: int | None = None
    job_type: str | None = None


class BaseJobConnector(ABC):
    access_method: str

    @abstractmethod
    async def search(self, query: JobSearchQuery) -> list[dict]:
        """Return jobs from legal APIs, RSS feeds, public pages, or user-authorized sources."""

