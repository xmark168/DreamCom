"""OpenAI LLM client implementation."""

from typing import Any, AsyncIterator

from openai import AsyncOpenAI

from core.llm.base import LLMClient, LLMMessage, LLMResponse


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        super().__init__(model, api_key)
        self.client = AsyncOpenAI(api_key=api_key)

    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Send messages and get a complete response."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content or ""
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0,
        }
        return LLMResponse(content=content, usage=usage)

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream response chunks."""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
