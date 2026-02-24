"""Manager for LLM provider configurations."""

import json
import os
from pathlib import Path
from typing import Optional

from .provider_types import ProviderConfig, ProvidersConfig


class ProviderManager:
    """Manages provider configurations from JSON file."""

    DEFAULT_CONFIG_PATH = Path.home() / ".config" / "deamcompan" / "providers.json"

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Optional[ProvidersConfig] = None
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure config directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> ProvidersConfig:
        """Load configuration from file."""
        if self._config is not None:
            return self._config

        if not self.config_path.exists():
            # Create default config
            self._config = self._create_default_config()
            self.save_config()
            return self._config

        with open(self.config_path, "r") as f:
            data = json.load(f)

        self._config = ProvidersConfig.model_validate(data)
        return self._config

    def save_config(self) -> None:
        """Save configuration to file."""
        if self._config is None:
            return

        with open(self.config_path, "w") as f:
            json.dump(self._config.model_dump(), f, indent=2)

        # Set restrictive permissions
        os.chmod(self.config_path, 0o600)

    def _create_default_config(self) -> ProvidersConfig:
        """Create default configuration with Kimi."""
        return ProvidersConfig(
            providers=[
                ProviderConfig(
                    id="kimi-proxypal",
                    name="Kimi via ProxyPal",
                    type="openai-compatible",
                    api_key="proxypal-local",
                    base_url="http://127.0.0.1:8317/v1",
                    models=["kimi-k2.5", "kimi-k2", "kimi-k2-thinking"],
                    default_model="kimi-k2.5",
                    priority=1,
                    enabled=True,
                )
            ],
            settings={
                "auto_switch": True,
                "max_retries": 3,
                "retry_delay": 1.0,
                "fallback_to_mock": True,
            },
        )

    def add_provider(self, provider: ProviderConfig) -> None:
        """Add a new provider."""
        config = self.load_config()
        # Remove existing provider with same ID
        config.providers = [p for p in config.providers if p.id != provider.id]
        config.providers.append(provider)
        self.save_config()

    def remove_provider(self, provider_id: str) -> bool:
        """Remove a provider by ID."""
        config = self.load_config()
        original_count = len(config.providers)
        config.providers = [p for p in config.providers if p.id != provider_id]
        if len(config.providers) < original_count:
            self.save_config()
            return True
        return False

    def enable_provider(self, provider_id: str) -> bool:
        """Enable a provider."""
        config = self.load_config()
        for p in config.providers:
            if p.id == provider_id:
                p.enabled = True
                self.save_config()
                return True
        return False

    def disable_provider(self, provider_id: str) -> bool:
        """Disable a provider."""
        config = self.load_config()
        for p in config.providers:
            if p.id == provider_id:
                p.enabled = False
                self.save_config()
                return True
        return False

    def list_providers(self) -> list[ProviderConfig]:
        """List all providers."""
        config = self.load_config()
        return config.providers

    def get_enabled_providers(self) -> list[ProviderConfig]:
        """Get enabled providers sorted by priority."""
        config = self.load_config()
        return config.get_enabled_providers()

    def get_provider(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get a provider by ID."""
        config = self.load_config()
        return config.get_provider(provider_id)

    def get_settings(self):
        """Get multi-provider settings."""
        config = self.load_config()
        return config.settings
