import json

from openai import AsyncOpenAI

from app.services.llm.base import BaseLLMProvider, LLMMessage


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        chat_model: str,
        embedding_model: str | None = None,
        supports_embeddings: bool = True,
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.supports_embeddings = supports_embeddings

    async def chat(self, messages: list[LLMMessage], temperature: float = 0.2) -> str:
        response = await self.client.chat.completions.create(
            model=self.chat_model,
            messages=[{"role": item.role, "content": item.content} for item in messages],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    async def structured_output(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        response = await self.client.chat.completions.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"{user_prompt}\n\nReturn only JSON matching this schema description:\n"
                        f"{json.dumps(schema, ensure_ascii=False)}"
                    ),
                },
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    async def embedding(self, text: str) -> list[float]:
        if not self.supports_embeddings or not self.embedding_model:
            raise RuntimeError("This provider is not configured for embeddings.")
        response = await self.client.embeddings.create(model=self.embedding_model, input=text)
        return response.data[0].embedding

