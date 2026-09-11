from dataclasses import dataclass, field


@dataclass
class FakeInstagramAdapter:
    """Records simulated posts in memory. Does not access Instagram."""
    posts: list[tuple[str, str, str]] = field(default_factory=list)

    def publish_caption(self, account_id: str, caption: str, action_id: str) -> str:
        self.posts.append((account_id, caption, action_id))
        return f"fake-post-{len(self.posts)}"
