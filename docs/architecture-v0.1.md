# Architecture v0.1

## Scope and vision

AME may evolve to support generation, publishing, interactions, analytics,
scheduling, owner preferences and multiple media platforms. This milestone validates
only one offline caption workflow. Instagram is a boundary to validate first, not
a universal model. A caption-only fake does not imply that real Instagram accepts
caption-only posts.

## Flow and responsibility

The CLI loads Settings and injects dependencies. Engine.run creates a Task from an
owner brief. Engine.handle routes it through a dictionary to ContentAgent. The agent
calls a deterministic caption generator and returns one Action in AgentResult.
Engine checks task/account correlation and duplicate action IDs before any effects.
Policy checks the supported action, target account, nonempty caption and explicit
publishing flag. Only an accepted action reaches the executor. The executor calls
the fake Instagram adapter and returns a typed ExecutionResult.

The callable invocation is the synchronous dispatch boundary. There is no separate
Dispatcher class. Executor routing is by action kind; Engine imports no platform
implementation. The Instagram executor currently owns the single publish-caption
operation. A second real platform should inform any eventual routing changes.

ContentAgent's injected generation callable can be replaced with a model provider
without changing Engine. There are no provider credentials, SDKs, prompt framework
or live model calls. The initial generator trims owner-provided text; it does not
pretend to perform creative reasoning.

## Contracts and authority

Frozen dataclasses define Task, Action, AgentResult, PolicyDecision and
ExecutionResult. Task/action IDs are explicit; action IDs are stable for a given
task. Policy defaults to denial. Task/account identity is checked independently of
agent output so an agent cannot change the target account through its proposal.
These are in-process contracts for trusted Python components, not an untrusted
JSON parsing or process-security boundary.

The owner permission flag applies to this offline demonstration only. A production
approval scheme, platform validation (including media), and credentials must be
designed before wiring real mutations. The agent receives only its task and
generator. It receives no adapter, executor or global mutable system object.

## State ownership

Engine owns the current task/proposal/results during a call. Settings owns immutable
account and permission configuration. ContentAgent has a dependency but no persistent
working state. FakeInstagramAdapter owns simulated posts in a process-local list;
the list disappears when the process ends. There is no persistent state yet.
Future content history and account memory belong in an explicit repository/service,
not hidden inside agents.

## Failures and traceability

JSON log messages carry task ID, stage, and action ID when available. Input text,
captions, credentials and raw exception messages are omitted. Returned codes
distinguish input validation, missing routes, agent failure, proposal identity,
policy failure/rejection, executor failure and platform failure. Ordinary exceptions
at component boundaries become explicit failed results; process interrupts propagate.

No automatic retry is implemented. A platform failure can be ambiguous after a
mutation; blindly retrying can duplicate a post. IDs allow later correlation but
there is no durable deduplication or exactly-once guarantee. Replaying a task against
the fake can append another post. Multiple actions are sequential, with individual
results and no transaction/rollback; the built-in agent proposes exactly one.

## Deferred decisions

Scheduling ownership; whether Strategy needs an agent; memory sophistication;
action-specific owner approvals; multiple accounts; worker processes; event bus
justification; and what a second platform reveals about shared operations remain
open. No queue, event type, AccessProvider, MemoryAgent, database, vector system,
plugin framework, distributed worker, scheduler or extra domain agent is included.

## Evolution

Next, locate and review useful prototype behavior without reading/copying secrets.
Define one real Instagram operation's payload and failure behavior, then implement
it behind this platform boundary with offline tests. Live execution needs separate
owner authorization. Extract new abstractions only when this concrete work requires
them. Consult the short root invariants and ADRs before expanding scope.
