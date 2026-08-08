# Future Work

This document is a living backlog for ideas that are intentionally outside the
current Codex-only v1 Skill. It is a place to record future direction without
turning every idea into a current dependency or promise.

## Planned extensions

### 1. Executable coordination helper

Explore a small helper that manages a parent-owned task ledger, correlates
`task_id` and `thread_id`, deduplicates report and completion delivery, and
makes the integration gate explicit. This would test executable coordination
logic without pretending to replace the Codex host.

### 2. Python protocol simulator

Explore a deterministic state-machine simulator for out-of-order reports,
duplicate events, missing delivery, blocked routing, review-source validation,
and terminal-result transitions. The simulator would validate the abstract
protocol; it would not be evidence that every Codex host version exposes the
same runtime events.

### 3. Host integration layer

Explore adapters for task creation, project-context verification, parent reply
routes, completion events, and bounded waiting when the host exposes stable
interfaces for them.

### 4. Concurrency controller

Explore an optional controller that turns the six-window ceiling into an
adaptive policy based on task independence, host limits, available capacity,
and the cost of duplicate context.

### 5. Report and review-source tooling

Explore schema validation for worker reports, review-source existence checks,
stale-artifact detection, and machine-readable parent-ledger snapshots.

### 6. Durable state and recovery

Explore optional durable coordination state, continuation records, and recovery
procedures for a parent task that is interrupted or resumed later. These should
remain optional rather than becoming mandatory product dependencies.

### 7. Release automation

Explore a small release check that validates the exact Git commit or archive
intended for publication, including public-file discovery, private-state
exclusion, license presence, reference links, and reproducible validation output.

### 8. Review-model diversity guidance

Document practical policies for using Luna Max for routine downstream work and
Sol or another configured reviewer for security, architecture, concurrency,
data-integrity, and release-critical review. The default model policy should
remain user-overridable.

## Explicitly not part of the current v1

The following ideas are recorded for future consideration, not current scope:

- a background task-scheduling service;
- a resident daemon;
- an independent ledger database;
- a message broker;
- a full Codex-host orchestration server;
- automatic model escalation without user or project configuration.
