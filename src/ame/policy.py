from .config import Settings
from .core.contracts import Action, PolicyDecision


def evaluate(action: Action, settings: Settings) -> PolicyDecision:
    if action.kind != "publish_caption":
        return PolicyDecision(False, "unsupported_action")
    if action.account_id != settings.account_id:
        return PolicyDecision(False, "account_not_allowed")
    if not isinstance(action.caption, str) or not action.caption.strip():
        return PolicyDecision(False, "invalid_caption")
    if not settings.allow_publish:
        return PolicyDecision(False, "publish_disabled")
    return PolicyDecision(True, "approved")
