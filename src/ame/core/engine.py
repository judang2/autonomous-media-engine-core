"""Orchestration only: dependencies are ordinary callables."""
import json
import logging
from collections.abc import Callable, Mapping
from uuid import uuid4

from .contracts import Action, AgentResult, ExecutionResult, PolicyDecision, Status, Task

logger = logging.getLogger("ame")


def trace(task_id: str, stage: str, **fields: str) -> None:
    # Never log prompts, captions, credentials, or raw exception messages.
    logger.info(json.dumps({"task_id": task_id, "stage": stage, **fields}))


class Engine:
    def __init__(
        self,
        agents: Mapping[str, Callable[[Task], AgentResult]],
        policy: Callable[[Action], PolicyDecision],
        executors: Mapping[str, Callable[[Action], ExecutionResult]],
    ) -> None:
        self.agents = dict(agents)
        self.policy = policy
        self.executors = dict(executors)

    def run(self, brief: str, account_id: str, kind: str = "content") -> tuple[ExecutionResult, ...]:
        task = Task(str(uuid4()), kind, account_id, brief)
        return self.handle(task)

    def handle(self, task: Task) -> tuple[ExecutionResult, ...]:
        trace(task.id, "input")
        if not all(value.strip() for value in (task.id, task.kind, task.account_id, task.brief)):
            return (self._failure(task, "validation_failed"),)
        agent = self.agents.get(task.kind)
        if agent is None:
            return (self._failure(task, "unknown_task_kind"),)
        trace(task.id, "agent")
        try:
            proposal = agent(task)
        except Exception as error:
            return (self._failure(task, "agent_failed", type(error).__name__),)
        trace(task.id, "agent_result", status=proposal.status.value)
        if proposal.task_id != task.id or proposal.status != Status.SUCCESS:
            return (self._failure(task, "agent_result_invalid"),)
        # Validate the entire proposal before executing any part of it.
        ids = [action.id for action in proposal.actions]
        if len(set(ids)) != len(ids) or any(
            not action.id.strip() or action.task_id != task.id
            or action.account_id != task.account_id
            for action in proposal.actions
        ):
            return (self._failure(task, "action_identity_invalid"),)
        results = []
        for action in proposal.actions:
            trace(task.id, "action", action_id=action.id)
            try:
                decision = self.policy(action)
            except Exception as error:
                results.append(self._failure(task, "policy_failed", type(error).__name__, action.id))
                continue
            trace(task.id, "policy", action_id=action.id, allowed=str(decision.allowed))
            if not decision.allowed:
                result = ExecutionResult(task.id, action.id, Status.REJECTED, decision.reason)
            elif action.kind not in self.executors:
                result = ExecutionResult(task.id, action.id, Status.FAILED, "unknown_action_kind")
            else:
                trace(task.id, "executor", action_id=action.id)
                try:
                    result = self.executors[action.kind](action)
                    if result.task_id != task.id or result.action_id != action.id:
                        result = ExecutionResult(task.id, action.id, Status.FAILED, "execution_identity_invalid")
                except Exception as error:
                    result = self._failure(task, "executor_failed", type(error).__name__, action.id)
            trace(task.id, "execution_result", action_id=action.id, status=result.status.value, code=result.code)
            results.append(result)
        return tuple(results)

    @staticmethod
    def _failure(task: Task, code: str, error_type: str = "", action_id: str | None = None) -> ExecutionResult:
        trace(task.id, "failure", code=code, error_type=error_type)
        return ExecutionResult(task.id, action_id, Status.FAILED, code)
