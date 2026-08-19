from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL = re.compile(
    r"(?<![A-Z0-9._%+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![A-Z0-9._%+-])",
    re.IGNORECASE,
)
_PHONE = re.compile(r"(?<!\d)(?:\+?82[- ]?)?0?1[016789][- ]?\d{3,4}[- ]?\d{4}(?!\d)")
_URL = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)
_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_CARD = re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)")
_KR_RRN = re.compile(r"(?<!\d)\d{6}[- ]?[1-4]\d{6}(?!\d)")
_API_KEY = re.compile(
    r"(?i)(?:bearer\s+[A-Za-z0-9._~+/=-]{16,}|(?:sk|pk|api)[-_][A-Za-z0-9_-]{16,})"
)
_PASSWORD = re.compile(r"(?i)(password|passwd|비밀번호|secret)\s*[:=]\s*\S+")


@dataclass(frozen=True)
class ResearchText:
    text: str
    labels: tuple[str, ...]
    task_class: str

    def to_dict(self) -> dict[str, object]:
        return {"text": self.text, "labels": list(self.labels), "task_class": self.task_class}


def prepare_research_text(value: str) -> ResearchText:
    labels: list[str] = []
    high_risk = False

    replacements = (
        (_KR_RRN, "[KOREAN_RESIDENT_ID]", "resident_id", True),
        (_CARD, "[PAYMENT_CARD]", "payment_card", True),
        (_API_KEY, "[SECRET_TOKEN]", "secret_token", True),
        (_PASSWORD, "[PASSWORD_FIELD]", "password", True),
        (_EMAIL, "[EMAIL]", "email", False),
        (_PHONE, "[PHONE]", "phone", False),
        (_URL, "[URL]", "url", False),
        (_IP, "[IP_ADDRESS]", "ip_address", False),
    )

    redacted = value
    for pattern, replacement, label, severe in replacements:
        if pattern.search(redacted):
            labels.append(label)
            high_risk = high_risk or severe
            redacted = pattern.sub(replacement, redacted)

    if high_risk:
        redacted = "[REDACTED_HIGH_RISK_MESSAGE]"
    return ResearchText(
        text=redacted,
        labels=tuple(sorted(set(labels))),
        task_class=classify_task(value),
    )


def classify_task(value: str) -> str:
    lowered = value.lower()
    classes = (
        ("code", ("코드", "함수", "버그", "python", "javascript", "sql", "api")),
        ("document", ("문서", "pdf", "요약", "보고서", "계약서", "논문")),
        ("creative", ("소설", "시", "카피", "아이디어", "스토리", "브랜드")),
        ("analysis", ("분석", "비교", "평가", "통계", "전략", "리서치")),
        ("translation", ("번역", "translate", "한국어로", "영어로")),
        ("agent_tool", ("mcp", "plugin", "skill", "tool", "에이전트", "agent")),
    )
    for name, markers in classes:
        if any(marker in lowered for marker in markers):
            return name
    return "general"
