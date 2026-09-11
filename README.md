# Autonomous Media Engine

A small synchronous modular monolith with one offline vertical slice:
owner brief → Engine → ContentAgent → policy → InstagramExecutor →
FakeInstagramAdapter → ExecutionResult.

No network access, credentials, or runtime dependencies are required. The adapter
simulates a caption post in memory; it is not an implementation of Instagram
publishing. Real Instagram media requirements and authentication remain unimplemented.

## Run from source (Python 3.11+)

In PowerShell, from this repository:

```powershell
$env:PYTHONPATH = "$PWD/src"
python -m unittest discover -s tests -v
$env:AME_ALLOW_PUBLISH = "true"
python -m ame "A quiet morning by the sea."
```

Publishing permission defaults to false. Omit the environment override to observe
a policy rejection (exit 1); successful simulation exits 0. The command always uses
the fake adapter, even when permission is enabled. Configuration reads environment
variables; .env is not automatically loaded. .env.example contains placeholders only.

For an ordinary installed Python environment, optionally use
`python -m pip install -e .`, then `ame "Your brief"`.
Installing may require downloading build tooling; source execution does not.

This machine's launcher has no registered Python. Bootstrap verification used:
`C:\Users\judan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
Use that executable in place of `python` if needed.

## Boundaries

- `core/`: contracts, routing, proposal identity checks, policy/executor coordination.
- `content.py`: one stateless worker with injected caption generation.
- `policy.py`: deterministic action, account and permission checks.
- `platforms/instagram/`: executor and in-memory test adapter.
- `config.py`: explicit owner settings.
- `__main__.py`: composition and CLI input.

See [architecture invariants](ARCHITECTURE.md),
[detailed rationale](docs/architecture-v0.1.md), and
[bootstrap review](docs/bootstrap-review.md).
