# Changelog

## v2.0.0-alpha — Constellary migration history

- Renamed the public Skill from `orchestrating-codex-task-windows` (display name
  “Orchestrating Codex Task Windows”) to `Constellary`, with slug `constellary`
  and invocation `$constellary`.
- Made Codex Desktop the only executable v2 coordination surface and recorded
  the breaking change from the prior v1 contract.
- Added same-project host verification, deterministic 34-code-point NFC title
  normalization/compression, sidebar visibility evidence, explicit lineage
  titles, and BLOCKED behavior when Desktop capabilities are unavailable.
- Added matching release summaries to all three READMEs, multilingual example
  updates, all-public-file privacy checks, a 79-test validation suite, and a
  concrete future CLI Adapter backlog. CLI is not supported in `v2.0.0`.

## 2026-08-08

- Added the MIT license.
- Added Japanese and Simplified Chinese README translations with cross-links.
- Added English, Japanese, and Simplified Chinese minimal orchestration examples with cross-links.
- Added `FUTURE_WORK.md` for optional runtime helpers, a protocol simulator, host integration, and other post-v1 ideas.
- Clarified the `review_source` vocabulary, including `copy` and `handoff`, while keeping execution environments separate from artifact sources.
- Hardened package discovery so untracked public files are included in hygiene checks.

## 2026-08-06

This is the first public change-history entry for the Codex-only v1 documentation. It records the refinement; it does not claim installation, deployment, or publication.

- Refined multi-worker correlation and deduplication.
- Combined active worker reports with event-driven waiting.
- Added same-project child-task defaults and verification.
- Added explicit review artifact sources.
- Clarified Luna Max reviewer defaults and user overrides.
- Documented sanitized behavior evidence.
- Added a user-adjustable concurrency ceiling: six downstream windows by
  default, seven total with the parent, with later batches waiting for the
  current batch to finish.
- Recorded fresh Luna Max refinement evidence for out-of-order multi-worker
  correlation, shared artifact review, isolated worktree handoff, and
  same-project child creation without claiming independently observed effective
  runtime.
