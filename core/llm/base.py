"""Base LLM client interface for multi-provider support."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class LLMMessage:
    """Represents a message in the conversation."""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class LLMResponse:
    """Standardized response from any LLM provider."""

    def __init__(self, content: str, usage: dict[str, Any] | None = None):
        self.content = content
        self.usage = usage or {}


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Send messages and get a complete response."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream response chunks."""
        pass
