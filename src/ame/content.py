"""One stateless domain worker; generation is a replaceable callable."""
from collections.abc import Callable
from dataclasses import dataclass

from .core.contracts import Action, AgentResult, Status, Task


def draft_caption(brief: str) -> str:
    """Deterministic stand-in for a future model provider."""
    return brief.strip()


@dataclass(frozen=True)
class ContentAgent:
    generate: Callable[[str], str] = draft_caption

    def __call__(self, task: Task) -> AgentResult:
        caption = self.generate(task.brief)
        action = Action(f"{task.id}:publish:1", task.id, "publish_caption", task.account_id, caption)
        return AgentResult(task.id, Status.SUCCESS, (action,), "Prepared one caption for policy review.")
