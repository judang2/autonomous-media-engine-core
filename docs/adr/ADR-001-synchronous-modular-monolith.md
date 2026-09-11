# ADR-001: Synchronous modular monolith

Status: Accepted

Decision: One application invokes agents and executors directly through injected
callables and small dictionaries. No queue or dispatcher framework.

Reason: One offline vertical slice needs clear ownership, not distributed execution.

Tradeoffs: Calls block and work is not durable. Revisit dispatch only when real
operational throughput or recovery requirements justify it.
