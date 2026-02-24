"""Factory for creating LLM clients."""

import os

from .base import LLMClient
from .providers.anthropic_client import AnthropicClient
from .providers.openai_client import OpenAIClient


class LLMClientFactory:
    """Factory to create appropriate LLM client based on provider."""

    @staticmethod
    def create(
        provider: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> LLMClient:
        """Create an LLM client for the specified provider."""
        provider = provider.lower()

        if provider == "openai":
            model = model or "gpt-4o"
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")
            return OpenAIClient(model=model, api_key=api_key)

        elif provider == "anthropic":
            model = model or "claude-3-5-sonnet-20241022"
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var.")
            return AnthropicClient(model=model, api_key=api_key)

        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: openai, anthropic")
