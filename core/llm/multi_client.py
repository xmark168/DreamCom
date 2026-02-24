"""Multi-provider LLM client with auto-switch capability."""

import asyncio
import time
from typing import AsyncIterator, Optional

from .base import LLMClient, LLMMessage, LLMResponse
from .provider_manager import ProviderManager
from .provider_types import ProviderConfig, ProviderType
from .providers.anthropic_client import AnthropicClient
from .providers.openai_client import OpenAIClient


class MultiClientError(Exception):
    """Error when all providers fail."""

    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        super().__init__(f"All providers failed: {errors}")


class MultiClient:
    """LLM client that tries multiple providers with auto-switch."""

    def __init__(self, provider_manager: Optional[ProviderManager] = None):
        self.provider_manager = provider_manager or ProviderManager()
        self._current_provider_idx = 0

    def _create_client(self, provider: ProviderConfig) -> LLMClient:
        """Create an LLM client for a provider."""
        if provider.type == ProviderType.ANTHROPIC:
            return AnthropicClient(
                model=provider.default_model,
                api_key=provider.api_key,
            )
        else:  # openai or openai-compatible
            return OpenAIClient(
                model=provider.default_model,
                api_key=provider.api_key,
                base_url=provider.base_url,
            )

    async def _try_provider(
        self,
        provider: ProviderConfig,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: Optional[int],
    ) -> LLMResponse:
        """Try to get completion from a single provider."""
        client = self._create_client(provider)
        return await client.complete(messages, temperature, max_tokens)

    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        specific_provider: Optional[str] = None,
    ) -> LLMResponse:
        """
        Get completion, trying providers in order until one succeeds.

        Args:
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            specific_provider: If set, only use this provider

        Returns:
            LLMResponse from the first successful provider

        Raises:
            MultiClientError: If all providers fail
        """
        settings = self.provider_manager.get_settings()

        if specific_provider:
            providers = [self.provider_manager.get_provider(specific_provider)]
            providers = [p for p in providers if p]
        else:
            providers = self.provider_manager.get_enabled_providers()

        if not providers:
            raise MultiClientError({"all": "No providers available"})

        errors: dict[str, str] = {}

        for provider in providers:
            for attempt in range(settings.max_retries):
                try:
                    print(f"  🔄 Trying {provider.name} (attempt {attempt + 1}/{settings.max_retries})...")
                    response = await self._try_provider(
                        provider, messages, temperature, max_tokens
                    )
                    print(f"  ✅ Success with {provider.name}")
                    return response
                except Exception as e:
                    error_msg = str(e)
                    errors[provider.name] = error_msg
                    print(f"  ❌ {provider.name} failed: {error_msg[:100]}")

                    if attempt < settings.max_retries - 1:
                        wait_time = settings.retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"  ⏳ Retrying in {wait_time:.1f}s...")
                        await asyncio.sleep(wait_time)

            if not settings.auto_switch:
                break

        # All providers failed
        raise MultiClientError(errors)

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        specific_provider: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Stream response, trying providers in order until one succeeds.

        Note: If the first provider fails mid-stream, we cannot switch.
        This method tries to start streaming with each provider.
        """
        settings = self.provider_manager.get_settings()

        if specific_provider:
            providers = [self.provider_manager.get_provider(specific_provider)]
            providers = [p for p in providers if p]
        else:
            providers = self.provider_manager.get_enabled_providers()

        if not providers:
            raise MultiClientError({"all": "No providers available"})

        errors: dict[str, str] = {}

        for provider in providers:
            try:
                client = self._create_client(provider)
                async for chunk in client.stream(messages, temperature, max_tokens):
                    yield chunk
                return
            except Exception as e:
                errors[provider.name] = str(e)
                if not settings.auto_switch:
                    break

        raise MultiClientError(errors)

    def get_available_providers(self) -> list[ProviderConfig]:
        """Get list of available (enabled) providers."""
        return self.provider_manager.get_enabled_providers()

    async def test_provider(self, provider_id: str) -> tuple[bool, str]:
        """
        Test a specific provider.

        Returns:
            (success, message)
        """
        provider = self.provider_manager.get_provider(provider_id)
        if not provider:
            return False, f"Provider {provider_id} not found"

        if not provider.enabled:
            return False, f"Provider {provider_id} is disabled"

        try:
            messages = [
                LLMMessage("system", "You are a helpful assistant."),
                LLMMessage("user", "Say 'Test successful' and nothing else."),
            ]
            response = await self._try_provider(provider, messages, 0.7, None)
            if "Test successful" in response.content:
                return True, f"Provider {provider.name} is working"
            else:
                return True, f"Provider {provider.name} responded (unexpected content)"
        except Exception as e:
            return False, f"Provider {provider.name} failed: {str(e)[:100]}"

    async def test_all_providers(self) -> dict[str, tuple[bool, str]]:
        """Test all enabled providers."""
        results = {}
        providers = self.provider_manager.list_providers()

        for provider in providers:
            success, message = await self.test_provider(provider.id)
            results[provider.id] = (success, message)

        return results
