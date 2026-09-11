from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Task:
    id: str
    kind: str
    account_id: str
    brief: str


@dataclass(frozen=True)
class Action:
    id: str
    task_id: str
    kind: str
    account_id: str
    caption: str


@dataclass(frozen=True)
class AgentResult:
    task_id: str
    status: Status
    actions: tuple[Action, ...] = ()
    decision_summary: str = ""


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True)
class ExecutionResult:
    task_id: str
    action_id: str | None
    status: Status
    code: str
    external_id: str | None = None
