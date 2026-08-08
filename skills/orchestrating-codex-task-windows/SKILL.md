---
name: orchestrating-codex-task-windows
description: Use when coordinating implementation, review, or investigation across multiple independent Codex task windows while one parent task retains architecture, integration, and user communication.
---

# Orchestrating Codex Task Windows

## Overview

This Skill is a compact recipe for parent-led coordination across independent
Codex task windows. An independent Codex task is a separate visible task
window with its own context and lifecycle; it is not a subagent. A worker may
use subagents internally, but that choice does not change report ownership.
The parent retains architecture, integration, user communication, authoritative
coordination state, and final claims. The workflow depends on capabilities, not
on a named product: use the strongest suitable option already available and
state limitations honestly. The absence of an optional planning or durable-state capability does not block an otherwise authorized task.

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
bounded briefs, creates independent tasks, supplies the immediate coordinator
and report channel, preserves user and project constraints, verifies evidence,
dispatches fresh reviewers, integrates approved work, and makes final claims.
The task that creates a worker is its immediate coordinator; every worker
reports to that direct coordinator. An optional root may receive a supplemental
notification, but it cannot replace the immediate coordinator or report
channel. In a delegation envelope, an incoming machine-provided
`source_thread_id` identifies the task that created the current task, not the
current task itself. A nested coordinator never copies that parent or root ID
into a child brief as its own coordinator ID. Workers report updates to the
parent and do not redefine goal, authority, paths, acceptance criteria, or
release decisions.

### Implementation worker

The worker owns its internal method and one bounded deliverable. It stays
within the assigned authority and write scope, verifies the required checks,
and actively sends one structured terminal report before ending. A result left only in the worker task is not delivered. Incomplete authority or a required
user decision is reported as `NEEDS_CONTEXT` or `BLOCKED`, not silently broadened.
When a send tool requires an ID, the worker uses the exact machine-provided
source ID in its own envelope, never a manually copied or guessed brief value.

### Independent reviewer

The reviewer is a fresh independent reviewer task, separate from implementation, and is
read-only by default. It evaluates the original brief and actual artifact,
then returns a reproducible `APPROVED` or `CHANGES_REQUIRED` verdict. Repair is
a separate bounded implementation task followed by fresh review; a reviewer
does not edit files merely to make its own verdict pass.

## Runtime default

Invoking this Skill accepts `gpt-5.6-luna` with `max` reasoning as the default
for every downstream role, including independent reviewers. A current user
instruction or project configuration overrides either value without a repeated confirmation prompt. Do not silently promote the reviewer model.

```yaml
worker_defaults:
  model: gpt-5.6-luna
  reasoning: max
  environment: worktree_when_writing
```

Record runtime evidence at its highest supported level: `requested` means the
values sent, `accepted` means creation succeeded without a reported
replacement, and `observed` means the host explicitly exposed or independently
verified the effective runtime. `accepted` alone does not prove `observed`;
report substitutions or uncertainty honestly.

## Dispatch and collect

Concurrency is bounded before dispatch. By default, run at most six downstream
windows at once, seven total including the parent. The user may adjust the
limit, but the active limit is a hard ceiling and must never be exceeded. If
more work remains, start another batch only after every task in the current
batch has ended.

For each task, follow one parent-owned flow:

1. Bound the goal, authority, paths, dependencies, acceptance criteria, and
   required checks.
2. Resolve the current Codex project. A child defaults to the same registered
   project as its parent. Genuinely no-file work or an explicit user request
   may be projectless; otherwise a project cannot be silently omitted.
3. Register the task by `task_id` before creation. Keep at least this task ledger:

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

4. Create the independent task, verify its project context after creation, and
   record its `thread_id`. Use the host-created implicit reply-to-source route
   by default; use a direct coordinator ID only when this coordinator's own ID
   is machine-confirmed and passed verbatim. If the parent cannot select or
   verify the current project, stop; do not silently create a projectless task.
5. Let the worker own its internal method; do not micromanage worker-internal
   subagents.
6. Wait on task and message events. The parent does not routinely poll
   unchanged workers.
7. Arrival order does not determine ownership. The parent matches every message and completion event by task_id and thread_id; multiple children are never mixed by return or completion order. Accept the worker's active structured report, then deduplicate a matching completion event in the same ledger row.
8. Dispatch a fresh reviewer only after its implementation artifact is
   accessible through a concrete `review_source`.
9. Integrate only after the review verdict and parent verification pass.

The single completion rule is: the worker actively sends one terminal report
to its immediate coordinator; the parent may receive a matching completion
event; whichever arrives first wakes the parent; the parent records one
terminal result and deduplicates the other; neither mechanism permits routine
polling. If neither direct delivery nor event-driven collection can deliver a
result, the task is `BLOCKED`.

Terminal `status` and review `verdict` are separate. Worker statuses are
`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; a review verdict
is `APPROVED` or `CHANGES_REQUIRED`. A terminal report states work completed,
changed paths or `none`, required checks and evidence, blockers, remaining
concerns, and uncertainty. Before integration, verify report delivery and routing, changed paths or none, required checks and evidence, review verdict, blockers and remaining concerns, and runtime claim evidence level.

## Review handoff

Give the reviewer the original goal and acceptance criteria, required
verification, and the actual artifact through `review_source`. The reviewer
does not need the implementer's reasoning, intermediate attempts, or
self-assessment. `files_changed` and the worker report are locators and claims,
not proof. A `shared_workspace` source means serialized implementation then
read-only review of current files; an isolated `worktree`, `commit`, `branch`,
`handoff`, or `diff` source must contain the implementation. A missing, stale,
or inaccessible source is `BLOCKED`; never review the untouched baseline.

## Escalation and safety

Escalate when scope, ownership, privacy, destructive risk, release authority,
or a materially different user outcome is unresolved. Live user constraints
outrank fallback preferences. If the user forbids file creation, do not create
a project-local status or coordination file merely for record keeping; use the
current task context instead. Apply an explicit runtime override without a
repeated confirmation prompt.

Before escalating authority, inspect the granted permission profile. Full or
unrestricted access forbids a redundant elevation or approval request. A
command failure alone does not prove missing permission: first diagnose the
working directory, absolute path, quoting, shell, command availability, and
process startup. Ask only for new authority that is actually absent and needed.

Unless explicitly authorized, workers do not merge into the canonical branch,
push or publish, create or change remotes, modify unrelated files, perform
destructive cleanup, or make final release claims. Concurrent writers must not
overlap paths in one shared directory. Public Skill files contain no local
paths, live task identifiers, secrets, private transcripts, or dependencies on
local planning or memory products. The parent verifies important reports
against workspace or host evidence before integrating or claiming completion.

## References

- [Task and report contracts](references/task-contracts.md) — read before
  creating a task or formatting a terminal report.
- [Capability fallbacks](references/capability-fallbacks.md) — read when
  selecting state, messaging, project, or isolation behavior.
