import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    account_id: str = "demo-account"
    allow_publish: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        enabled = os.environ.get("AME_ALLOW_PUBLISH", "false").lower()
        if enabled not in {"true", "false"}:
            raise ValueError("AME_ALLOW_PUBLISH must be true or false")
        account = os.environ.get("AME_ACCOUNT_ID", "demo-account").strip()
        if not account:
            raise ValueError("AME_ACCOUNT_ID must not be empty")
        return cls(account, enabled == "true")
