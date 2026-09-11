# ADR-002: Proposals separated from authority

Status: Accepted

Decision: Agents return proposed actions to Engine; deterministic policy gates the
executor. Bootstrap uses only an in-memory Instagram adapter.

Reason: Validate orchestration without credentials or external mutations. Keep
domain work independent of publishing authority and platform implementation.

Tradeoffs: This proves boundaries, not Instagram compatibility. Real media payloads,
authentication, platform errors and approvals need separate implementation and tests.
