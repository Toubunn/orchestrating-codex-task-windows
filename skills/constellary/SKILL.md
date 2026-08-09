---
name: constellary
description: Use when coordinating implementation, review, or investigation across multiple independent Codex Desktop task windows while one parent task retains architecture, integration, and user communication.
---

# Constellary

## Overview

Constellary `v2.0.0-alpha` is a compact recipe for parent-led coordination
across visible Codex Desktop task windows. An independent Codex task has its
own context and lifecycle; it is not a subagent. A worker may use subagents
internally, but the parent retains architecture, integration, user communication,
authoritative state, and final claims. The stable target is `v2.0.0`; install
the `constellary` Skill and invoke it as `$constellary`.

The workflow depends on capabilities, not on a named product; use the strongest
suitable option already available and state limitations honestly. The absence of an optional planning or durable-state capability does not block an otherwise authorized task. Multiple independent tasks run like stars while the parent organizes them into a meaningful constellation.

## Codex Desktop runtime contract

The v2 executable coordination surface is Codex Desktop only. Set
`coordination_surface: codex_desktop` and deterministic `desktop_required`.
Resolve the current registered project, require host `create_thread`, and
create the task in the same registered Codex project. Use `list_threads`,
`read_thread`, `wait_threads`, and `send_message_to_thread` for verification,
event-driven waiting, and report communication. Include the policy-approved
prompt, title, project, execution environment, model, and reasoning settings.

Post-creation, verify `thread_id`, `project_id`, `host_id`, actual `title`, and
sidebar visibility. A title, project, or visibility mismatch blocks acceptance.

### Missing Desktop capability

If any mandatory Desktop capability is absent, mark the dispatch BLOCKED. No CLI fallback is allowed. Forbidden substitutes are `codex`, `codex exec`,
`codex.exe`, PowerShell, `pwsh`, `cmd`, Windows Terminal, `Start-Process`,
`subprocess`, a background shell, a temporary prompt or report file, and an
internal-only agent. A future CLI adapter is separate explicit opt-in work.

## Downstream title protocol

Use the deterministic schema:

`Constellary · <TaskID> · <Role> · <ShortGoal>`

The host title budget is 34 NFC-normalized Unicode code points. Apply Unicode normalization (NFC),
collapse whitespace, and deterministically compress the short goal
before creation while preserving identity, task ID, and role. Do not rely on
implicit host truncation. Compare the actual title after creation; a mismatch
is BLOCKED. The compact example is `Constellary · T01 · 实现 · Desktop适配`.

Downstream tasks are sidebar-visible peers linked by creator task,
`source_thread_id`, task ledger, report route, and same registered project. A
worker-internal mechanism is not the primary downstream-task mechanism.
`T01-R1`, `T01-F1`, and `T01-R2` identify review, repair, and re-review.

## Execution environment mapping

`coordination_surface: codex_desktop` is mandatory for v2. Keep file execution
separate as `execution_environment: auto_safe`: Local for a prepared isolated
copy or serialized single writer, Worktree for concurrent Git writers or overlap
risk. A user may override this environment choice; it affects only Local,
Worktree, or serialized execution and never changes the same-project Desktop
coordination target. Without safe isolation, serialize or mark BLOCKED.

## When to use

Use it when two or more bounded implementation, investigation, or review
responsibilities benefit from fresh context, separate accountability, or
independent verification. Keep work in the current task when it is tightly
coupled, needs frequent shared edits, or cannot be given clear authority,
paths, acceptance criteria, and checks. Do not use independent tasks to avoid
a user decision or turn every small change into coordination overhead.

## Roles and authority

### Parent coordinator

The parent is the sole owner of authoritative coordination state. It defines
briefs, creates tasks, supplies the immediate coordinator and report channel,
preserves constraints, verifies evidence, dispatches fresh reviewers, and
integrates approved work. An optional root is supplemental and cannot replace
the immediate coordinator or report channel. `source_thread_id` identifies the
creator, not the current task; workers report updates to the parent and do not
redefine authority or release decisions.

### Implementation worker

