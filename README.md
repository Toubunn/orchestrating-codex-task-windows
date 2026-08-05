# Orchestrating Codex Task Windows

This repository contains the `orchestrating-codex-task-windows` Skill for coordinating bounded work across visible, context-isolated Codex task windows.

## Scope

This is a Codex-only v1. An independent task is a separate, visible Codex window with its own context and lifecycle; it is not the same thing as a worker-internal subagent. A worker may use subagents internally, while the parent coordinates independent tasks and owns architecture, integration, user communication, and final claims.

## Install

Copy the single directory `skills/orchestrating-codex-task-windows/` into the Codex skills directory. The repository-level tests and validation script are for maintainers; the Skill itself remains independently installable.

## Runtime defaults

Worker tasks use a configurable Luna Max default: `gpt-5.6-luna` with `max` reasoning. Project configuration or current user instructions may override that default without a repeated confirmation prompt. When the host exposes the effective runtime, the parent should record it and report any substitution honestly.

Implementation and review use different fresh independent tasks. Review is read-only by default and any repair is dispatched as a new bounded implementation task.

## Reporting and capability fallbacks

Every worker must send a structured terminal report to the parent before ending, including completion, blocker, verification, evidence, remaining concerns, and uncertainty. A result left only in the worker task is not delivered.

Planning, durable state, messaging, Git, and worktree isolation are optional capabilities. The workflow uses the strongest available capability, then an ordinary project-local record, then short-lived task context. Reduced continuity or isolation is reported honestly; it does not become an excuse to invent dependencies or silently change scope.

Minimal usage:

```text
Use $orchestrating-codex-task-windows to split this project into independent implementation and review tasks, collect each required report, and keep final integration in the parent task.
```

## Safety boundary

The Skill does not automatically merge, push, publish, create or change remotes, perform destructive cleanup, or make final release claims. Those actions remain subject to explicit authority and parent-owned verification.

## Validate

Run the deterministic contract and hygiene checks from the repository root:

```text
python -B scripts/validate_package.py
```

The checks cover Skill contracts, machine-specific paths, live task or project identifiers, secret-shaped values, unresolved authoring markers, broken Skill references, and packaged cache artifacts.

## Licensing

This repository does not choose a license. A license will be added only after the repository owner selects one.
