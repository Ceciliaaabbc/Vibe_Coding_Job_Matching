from app.services.connectors.base import BaseJobConnector, JobSearchQuery


class ManualJDConnector(BaseJobConnector):
    access_method = "manual_import"

    async def search(self, query: JobSearchQuery) -> list[dict]:
        return []