The worker owns one bounded deliverable and its internal method. It stays in
scope, verifies checks, and actively sends one structured terminal report before
ending. A result left only in the worker task is not delivered. Missing
authority or a required user decision is `NEEDS_CONTEXT` or `BLOCKED`, not a
silent scope expansion.

### Independent reviewer

The reviewer is a fresh independent reviewer task, separate from implementation,
and read-only by default. It evaluates the original brief and actual artifact,
then returns reproducible `APPROVED` or `CHANGES_REQUIRED`. Repair is a separate
bounded task followed by fresh review; a reviewer does not edit files to pass.

## Runtime default

Invoking this Skill accepts `gpt-5.6-luna` with `max` reasoning for every
downstream role, including reviewers. A current user instruction or project
configuration overrides either value without a repeated confirmation prompt;
do not silently promote the reviewer.

```yaml
worker_defaults:
  model: gpt-5.6-luna
  reasoning: max
  environment: auto_safe
```

Record runtime evidence as `requested` (values sent), `accepted` (creation
succeeded without a reported replacement), or `observed` (host exposure or
independent verification). `accepted` alone does not prove `observed`; report
substitutions or uncertainty honestly.

## Dispatch and collect

Concurrency is bounded before dispatch: at most six downstream windows, seven
total including the parent. The user may adjust the limit, but the active limit
is a hard ceiling and must never be exceeded. Start another batch only after the
current batch ends.

For each task, follow one parent-owned flow:

1. Bound goal, authority, paths, dependencies, acceptance criteria, and checks.
2. Resolve the current registered Codex project; every downstream task is
   created in that same project. The execution environment may be Local or
   Worktree according to the safety policy and user override.
3. Register `task_id` before creation in at least this task ledger:

```yaml
task_id: TASK-001
thread_id: CREATED_THREAD
project_context: CURRENT_PROJECT
role: implementation
depends_on: none
status: active
report_received: false
review_source: pending
review_verdict: pending
```

4. Create through the host, verify project context, title, thread, host, and
   sidebar visibility, and use the host-created implicit reply-to-source route.
   If project selection or verification fails, stop; do not dispatch.
5. Let workers own their method; wait for task/message events. The parent does not routinely poll unchanged workers.
6. Arrival order does not determine ownership. The parent matches every message and completion event by task_id and thread_id, then deduplicate a matching completion event in the same ledger row.
7. Dispatch a fresh reviewer only after its artifact is accessible through
   `review_source`; integrate only after reviewer and parent verification pass.

The worker actively sends one terminal report. Whichever matching report or
completion event arrives first wakes the parent; it records one result and
deduplicates the other. Neither mechanism permits routine polling. If delivery
or event-driven collection is unavailable, mark `BLOCKED`.

Terminal `status` and review `verdict` are separate. Before integration verify
report delivery and routing, changed paths or none, required checks and evidence; verify review verdict, blockers and remaining concerns, and runtime claim evidence level.

## Review handoff

Give the reviewer the original criteria, required checks, and actual artifact
through `review_source`; implementer's reasoning is not required. A
`shared_workspace` source means serialized implementation then read-only review;
`worktree`, `commit`, `branch`, `handoff`, or `diff` sources must contain the
implementation. A missing or stale source is `BLOCKED`; never review baseline.

## Escalation and safety

Escalate unresolved scope, ownership, privacy, destructive risk, release
authority, or materially different outcomes. Live user constraints outrank
fallback preferences. If the user forbids file creation, use the current task context instead of a project-local record. Apply explicit overrides without a repeated confirmation prompt.

Inspect granted authority before escalation; full access forbids redundant
approval requests. Command failure alone does not prove missing permission;
diagnose the command and environment first. Without explicit authorization,
workers do not merge, push, publish, change remotes, edit unrelated files, or
make release claims. Public Skill files contain no local paths, live IDs,
secrets, private state, or local planning dependencies.

## References

- [Task and report contracts](references/task-contracts.md) — read before
  creating a task or formatting a terminal report.
- [Capability fallbacks](references/capability-fallbacks.md) — read when
  selecting state, messaging, project, or isolation behavior.
