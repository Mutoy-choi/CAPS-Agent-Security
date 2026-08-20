from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
import uuid
from collections import defaultdict, deque
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import AppConfig
from .crypto import ContentCipher
from .db import Database
from .privacy import prepare_research_text
from .provider import ChatProvider, HttpChatProvider

COOKIE_NAME = "caps_research_session"


class ConsentRequest(BaseModel):
    mode: Literal["research", "private"]
    accepted: bool
    terms_version: str


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    messages: list[ChatMessage] = Field(min_length=1)


class FeedbackRequest(BaseModel):
    conversation_id: str
    value: Literal[-1, 1]
    comment: str | None = Field(default=None, max_length=1000)


class RateLimiter:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] < now - 60:
                bucket.popleft()
            if len(bucket) >= self.limit:
                return False
            bucket.append(now)
            return True


def create_app(
    config: AppConfig | None = None,
    *,
    provider: ChatProvider | None = None,
    database: Database | None = None,
) -> FastAPI:
    settings = config or AppConfig.from_env()
    settings.validate()
    db = database or Database(settings.database_path)
    cipher = ContentCipher(settings.encryption_secret or settings.app_secret)
    chat_provider = provider or HttpChatProvider(settings)
    limiter = RateLimiter(settings.rate_limit_per_minute)
    static_dir = Path(__file__).with_name("static")

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        db.initialize()
        yield
        close = getattr(chat_provider, "aclose", None)
        if close is not None:
            await close()

    app = FastAPI(title=settings.public_name, version="0.1.0", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.middleware("http")
    async def security_headers(request: Request, call_next: Any) -> Response:
        if int(request.headers.get("content-length", "0") or "0") > 1_000_000:
            return JSONResponse({"detail": "request_too_large"}, status_code=413)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "connect-src 'self'; img-src 'self' data:"
        )
        return response

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/healthz")
    async def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "caps-research-chat",
            "provider_mode": settings.provider_mode,
            "model": settings.model,
        }

    @app.get("/api/bootstrap")
    async def bootstrap(request: Request) -> Response:
        token = request.cookies.get(COOKIE_NAME)
        new_token = False
        if not token or len(token) < 32:
            token = secrets.token_urlsafe(32)
            new_token = True
        session = db.ensure_session(_token_hash(token))
        response = JSONResponse(
            {
                "public_name": settings.public_name,
                "mode": session["mode"],
                "terms_version": settings.research_terms_version,
                "model": settings.model,
                "provider_mode": settings.provider_mode,
                "retention_days": settings.research_retention_days,
            }
        )
        if new_token:
            response.set_cookie(
                COOKIE_NAME,
                token,
                httponly=True,
                secure=settings.secure_cookie,
                samesite="lax",
                max_age=60 * 60 * 24 * settings.research_retention_days,
                path="/",
            )
        return response

    @app.post("/api/consent")
    async def consent(payload: ConsentRequest, request: Request) -> dict[str, Any]:
        token_hash = _required_token_hash(request)
        if not payload.accepted:
            raise HTTPException(status_code=400, detail="explicit_acceptance_required")
        if payload.terms_version != settings.research_terms_version:
            raise HTTPException(status_code=409, detail="terms_version_mismatch")
        session = db.set_consent(token_hash, payload.mode, payload.terms_version)
        return {"mode": session["mode"], "terms_version": session["terms_version"]}

    @app.post("/api/consent/withdraw")
    async def withdraw(request: Request) -> dict[str, str]:
        token_hash = _required_token_hash(request)
        db.withdraw_and_purge(token_hash)
        return {"mode": "private", "status": "purged"}

    @app.post("/api/chat")
    async def chat(payload: ChatRequest, request: Request) -> dict[str, Any]:
        token_hash = _required_token_hash(request)
        session = db.get_session(token_hash)
        if session is None or session["mode"] not in {"research", "private"}:
            raise HTTPException(status_code=403, detail="consent_choice_required")
        if not limiter.allow(token_hash):
            raise HTTPException(status_code=429, detail="rate_limit_exceeded")
        if len(payload.messages) > settings.max_history_messages:
            raise HTTPException(status_code=400, detail="too_many_history_messages")

        messages = [item.model_dump() for item in payload.messages]
        if any(len(item["content"]) > settings.max_message_chars for item in messages):
            raise HTTPException(status_code=400, detail="message_too_long")
        if messages[-1]["role"] != "user":
            raise HTTPException(status_code=400, detail="last_message_must_be_user")

        result = await chat_provider.chat(messages)
        conversation_id = _conversation_id(payload.conversation_id)
        if session["mode"] == "research":
            user_text = messages[-1]["content"]
            user_research = prepare_research_text(user_text).to_dict()
            assistant_research = prepare_research_text(result.text).to_dict()
            db.store_exchange(
                token_hash=token_hash,
                conversation_id=conversation_id,
                user_encrypted=cipher.encrypt(user_text),
                assistant_encrypted=cipher.encrypt(result.text),
                user_sha256=_sha256(user_text),
                assistant_sha256=_sha256(result.text),
                provider=result.provider,
                model=result.model,
                latency_ms=result.latency_ms,
                usage=result.usage,
                terms_version=settings.research_terms_version,
                user_research=user_research,
                assistant_research=assistant_research,
            )

        return {
            "conversation_id": conversation_id,
            "message": {"role": "assistant", "content": result.text},
            "model": result.model,
            "provider": result.provider,
            "latency_ms": round(result.latency_ms, 2),
            "usage": result.usage,
            "storage_mode": session["mode"],
        }

    @app.post("/api/feedback")
    async def feedback(payload: FeedbackRequest, request: Request) -> dict[str, bool]:
        token_hash = _required_token_hash(request)
        db.add_feedback(token_hash, payload.conversation_id, payload.value, payload.comment)
        return {"accepted": True}

    @app.get("/api/data/export")
    async def export_user(request: Request) -> dict[str, Any]:
        token_hash = _required_token_hash(request)
        rows = db.export_session_rows(token_hash)
        messages = []
        for row in rows["messages"]:
            messages.append(
                {
                    "conversation_id": row["conversation_id"],
                    "role": row["role"],
                    "content": cipher.decrypt(row["encrypted_content"]),
                    "provider": row["provider"],
                    "model": row["model"],
                    "created_at": row["created_at"],
                }
            )
        session = rows["session"]
        return {
            "mode": session["mode"],
            "terms_version": session["terms_version"],
            "consent_at": session["consent_at"],
            "messages": messages,
        }

    @app.delete("/api/data")
    async def delete_user(request: Request) -> Response:
        token_hash = _required_token_hash(request)
        db.delete_session(token_hash)
        response = JSONResponse({"deleted": True})
        response.delete_cookie(COOKIE_NAME, path="/")
        return response

    @app.get("/api/admin/stats")
    async def admin_stats(authorization: str | None = Header(default=None)) -> dict[str, Any]:
        _require_admin(authorization, settings.admin_token)
        return db.admin_stats()

    @app.get("/api/admin/research/export")
    async def admin_research_export(
        authorization: str | None = Header(default=None),
    ) -> PlainTextResponse:
        _require_admin(authorization, settings.admin_token)
        rows = db.research_export()
        content = "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
        )
        return PlainTextResponse(
            content,
            media_type="application/x-ndjson",
            headers={"Content-Disposition": "attachment; filename=caps-research.jsonl"},
        )

    return app


def main(argv: Sequence[str] | None = None) -> int:
    del argv
    config = AppConfig.from_env()
    config.validate()
    uvicorn.run(create_app(config), host="0.0.0.0", port=config.port)
    return 0


def _required_token_hash(request: Request) -> str:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="bootstrap_required")
    return _token_hash(token)


def _token_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _conversation_id(value: str | None) -> str:
    if value:
        try:
            return str(uuid.UUID(value))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid_conversation_id") from exc
    return str(uuid.uuid4())


def _require_admin(authorization: str | None, expected: str) -> None:
    if not expected:
        raise HTTPException(status_code=503, detail="admin_endpoint_disabled")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="invalid_admin_token")
