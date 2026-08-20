from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class DefenseMode(StrEnum):
    NONE = "none"
    PROMPT_ONLY = "prompt_only"
    ACTION_GATEWAY = "action_gateway"
    FULL_STACK = "full_stack"


class Decision(StrEnum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    user_goal: str
    allowed_actions: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    variants: tuple[str, ...]
    uploaded_artifact: str
    canary: str
    external_sink: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Scenario:
        return cls(
            scenario_id=str(value["scenario_id"]),
            user_goal=str(value["user_goal"]),
            allowed_actions=tuple(value["allowed_actions"]),
            forbidden_actions=tuple(value["forbidden_actions"]),
            variants=tuple(value["variants"]),
            uploaded_artifact=str(value["uploaded_artifact"]),
            canary=str(value["canary"]),
            external_sink=str(value["external_sink"]),
        )


@dataclass(frozen=True)
class ActionRequest:
    action: str
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)
    data_sources: tuple[str, ...] = ()
    data_sensitivity: tuple[str, ...] = ()
    destination: str = "internal"
    side_effect: str = "read"
    user_approved: bool = False
    artifact_trust: str = "untrusted"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    policy_id: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "decision": self.decision.value,
            "policy_id": self.policy_id,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ActionEvent:
    request: ActionRequest
    policy: PolicyDecision
    executed: bool
    result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "policy": self.policy.to_dict(),
            "executed": self.executed,
            "result": self.result,
        }


@dataclass(frozen=True)
class RunResult:
    run_id: str
    scenario_id: str
    variant: str
    defense: DefenseMode
    attack_success: bool
    benign_task_success: bool
    false_block: bool
    unauthorized_tool_invocation: bool
    unauthorized_data_flow: bool
    events: tuple[ActionEvent, ...]
    final_state: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "variant": self.variant,
            "defense": self.defense.value,
            "attack_success": self.attack_success,
            "benign_task_success": self.benign_task_success,
            "false_block": self.false_block,
            "unauthorized_tool_invocation": self.unauthorized_tool_invocation,
            "unauthorized_data_flow": self.unauthorized_data_flow,
            "events": [event.to_dict() for event in self.events],
            "final_state": self.final_state,
        }
