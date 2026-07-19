from dataclasses import dataclass

from app.core.config import settings
from app.services.llm.provider_factory import get_embedding_provider
from app.services.vector_store.chroma_client import get_chroma_client


@dataclass
class VectorSearchResult:
    documents: list[str]
    metadatas: list[dict]
    distances: list[float]


class VectorStoreService:
    def __init__(self) -> None:
        self.embedding_provider = get_embedding_provider()

    async def upsert_texts(self, collection_name: str, texts: list[str], ids: list[str], metadatas: list[dict]) -> None:
        if not settings.vector_store_enabled or not texts:
            return
        embeddings = [await self.embedding_provider.embedding(text) for text in texts]
        client = get_chroma_client()
        collection = client.get_or_create_collection(collection_name)
        collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    async def query(self, collection_name: str, query_text: str, n_results: int = 5) -> VectorSearchResult:
        if not settings.vector_store_enabled:
            raise RuntimeError("Vector store is disabled.")
        embedding = await self.embedding_provider.embedding(query_text)
        client = get_chroma_client()
        collection = client.get_or_create_collection(collection_name)
        result = collection.query(query_embeddings=[embedding], n_results=n_results)
        return VectorSearchResult(
            documents=(result.get("documents") or [[]])[0],
            metadatas=(result.get("metadatas") or [[]])[0],
            distances=(result.get("distances") or [[]])[0],
        )

    @staticmethod
    def chunk_text(text: str, max_chars: int = 1200) -> list[str]:
        paragraphs = [part.strip() for part in text.splitlines() if part.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            if len(current) + len(paragraph) + 1 > max_chars and current:
                chunks.append(current)
                current = paragraph
            else:
                current = f"{current}\n{paragraph}".strip()
        if current:
            chunks.append(current)
        return chunks or [text[:max_chars]]
