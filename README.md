# Constellary

- 🇬🇧 [English](README.md)
- 🇯🇵 [日本語](README.ja.md)
- 🇨🇳 [简体中文](README.zh-CN.md)

Constellary is a Codex Skill for coordinating bounded work across independent,
visible Codex Desktop tasks. Multiple independent tasks run like stars, each on
its own, while the parent task organizes them into a meaningful constellation.
The approved Chinese wording is: 多个独立任务像星星一样各自运行，由上级任务把它们组织成一个有意义的星群。

This candidate is `v2.0.0-alpha`; the intended stable target is `v2.0.0`.
The public Skill slug is `constellary`, and the invocation is `$constellary`.

## What's new in v2.0.0-alpha

- **Breaking rename:** the project and Skill are now Constellary. Use
  `$constellary` and install `skills/constellary/`; the previous public name and
  invocation are retained only in the migration record.
- **Real Desktop downstream tasks:** `coordination_surface: codex_desktop` and
  `desktop_required` require the parent to create separately visible tasks in
  the same registered Codex project. Missing host capabilities produce
  `BLOCKED`, never a terminal or CLI fallback.
- **Safer file execution:** `execution_environment: auto_safe` independently
  chooses Local, Worktree, or serialized execution from write risk. It does not
  change the Desktop coordination surface.
- **Predictable identity and hierarchy:** creation-time titles follow a
  deterministic 34-code-point protocol, while creator identity, task contracts,
  report routes, and parent-owned integration establish the logical hierarchy.
- **Explicit delivery and review:** workers send structured reports, the parent
  waits on host events, and each independent read-only review uses a fresh task;
  repairs use another bounded implementation task.
- **CLI kept separate:** [FUTURE_WORK.md](FUTURE_WORK.md) records a future,
  explicit opt-in CLI Adapter rather than mixing it into the Desktop workflow.
- **Publication hygiene:** validation scans every public regular file and path
  for machine-specific paths, identifiers, secret-shaped values, private state,
  old-name residue, broken links, malformed titles, and cache artifacts.
- **Release evidence:** the English, Japanese, and Simplified Chinese READMEs
  and examples describe the same contract, and 79 automated tests plus the
  package validator protect the candidate.

## Scope

Constellary v2 uses Codex Desktop as its only executable coordination surface.
An independent task is a separate visible task window with its own context and
lifecycle; it is not a worker-internal subagent. The parent owns architecture,
the task ledger, project context, integration, reports, and final claims.

The current policy is deterministic: `coordination_surface: codex_desktop` and
`desktop_required`. The parent resolves the current registered Codex project,
creates the downstream task through the host `create_thread` capability, then
verifies `thread_id`, `project_id`, `host_id`, the actual title, and sidebar
visibility. It waits with host events and communicates through the host thread.
If a mandatory Desktop capability is missing, the dispatch is `BLOCKED`.

There is no CLI fallback in v2. A terminal, `codex`, `codex exec`, `codex.exe`,
PowerShell, `pwsh`, `cmd`, Windows Terminal, `Start-Process`, subprocess,
background shell, temporary prompt file, or internal-only agent is not a
successful Desktop route.

## Install

Copy the single directory `skills/constellary/` into the Codex Skills
directory. The repository-level tests and validation script are for maintainers;
the Skill itself remains independently installable.

## Examples

Start with the same minimal example in the language you prefer:

- 🇬🇧 [English minimal orchestration example](examples/minimal-orchestration.en.md)
- 🇯🇵 [日本語の最小オーケストレーション例](examples/minimal-orchestration.ja.md)
- 🇨🇳 [简体中文最小编排示例](examples/minimal-orchestration.zh-CN.md)

The three examples link to one another. Future extensions are tracked in
[FUTURE_WORK.md](FUTURE_WORK.md).

## Title protocol

Every downstream task uses:

`Constellary · <TaskID> · <Role> · <ShortGoal>`

The host title budget is 34 NFC-normalized Unicode code points. Apply Unicode
normalization (NFC), collapse redundant whitespace, and deterministically compress
the short goal before creation. Preserve the project name, TaskID, and role;
verify the actual returned/displayed title after creation. Do not accept
implicit host truncation. A concrete compact title is
`Constellary · T01 · 实现 · Desktop适配`; reviewer, repair, and re-review titles
use `T01-R1`, `T01-F1`, and `T01-R2`.

## Runtime defaults

All downstream roles, including implementation workers and independent
reviewers, default to Luna Max: `gpt-5.6-luna` with `max` reasoning. A current
user instruction or project configuration may override the model, reasoning
level, or both for any role without a repeated confirmation prompt. The Skill
does not silently promote a reviewer.

Implementation and review always use different fresh independent tasks. Review
is read-only by default; any repair is a new bounded implementation task. A
sidebar-visible peer is logically correlated by creator identity, source thread,
project context, task ledger, and report route.

## Reports, event waits, and polling

Every worker actively sends one structured terminal report to its immediate
coordinator. A result left only in the worker task is not delivered. The parent
waits for matching messages, completion, blocker, failure, or user events and
does not routinely poll unchanged tasks. It correlates `task_id` and `thread_id`,
deduplicates a matching completion event, and keeps `report_received` separate
from the review verdict and `review_source`.

## Execution environment

Coordination and file execution are separate decisions. The public policy is
`execution_environment: auto_safe`: use Local for a prepared isolated copy or
serialized single-writer work, and Worktree for concurrent writers in a Git
repository or material overlap risk. A user may override the policy. If safe
isolation is unavailable, serialize or report `BLOCKED`.

## Future CLI adapter

CLI is not supported or executable in `v2.0.0`. [FUTURE_WORK.md](FUTURE_WORK.md)
records an explicit opt-in study for lifecycle supervision, cleanup, structured
report transport, identity correlation, concurrency, reviewer creation,
security, cross-platform behavior, and end-to-end verification. It must never
become an automatic Desktop fallback.

## Validation

Run the deterministic contract and hygiene checks from the repository root:

```text
python -B scripts/validate_package.py
```

The checks cover Skill contracts, multilingual links, machine-specific paths,
live task or project identifiers, secret-shaped values, unresolved authoring
markers, broken Skill references, old-name residue, and packaged cache
artifacts.

## License

This repository is released under the [MIT License](LICENSE).
