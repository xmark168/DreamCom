"""Factory for creating LLM clients.

Deprecated: Use MultiClient instead for multi-provider support.
"""

import os
from typing import Optional

from .base import LLMClient
from .multi_client import MultiClient
from .providers.anthropic_client import AnthropicClient
from .providers.openai_client import OpenAIClient


# Load environment variables from .env file if exists
try:
    from pathlib import Path
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = value
except Exception:
    pass  # Silently fail if .env cannot be read


class LLMClientFactory:
    """Factory to create appropriate LLM client based on provider.
    
    Deprecated: Use MultiClient for multi-provider support with auto-switch.
    """

    @staticmethod
    def create(
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> LLMClient:
        """Create an LLM client for the specified provider."""
        provider = provider.lower()

        if provider == "openai":
            model = model or os.getenv("DEFAULT_MODEL", "gpt-4o")
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")
            return OpenAIClient(model=model, api_key=api_key, base_url=base_url)

        elif provider == "anthropic":
            model = model or "claude-3-5-sonnet-20241022"
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var.")
            return AnthropicClient(model=model, api_key=api_key)

        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: openai, anthropic")

    @staticmethod
    def create_multi_client() -> MultiClient:
        """Create a MultiClient with auto-switch support."""
        return MultiClient()
