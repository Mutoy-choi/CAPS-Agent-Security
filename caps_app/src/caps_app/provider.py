from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from .config import AppConfig


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    provider: str
    model: str
    latency_ms: float
    usage: dict[str, int | float]


class ChatProvider(Protocol):
    async def chat(self, messages: list[dict[str, str]]) -> ProviderResponse: ...

    async def aclose(self) -> None: ...


class HttpChatProvider:
    def __init__(self, config: AppConfig, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.config = config
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.request_timeout_seconds),
            transport=transport,
            follow_redirects=False,
        )

    async def chat(self, messages: list[dict[str, str]]) -> ProviderResponse:
        started = time.perf_counter()
        if self.config.provider_mode == "anthropic":
            payload, headers, url = self._anthropic_request(messages)
        else:
            payload, headers, url = self._openai_request(messages)

        try:
            response = await self._client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            value = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Configured model provider request failed") from exc
        except ValueError as exc:
            raise RuntimeError("Configured model provider returned invalid JSON") from exc

        latency_ms = (time.perf_counter() - started) * 1000
        if self.config.provider_mode == "anthropic":
            text = _anthropic_text(value)
        else:
            text = _openai_text(value)
        resolved_model = value.get("model") if isinstance(value, dict) else None
        return ProviderResponse(
            text=text,
            provider=self.config.provider_mode,
            model=resolved_model if isinstance(resolved_model, str) else self.config.model,
            latency_ms=latency_ms,
            usage=_numeric_usage(value.get("usage") if isinstance(value, dict) else None),
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    def _openai_request(
        self, messages: list[dict[str, str]]
    ) -> tuple[dict[str, Any], dict[str, str], str]:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        if self.config.gateway_client_token:
            headers["X-CAPS-Client-Token"] = self.config.gateway_client_token
        return (
            {"model": self.config.model, "messages": messages, "temperature": 0.2},
            headers,
            _join(self.config.upstream_base_url, "chat/completions"),
        )

    def _anthropic_request(
        self, messages: list[dict[str, str]]
    ) -> tuple[dict[str, Any], dict[str, str], str]:
        system_parts = [item["content"] for item in messages if item["role"] == "system"]
        conversation = [item for item in messages if item["role"] in {"user", "assistant"}]
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        if self.config.gateway_client_token:
            headers["X-CAPS-Client-Token"] = self.config.gateway_client_token
        payload: dict[str, Any] = {
            "model": self.config.model,
            "max_tokens": 2048,
            "messages": conversation,
        }
        if system_parts:
            payload["system"] = "\n".join(system_parts)
        return payload, headers, _join(self.config.upstream_base_url, "messages")


def _join(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def _openai_text(value: Any) -> str:
    if not isinstance(value, dict):
        raise RuntimeError("OpenAI-compatible response must be a JSON object")
    choices = value.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("OpenAI-compatible response did not contain choices")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            item.get("text")
            for item in content
            if isinstance(item, dict) and isinstance(item.get("text"), str)
        ]
        if parts:
            return "\n".join(parts)
    raise RuntimeError("OpenAI-compatible response did not contain assistant text")


def _anthropic_text(value: Any) -> str:
    if not isinstance(value, dict) or not isinstance(value.get("content"), list):
        raise RuntimeError("Anthropic response did not contain content blocks")
    parts = [
        block.get("text")
        for block in value["content"]
        if isinstance(block, dict)
        and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]
    if not parts:
        raise RuntimeError("Anthropic response did not contain a text block")
    return "\n".join(parts)


def _numeric_usage(value: Any) -> dict[str, int | float]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): item
        for key, item in value.items()
        if isinstance(item, int | float) and not isinstance(item, bool)
    }
