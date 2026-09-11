import argparse
import json
import logging
from dataclasses import asdict
from functools import partial

from .config import Settings
from .content import ContentAgent
from .core.contracts import Status
from .core.engine import Engine
from .platforms.instagram.adapter import FakeInstagramAdapter
from .platforms.instagram.executor import InstagramExecutor
from .policy import evaluate


def main() -> int:
    parser = argparse.ArgumentParser(description="AME offline caption publishing simulation")
    parser.add_argument("brief")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        settings = Settings.from_env()
    except ValueError as error:
        parser.error(str(error))
    adapter = FakeInstagramAdapter()
    engine = Engine(
        {"content": ContentAgent()},
        partial(evaluate, settings=settings),
        {"publish_caption": InstagramExecutor(adapter)},
    )
    results = engine.run(args.brief, settings.account_id)
    print(json.dumps([asdict(result) for result in results]))
    return 0 if results and all(result.status == Status.SUCCESS for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
