from dataclasses import dataclass

from ...core.contracts import Action, ExecutionResult, Status
from .adapter import FakeInstagramAdapter


@dataclass
class InstagramExecutor:
    adapter: FakeInstagramAdapter

    def __call__(self, action: Action) -> ExecutionResult:
        if action.kind != "publish_caption":
            return ExecutionResult(action.task_id, action.id, Status.REJECTED, "unsupported_action")
        try:
            external_id = self.adapter.publish_caption(action.account_id, action.caption, action.id)
        except Exception:
            # Publishing may have succeeded before a transport failure.
            # Do not automatically retry an ambiguous mutation.
            return ExecutionResult(action.task_id, action.id, Status.FAILED, "platform_failed")
        return ExecutionResult(action.task_id, action.id, Status.SUCCESS, "simulated", external_id)
