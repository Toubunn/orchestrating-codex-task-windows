# Orchestrating Codex Task Windows

- 🇬🇧 [English](README.md)
- 🇯🇵 [日本語](README.ja.md)
- 🇨🇳 [简体中文](README.zh-CN.md)

This repository contains the `orchestrating-codex-task-windows` Skill for coordinating bounded work across visible, context-isolated Codex task windows.

## Scope

This is a Codex-only v1. An independent task is a separate, visible Codex window with its own context and lifecycle; it is not the same thing as a worker-internal subagent. A worker may use subagents internally, while the parent coordinates independent tasks and owns architecture, integration, user communication, and final claims.

## Install

Copy the single directory `skills/orchestrating-codex-task-windows/` into the Codex skills directory. The repository-level tests and validation script are for maintainers; the Skill itself remains independently installable.

## Examples

Start with the same minimal example in the language you prefer:

- 🇬🇧 [English minimal orchestration example](examples/minimal-orchestration.en.md)
- 🇯🇵 [日本語の最小オーケストレーション例](examples/minimal-orchestration.ja.md)
- 🇨🇳 [简体中文最小编排示例](examples/minimal-orchestration.zh-CN.md)

The three examples link to one another. Future extensions are tracked in
[FUTURE_WORK.md](FUTURE_WORK.md).

## Runtime defaults

All downstream roles, including implementation workers and independent reviewers, default to Luna Max: `gpt-5.6-luna` with `max` reasoning. A current user instruction or project configuration may override the model, the reasoning level, or both for any role without a repeated confirmation prompt.

Luna Max is suitable for bounded, routine review. For security, architecture, concurrency, data-integrity, or release-critical review, the user or project configuration may select Sol or another stronger configured reviewer. The Skill never promotes a reviewer automatically when nobody requested or configured an escalation. When the host exposes the effective runtime, the parent should record it and report any substitution honestly.

Implementation and review use different fresh independent tasks. Review is read-only by default and any repair is dispatched as a new bounded implementation task.

## Choosing direct Sol or orchestration

Use a direct Sol task when the change is small, tightly coupled, or requires
continuous architectural judgment. Use this Skill when two or more bounded
responsibilities can be completed independently, such as implementation,
testing, documentation, or separate investigations.

For security, architecture, concurrency, data-integrity, or release-critical
work, a practical hybrid is a Sol parent or reviewer with Luna Max workers. The
six-downstream-window limit is a ceiling, not a target; start with only the
independent workers that the task genuinely needs.

## Reports, event waits, and polling

These three ideas are different:

- **Worker report:** the structured result a worker or reviewer actively sends to its immediate coordinator when it finishes or is blocked. It carries the work result, changed paths, checks, evidence, blockers, concerns, and uncertainty.
- **Event wait:** the parent sleeps until a relevant message or completion, blocker, failure, or user event wakes it. The parent can wait across its active tasks instead of watching them continuously.
- **Polling:** repeatedly opening or inspecting unchanged child tasks to see whether anything changed. Routine polling is forbidden by the Skill.

Use the report and event wait together: the worker sends its report, while the parent waits for the matching activity. A matching completion event that arrives first only wakes the parent; it does not mean that the structured report has been received or validated. Only after the parent validates the matching structured report does it mark `report_received` (report received). If the structured report arrives first, a later matching completion event is the second delivery and is deduplicated. In either order, each task records one terminal result; the matching delivery through the other route cannot create a second result.

## Projects and child tasks

An independent child task uses the parent's registered Codex project by default. A worktree is an isolated workspace inside that same project; it does not make the child projectless. Projectless execution is limited to genuinely no-file work or an explicit user request.

After creating a child, the coordinator verifies its project context. If the intended project cannot be selected or verified, the coordinator stops before dispatch and does not silently create a projectless window.

When several children run at once, the parent pairs each `task_id` with its `thread_id` in the task ledger. Message order does not decide ownership. Reports and completion events are matched by those identifiers; an active report plus its matching completion event produces one terminal result, not two.

By default, the parent runs no more than six downstream windows at the same
time, which means seven active windows total when the parent is included. The
user may choose a different limit, but the current limit is a hard ceiling and
must never be exceeded. If more tasks remain, finish the current batch before
starting the next batch.

The source address received by a child is its parent's address, not the child's own address. A child that later creates another task must not copy that incoming address and pretend it is its own; the host's reply route is the default, and a direct address is used only when the coordinator's exact address is confirmed by the host.

## Review artifacts and capability fallbacks

The reviewer receives the original goal, acceptance criteria, required checks, and a concrete `review_source` for the actual artifact. That source may be the current shared workspace or an isolated worktree, commit, branch, handoff, or diff. The reviewer does not need the implementer's reasoning or self-assessment and must not review an inaccessible or stale baseline.

Every worker must send a structured terminal report to its immediate coordinator before ending. A result left only in the worker task is not delivered.

Planning, durable state, messaging, Git, and worktree isolation are optional capabilities. The workflow uses the strongest available capability, then an ordinary project-local record, then short-lived task context. Reduced continuity or isolation is reported honestly; it does not become an excuse to invent dependencies or silently change scope.

Minimal usage:

```text
Use $orchestrating-codex-task-windows to split this project into independent implementation and review tasks, collect each required report, and keep final integration in the parent task.
```

## Safety boundary

The Skill does not automatically merge, push, publish, create or change remotes, perform destructive cleanup, or make final release claims. Those actions remain subject to explicit authority and parent-owned verification.

When the system already grants full access, a child must not ask for permission again. A command failure by itself is not a permission problem: check the command, working directory, absolute path, quoting, shell, and process startup first. Ask only when the task truly needs authority that has not already been granted.

## Validate

Run the deterministic contract and hygiene checks from the repository root:

```text
python -B scripts/validate_package.py
```

The checks cover Skill contracts, machine-specific paths, live task or project identifiers, secret-shaped values, unresolved authoring markers, broken Skill references, and packaged cache artifacts.

## Licensing

This repository is released under the [MIT License](LICENSE).
