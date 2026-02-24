"""Types and models for LLM providers."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    """Types of LLM providers."""

    OPENAI = "openai"
    OPENAI_COMPATIBLE = "openai-compatible"
    ANTHROPIC = "anthropic"


class ProviderConfig(BaseModel):
    """Configuration for a single LLM provider."""

    id: str = Field(..., description="Unique identifier for the provider")
    name: str = Field(..., description="Display name")
    type: ProviderType = Field(..., description="Provider type")
    api_key: str = Field(..., description="API key")
    base_url: Optional[str] = Field(None, description="Base URL for API")
    models: list[str] = Field(default_factory=list, description="Available models")
    default_model: str = Field(..., description="Default model to use")
    priority: int = Field(1, description="Priority (lower = higher priority)")
    enabled: bool = Field(True, description="Whether this provider is enabled")


class MultiProviderSettings(BaseModel):
    """Settings for multi-provider management."""

    auto_switch: bool = Field(True, description="Auto-switch on failure")
    max_retries: int = Field(3, description="Max retries per provider")
    retry_delay: float = Field(1.0, description="Delay between retries in seconds")
    fallback_to_mock: bool = Field(True, description="Fallback to mock mode if all fail")


class ProvidersConfig(BaseModel):
    """Root configuration for all providers."""

    providers: list[ProviderConfig] = Field(default_factory=list)
    settings: MultiProviderSettings = Field(default_factory=MultiProviderSettings)

    def get_enabled_providers(self) -> list[ProviderConfig]:
        """Get all enabled providers sorted by priority."""
        return sorted(
            [p for p in self.providers if p.enabled],
            key=lambda p: p.priority
        )

    def get_provider(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get a provider by ID."""
        for p in self.providers:
            if p.id == provider_id:
                return p
        return None
