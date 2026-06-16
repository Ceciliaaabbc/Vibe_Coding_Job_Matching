from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMMessage:
    role: str
    content: str


class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[LLMMessage], temperature: float = 0.2) -> str:
        pass

    @abstractmethod
    async def structured_output(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        pass

    @abstractmethod
    async def embedding(self, text: str) -> list[float]:
        pass
