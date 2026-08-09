# Future Work

This document records ideas intentionally outside the current Constellary
`v2.0.0-alpha` candidate. Codex Desktop is the only executable coordination
surface in v2, and CLI is not supported or executable in `v2.0.0`.

## Explicit future CLI Adapter backlog

A CLI Adapter may be studied only as a separately specified, explicit opt-in
adapter. It must never be selected automatically when Desktop is unavailable.
Before any implementation, the design and tests must cover:

1. adapter selection and an explicit user opt-in boundary;
2. process lifecycle supervision and deterministic process cleanup;
3. structured report transport to the immediate coordinator;
4. task/thread identity correlation and host/project context boundaries;
5. concurrency limits, cancellation, timeout, and duplicate-event handling;
6. implementation, reviewer, repair, and fresh re-review creation;
7. security, secret handling, permissions, and temporary-file hygiene;
8. cross-platform behavior and failure reporting;
9. end-to-end verification that distinguishes visible tasks from terminal work.

The CLI Adapter study is future work only. A missing Desktop capability remains
`BLOCKED` in the current release.

## Other planned extensions

### 1. Executable coordination helper

Explore a small helper for the parent-owned task ledger, `task_id`/`thread_id`
correlation, duplicate delivery handling, and explicit integration gates. It
must not replace the Codex Desktop host.

### 2. Protocol simulator

Explore a deterministic state-machine simulator for out-of-order reports,
duplicate events, missing delivery, blocked routing, review-source validation,
and terminal-result transitions. The simulator would validate the abstract
protocol, not prove that every host exposes the same events.

### 3. Stable Desktop host integration

Explore adapters for project discovery, task creation, post-creation identity
and title verification, sidebar visibility, parent reply routes, completion
events, and bounded event waiting when host interfaces become stable.

### 4. Concurrency controller

Explore an optional controller for the six-window ceiling, task independence,
host capacity, and duplicate-context cost. The user-adjustable hard ceiling
must remain explicit.

### 5. Report and review-source tooling

Explore schema validation for worker reports, `review_source` existence checks,
stale-artifact detection, and machine-readable parent-ledger snapshots.

### 6. Durable state and recovery

Explore optional continuation records and recovery procedures for interrupted
parent tasks. These remain optional and do not become mandatory dependencies.

### 7. Release automation

Explore a release check for public-file discovery, private-state exclusion,
license presence, multilingual links, reference integrity, title-contract
coverage, and reproducible validation output.

### 8. Review-model diversity guidance

Document practical policies for Luna Max routine downstream work and Sol or
another configured reviewer for security, architecture, concurrency,
data-integrity, and release-critical review. User and project overrides remain
authoritative.
