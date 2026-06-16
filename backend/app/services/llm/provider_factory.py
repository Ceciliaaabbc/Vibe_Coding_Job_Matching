from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.local_provider import LocalFallbackProvider
from app.services.llm.openai_compatible import OpenAICompatibleProvider


def get_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    provider = (provider_name or settings.default_llm_provider).lower()

    if provider == "openai" and settings.openai_api_key:
        return OpenAICompatibleProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            chat_model=settings.default_llm_model,
            embedding_model=settings.default_embedding_model,
            supports_embeddings=True,
        )

    if provider == "deepseek" and settings.deepseek_api_key:
        return OpenAICompatibleProvider(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            chat_model=settings.default_llm_model,
            embedding_model=None,
            supports_embeddings=False,
        )

    if provider == "qwen" and settings.qwen_api_key:
        return OpenAICompatibleProvider(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
            chat_model=settings.default_llm_model,
            embedding_model=settings.default_embedding_model,
            supports_embeddings=True,
        )

    if provider == "ollama":
        return OpenAICompatibleProvider(
            api_key=settings.ollama_api_key,
            base_url=settings.ollama_base_url,
            chat_model=settings.default_llm_model,
            embedding_model=None,
            supports_embeddings=False,
        )

    return LocalFallbackProvider()


def get_embedding_provider() -> BaseLLMProvider:
    if settings.openai_api_key:
        return get_llm_provider("openai")
    if settings.qwen_api_key:
        return get_llm_provider("qwen")
    return LocalFallbackProvider()
