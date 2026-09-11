import json
import unittest
from dataclasses import replace
from functools import partial
from unittest.mock import Mock, patch

from ame.config import Settings
from ame.content import ContentAgent
from ame.core.contracts import AgentResult, ExecutionResult, Status, Task
from ame.core.engine import Engine
from ame.platforms.instagram.adapter import FakeInstagramAdapter
from ame.platforms.instagram.executor import InstagramExecutor
from ame.policy import evaluate


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.task = Task("task-1", "content", "account-1", "  Hello sea  ")
        self.adapter = FakeInstagramAdapter()
        self.agent = ContentAgent()
        self.executor = Mock(wraps=InstagramExecutor(self.adapter))
        self.engine = Engine(
            {"content": self.agent},
            partial(evaluate, settings=Settings("account-1", True)),
            {"publish_caption": self.executor},
        )

    def test_full_slice(self):
        result, = self.engine.handle(self.task)
        self.assertEqual(result.status, Status.SUCCESS)
        self.assertEqual(result.external_id, "fake-post-1")
        self.assertEqual(self.adapter.posts, [("account-1", "Hello sea", "task-1:publish:1")])
        self.executor.assert_called_once()

    def test_input_creates_correlated_task(self):
        result, = self.engine.run("hello", "account-1")
        self.assertTrue(result.task_id)
        self.assertEqual(result.action_id, result.task_id + ":publish:1")

    def test_default_permission_blocks_executor(self):
        self.engine.policy = partial(evaluate, settings=Settings("account-1"))
        result, = self.engine.handle(self.task)
        self.assertEqual(result.status, Status.REJECTED)
        self.assertEqual(result.code, "publish_disabled")
        self.executor.assert_not_called()
        self.assertEqual(self.adapter.posts, [])

    def test_routes_only_selected_agent(self):
        unused = Mock(side_effect=AssertionError("wrong route"))
        self.engine.agents["other"] = unused
        self.engine.handle(self.task)
        unused.assert_not_called()

    def test_missing_route_and_invalid_input(self):
        for task, code in [
            (replace(self.task, kind="missing"), "unknown_task_kind"),
            (replace(self.task, brief=" "), "validation_failed"),
        ]:
            with self.subTest(code=code):
                self.assertEqual(self.engine.handle(task)[0].code, code)
        self.executor.assert_not_called()

    def test_generator_is_replaceable(self):
        self.engine.agents["content"] = ContentAgent(lambda brief: "Generated caption")
        self.engine.handle(self.task)
        self.assertEqual(self.adapter.posts[0][1], "Generated caption")

    def test_policy_checks_kind_account_and_caption(self):
        action = self.agent(self.task).actions[0]
        for changed, code in [
            (replace(action, kind="delete"), "unsupported_action"),
            (replace(action, account_id="other"), "account_not_allowed"),
            (replace(action, caption=" "), "invalid_caption"),
        ]:
            with self.subTest(code=code):
                decision = evaluate(changed, Settings("account-1", True))
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.reason, code)

    def test_proposal_identity_checked_before_any_effects(self):
        proposal = self.agent(self.task)
        action = proposal.actions[0]
        for actions in [
            (action, replace(action, id="second", account_id="other")),
            (replace(action, task_id="other"),),
            (action, action),
        ]:
            with self.subTest(actions=actions):
                self.engine.agents["content"] = lambda task: replace(proposal, actions=actions)
                self.assertEqual(self.engine.handle(self.task)[0].code, "action_identity_invalid")
        self.executor.assert_not_called()

    def test_agent_failure_is_explicit(self):
        self.engine.agents["content"] = Mock(side_effect=RuntimeError("private detail"))
        self.assertEqual(self.engine.handle(self.task)[0].code, "agent_failed")
        self.executor.assert_not_called()

    def test_mismatched_agent_result(self):
        self.engine.agents["content"] = lambda task: AgentResult("other", Status.SUCCESS)
        self.assertEqual(self.engine.handle(self.task)[0].code, "agent_result_invalid")
        self.executor.assert_not_called()

    def test_policy_error_fails_closed(self):
        self.engine.policy = Mock(side_effect=RuntimeError())
        self.assertEqual(self.engine.handle(self.task)[0].code, "policy_failed")
        self.executor.assert_not_called()

    def test_platform_is_replaceable_and_failure_not_retried(self):
        adapter = Mock()
        adapter.publish_caption.side_effect = TimeoutError("private detail")
        self.engine.executors["publish_caption"] = InstagramExecutor(adapter)
        result, = self.engine.handle(self.task)
        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.code, "platform_failed")
        adapter.publish_caption.assert_called_once()

    def test_unknown_executor(self):
        self.engine.executors.clear()
        self.assertEqual(self.engine.handle(self.task)[0].code, "unknown_action_kind")

    def test_executor_failure_and_mismatched_result(self):
        for executor, code in [
            (Mock(side_effect=RuntimeError()), "executor_failed"),
            (lambda action: ExecutionResult("wrong", action.id, Status.SUCCESS, "bad"),
             "execution_identity_invalid"),
        ]:
            self.engine.executors["publish_caption"] = executor
            self.assertEqual(self.engine.handle(self.task)[0].code, code)

    def test_structured_trace_without_content(self):
        with self.assertLogs("ame", level="INFO") as captured:
            self.engine.handle(self.task)
        rows = [json.loads(record.getMessage()) for record in captured.records]
        self.assertTrue(all(row["task_id"] == self.task.id for row in rows))
        self.assertTrue({"input", "agent", "agent_result", "action", "policy", "executor",
                         "execution_result"} <= {row["stage"] for row in rows})
        self.assertNotIn("Hello sea", str(rows))

    def test_configuration_defaults_and_validation(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(Settings.from_env().allow_publish)
        with patch.dict("os.environ", {"AME_ALLOW_PUBLISH": "yes"}, clear=True):
            with self.assertRaises(ValueError):
                Settings.from_env()


if __name__ == "__main__":
    unittest.main()
