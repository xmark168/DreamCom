"""Anthropic LLM client implementation."""

from typing import Any, AsyncIterator

from anthropic import AsyncAnthropic

from core.llm.base import LLMClient, LLMMessage, LLMResponse


class AnthropicClient(LLMClient):
    """Anthropic API client."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str | None = None):
        super().__init__(model, api_key)
        self.client = AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Send messages and get a complete response."""
        # Separate system message from other messages
        system_message = ""
        other_messages = []
        for m in messages:
            if m.role == "system":
                system_message = m.content
            else:
                other_messages.append(m.to_dict())

        response = await self.client.messages.create(
            model=self.model,
            system=system_message if system_message else None,
            messages=other_messages,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
        )
        content = response.content[0].text if response.content else ""
        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        }
        return LLMResponse(content=content, usage=usage)

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream response chunks."""
        system_message = ""
        other_messages = []
        for m in messages:
            if m.role == "system":
                system_message = m.content
            else:
                other_messages.append(m.to_dict())

        stream = await self.client.messages.create(
            model=self.model,
            system=system_message if system_message else None,
            messages=other_messages,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            stream=True,
        )
        async for event in stream:
            if event.type == "content_block_delta":
                if event.delta.text:
                    yield event.delta.text
