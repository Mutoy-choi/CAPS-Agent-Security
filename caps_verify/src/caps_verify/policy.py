from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import ActionRequest, Decision, PolicyDecision
from .resource_loader import load_json


@dataclass(frozen=True)
class PolicyRule:
    rule_id: str
    decision: Decision
    reason: str
    when: dict[str, Any]

    def matches(self, request: ActionRequest) -> bool:
        value = request.to_dict()
        return all(
            _match_value(value.get(key), expected)
            for key, expected in self.when.items()
        )


class PolicyEngine:
    def __init__(self, rules: tuple[PolicyRule, ...]) -> None:
        self.rules = rules

    @classmethod
    def default(cls) -> PolicyEngine:
        payload = load_json("default_policy.json")
        rules = tuple(
            PolicyRule(
                rule_id=str(item["id"]),
                decision=Decision(str(item["decision"])),
                reason=str(item["reason"]),
                when=dict(item["when"]),
            )
            for item in payload["rules"]
        )
        return cls(rules)

    def evaluate(self, request: ActionRequest) -> PolicyDecision:
        for rule in self.rules:
            if rule.matches(request):
                return PolicyDecision(rule.decision, rule.rule_id, rule.reason)
        return PolicyDecision(Decision.ALLOW, "default-allow", "No blocking policy matched.")


def _match_value(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if "contains_any" in expected:
            expected_values = set(expected["contains_any"])
            actual_values = (
                set(actual or [])
                if isinstance(actual, list | tuple | set)
                else {actual}
            )
            return bool(expected_values & actual_values)
        if "equals" in expected:
            return actual == expected["equals"]
        raise ValueError(f"Unsupported policy operator: {expected}")
    return actual == expected
