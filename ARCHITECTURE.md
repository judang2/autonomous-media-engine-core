# Architectural invariants

- Engine orchestrates; it does not own platform access, prompts, or storage.
- Agents reason within their domains and do not orchestrate other agents.
  Calling deterministic services is allowed.
- Agents propose Actions; Policy validates authority; Executors perform effects.
- Platform-specific code stays outside Core. Composition wires implementations.
- Start synchronous and as one modular monolith.
- Persistent state ownership must be explicit; do not hide it in agents.
- Use deterministic code for deterministic decisions.
- Instagram is the first implementation boundary, not the architecture itself.
- Do not generalize one platform into a universal social-media API.
- Prefer small functions, dataclasses and dictionaries to framework ceremony.
- Add infrastructure and abstractions only for demonstrated needs.
- Model providers belong behind the worker's generation callable, not in Engine.
- Preserve the old prototype as reference; never copy its secrets.
- Record operational decision summaries, never hidden chain-of-thought.

v0.1 has no persistent storage or real platform access. The fake adapter owns only
process-local simulated posts. Tests and the CLI use the same orchestration path.
Read docs/architecture-v0.1.md before changing these boundaries.
