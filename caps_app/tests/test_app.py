from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from caps_app.app import create_app
from caps_app.config import AppConfig
from caps_app.db import Database
from caps_app.provider import ProviderResponse


class FakeProvider:
    async def chat(self, messages: list[dict[str, str]]) -> ProviderResponse:
        return ProviderResponse(
            text="답변을 보냅니다. 연락처는 helper@example.com 입니다.",
            provider="fake",
            model="fake-model-v1",
            latency_ms=12.5,
            usage={"input_tokens": 10, "output_tokens": 8},
        )

    async def aclose(self) -> None:
        return None


def _config(path: Path) -> AppConfig:
    return AppConfig(
        database_path=str(path),
        app_secret="a" * 48,
        encryption_secret="b" * 48,
        admin_token="c" * 48,
        provider_mode="openai_compatible",
        upstream_base_url="http://provider.invalid/v1",
        api_key="placeholder",
        model="fake-model",
        allow_insecure_dev=False,
    )


def _bootstrap(client: TestClient) -> dict[str, object]:
    response = client.get("/api/bootstrap")
    assert response.status_code == 200
    return response.json()


def _consent(client: TestClient, mode: str, terms: str) -> None:
    response = client.post(
        "/api/consent",
        json={"mode": mode, "accepted": True, "terms_version": terms},
    )
    assert response.status_code == 200


def test_research_mode_stores_encrypted_raw_and_redacted_export(tmp_path) -> None:
    database = Database(tmp_path / "app.db")
    app = create_app(_config(tmp_path / "app.db"), provider=FakeProvider(), database=database)

    with TestClient(app) as client:
        bootstrap = _bootstrap(client)
        _consent(client, "research", str(bootstrap["terms_version"]))
        response = client.post(
            "/api/chat",
            json={
                "conversation_id": "b275f494-d8ca-42dd-8857-917a01c19fea",
                "messages": [
                    {"role": "user", "content": "my-email@example.com으로 문서를 보내줘"}
                ],
            },
        )
        assert response.status_code == 200

        own = client.get("/api/data/export")
        assert own.status_code == 200
        serialized_own = json.dumps(own.json(), ensure_ascii=False)
        assert "my-email@example.com" in serialized_own

        research = client.get(
            "/api/admin/research/export",
            headers={"Authorization": f"Bearer {'c' * 48}"},
        )
        assert research.status_code == 200
        assert "my-email@example.com" not in research.text
        assert "helper@example.com" not in research.text
        assert "[EMAIL]" in research.text

        raw_database = (tmp_path / "app.db").read_bytes()
        assert b"my-email@example.com" not in raw_database


def test_private_mode_does_not_persist_conversation(tmp_path) -> None:
    database = Database(tmp_path / "app.db")
    app = create_app(_config(tmp_path / "app.db"), provider=FakeProvider(), database=database)

    with TestClient(app) as client:
        bootstrap = _bootstrap(client)
        _consent(client, "private", str(bootstrap["terms_version"]))
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "저장하지 마세요"}]},
        )
        assert response.status_code == 200
        stats = client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {'c' * 48}"},
        ).json()
        assert stats["messages"] == 0
        assert stats["research_records"] == 0


def test_withdrawal_purges_stored_rows_and_switches_private(tmp_path) -> None:
    database = Database(tmp_path / "app.db")
    app = create_app(_config(tmp_path / "app.db"), provider=FakeProvider(), database=database)

    with TestClient(app) as client:
        bootstrap = _bootstrap(client)
        _consent(client, "research", str(bootstrap["terms_version"]))
        client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "분석해줘"}]},
        )
        response = client.post("/api/consent/withdraw", json={})
        assert response.status_code == 200
        assert response.json()["mode"] == "private"
        stats = client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {'c' * 48}"},
        ).json()
        assert stats["messages"] == 0
        assert stats["research_records"] == 0


def test_chat_requires_consent_choice(tmp_path) -> None:
    app = create_app(_config(tmp_path / "app.db"), provider=FakeProvider())
    with TestClient(app) as client:
        _bootstrap(client)
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "안녕"}]},
        )
        assert response.status_code == 403


def test_admin_export_requires_token(tmp_path) -> None:
    app = create_app(_config(tmp_path / "app.db"), provider=FakeProvider())
    with TestClient(app) as client:
        response = client.get("/api/admin/research/export")
        assert response.status_code == 401
