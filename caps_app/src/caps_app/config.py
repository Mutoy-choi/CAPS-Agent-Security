from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

ProviderMode = Literal["openai_compatible", "anthropic"]


@dataclass(frozen=True)
class AppConfig:
    database_path: str = "/data/caps_app.db"
    app_secret: str = ""
    encryption_secret: str = ""
    admin_token: str = ""
    provider_mode: ProviderMode = "openai_compatible"
    upstream_base_url: str = "http://127.0.0.1:8788/v1"
    api_key: str = "local-placeholder"
    gateway_client_token: str = ""
    model: str = "gpt-4o-mini"
    public_name: str = "CAPS Unlock Research Chat"
    research_terms_version: str = "caps-research-v1"
    research_retention_days: int = 365
    secure_cookie: bool = False
    allow_insecure_dev: bool = False
    port: int = 8000
    request_timeout_seconds: float = 180.0
    max_history_messages: int = 24
    max_message_chars: int = 20_000
    rate_limit_per_minute: int = 30

    @classmethod
    def from_env(cls) -> AppConfig:
        return cls(
            database_path=os.environ.get("CAPS_APP_DATABASE_PATH", "/data/caps_app.db"),
            app_secret=os.environ.get("CAPS_APP_SECRET", ""),
            encryption_secret=os.environ.get("CAPS_APP_ENCRYPTION_SECRET", ""),
            admin_token=os.environ.get("CAPS_APP_ADMIN_TOKEN", ""),
            provider_mode=os.environ.get(
                "CAPS_APP_PROVIDER_MODE", "openai_compatible"
            ),  # type: ignore[arg-type]
            upstream_base_url=os.environ.get(
                "CAPS_APP_UPSTREAM_BASE_URL", "http://127.0.0.1:8788/v1"
            ),
            api_key=os.environ.get("CAPS_APP_API_KEY", "local-placeholder"),
            gateway_client_token=os.environ.get("CAPS_APP_GATEWAY_CLIENT_TOKEN", ""),
            model=os.environ.get("CAPS_APP_MODEL", "gpt-4o-mini"),
            public_name=os.environ.get("CAPS_APP_PUBLIC_NAME", "CAPS Unlock Research Chat"),
            research_terms_version=os.environ.get(
                "CAPS_APP_RESEARCH_TERMS_VERSION", "caps-research-v1"
            ),
            research_retention_days=int(
                os.environ.get("CAPS_APP_RESEARCH_RETENTION_DAYS", "365")
            ),
            secure_cookie=_bool_env("CAPS_APP_SECURE_COOKIE", False),
            allow_insecure_dev=_bool_env("CAPS_APP_ALLOW_INSECURE_DEV", False),
            port=int(os.environ.get("CAPS_APP_PORT", "8000")),
            request_timeout_seconds=float(
                os.environ.get("CAPS_APP_REQUEST_TIMEOUT_SECONDS", "180")
            ),
            max_history_messages=int(
                os.environ.get("CAPS_APP_MAX_HISTORY_MESSAGES", "24")
            ),
            max_message_chars=int(os.environ.get("CAPS_APP_MAX_MESSAGE_CHARS", "20000")),
            rate_limit_per_minute=int(
                os.environ.get("CAPS_APP_RATE_LIMIT_PER_MINUTE", "30")
            ),
        )

    def validate(self) -> None:
        if self.provider_mode not in {"openai_compatible", "anthropic"}:
            raise ValueError("CAPS_APP_PROVIDER_MODE must be openai_compatible or anthropic")
        if not self.upstream_base_url.startswith(("http://", "https://")):
            raise ValueError("CAPS_APP_UPSTREAM_BASE_URL must be an HTTP(S) URL")
        if not self.model:
            raise ValueError("CAPS_APP_MODEL is required")
        if self.research_retention_days < 1:
            raise ValueError("CAPS_APP_RESEARCH_RETENTION_DAYS must be positive")
        if self.port < 1 or self.port > 65535:
            raise ValueError("CAPS_APP_PORT must be between 1 and 65535")
        if self.allow_insecure_dev:
            return
        for name, value in (
            ("CAPS_APP_SECRET", self.app_secret),
            ("CAPS_APP_ENCRYPTION_SECRET", self.encryption_secret),
            ("CAPS_APP_ADMIN_TOKEN", self.admin_token),
        ):
            if len(value) < 32:
                raise ValueError(f"{name} must contain at least 32 characters")


def _bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
