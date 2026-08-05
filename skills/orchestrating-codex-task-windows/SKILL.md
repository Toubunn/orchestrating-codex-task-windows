---
name: orchestrating-codex-task-windows
description: Use when coordinating implementation, review, or investigation across multiple independent Codex task windows while one parent task retains architecture, integration, and user communication.
---

# Orchestrating Codex Task Windows

## Overview

This Skill helps a parent Codex task split a project into bounded implementation, review, or investigation work for fresh independent Codex task windows. Each worker receives a self-contained contract, works within an explicit scope, and actively returns a structured result to the parent before ending.

The first release is Codex-specific. It teaches coordination between visible, context-isolated task windows while keeping the parent responsible for architecture, integration, user communication, and final claims.

## When to use

Use this Skill when a project has two or more bounded responsibilities that benefit from fresh context, separate ownership, or independent review. It is especially useful when implementation and verification should be performed by different tasks, or when workers can proceed without sharing mutable coordination state.

Do not use it to turn every small change into a separate task. Do not use it to delegate a decision that belongs to the user or to avoid parent-owned integration and final verification.

## Core distinction: independent tasks, not subagents

An independent Codex task is a separate, visible task window with its own context and lifecycle. It is not a subagent. The parent creates it for one bounded responsibility and receives its result through the explicit reporting channel in the task contract.

A subagent is an internal worker used inside another task. A worker owns its internal method and may use subagents when useful; the parent does not micromanage that internal choice or require an inventory of worker-internal subagents. Independent task coordination and subagent management are different layers.

Create an independent task when fresh context, separate accountability, non-overlapping ownership, or an independent review is needed. Keep work in the current task when the work is tightly coupled, needs frequent shared edits, or cannot be given a bounded acceptance criterion.

## Parent coordinator

The parent coordinator owns the project-level decisions and the final user relationship. It:

- decomposes the project into bounded tasks and creates fresh independent tasks;
- provides each task with a role, goal, immediate coordinator identifier, project root, allowed write paths, forbidden actions, acceptance criteria, verification requirements, and coordinator report channel;
- owns architecture, authoritative coordination state, user communication, optional durable-state curation, integration, final verification, and final claims;
- records the effective worker runtime when the host exposes it and reports any substitution honestly;
- dispatches a fresh independent reviewer after implementation and routes any repair through a new implementation task;
- asks the user for decisions that exceed delegated authority.

The parent does not continuously supervise worker activity. After dispatch, it performs useful parent-owned work or waits for worker events.

The task that creates a worker is that worker's immediate coordinator. Every worker reports to that direct coordinator. An optional root task may receive a notification, but it cannot replace the immediate coordinator or its report channel.

## Implementation worker

An implementation worker receives one bounded deliverable and an explicit delivery contract. It may choose its own implementation method, including any worker-internal subagent use, as long as it stays within the assigned authority and write scope.

The worker verifies the acceptance criteria, keeps project-level coordination state under the parent’s ownership, and actively reports a terminal result to the parent. Forced completion and blocking have the same delivery rule: send the parent report before ending the task. A result left only in the worker task is not delivered.

If the worker discovers that the brief is incomplete or a user-owned decision is required, it reports `NEEDS_CONTEXT` or `BLOCKED` with evidence instead of silently broadening the task.

## Independent reviewer

Review is performed by a fresh independent reviewer, separate from the implementation task. The reviewer evaluates the assigned changes against the brief and returns a reproducible verdict; it does not treat the implementer’s conclusions as proof.

Review is read-only by default. If changes are required, the parent dispatches a separate bounded repair task and then requests another fresh independent review. A reviewer does not modify implementation files merely to make its own review pass.

## Runtime defaults

The shipped worker settings are configurable defaults:

```yaml
worker_defaults:
  model: gpt-5.6-luna
  reasoning: max
  environment: worktree_when_writing
```

Project configuration or current user instructions may override these values without a repeated confirmation prompt. The coordinator records the effective runtime when evidence is available. It must not claim that Luna Max was used when the host substituted another runtime or did not expose the runtime.

If the requested runtime cannot be created and substitution would change the user's intent, the parent asks the user. Otherwise, the parent reports the mismatch and continues only within the authority already granted.

Runtime claims use three evidence levels:

- `requested` — the values sent in the task-creation request;
- `accepted` — the host accepted creation and did not report a replacement;
- `observed` — the host explicitly echoed the effective runtime or it was independently verifiable after creation.

`accepted` alone does not prove `observed`. Only claim an actual runtime as observed when the host provides that evidence; otherwise report the highest supported level and any uncertainty.

## Dispatch workflow

1. Define the bounded goal, role, dependencies, allowed write paths, forbidden actions, acceptance criteria, and verification commands.
2. Map the task to an environment. For a no-file task, prefer projectless execution. For a file-writing task, prefer `worktree_when_writing`; this is a preference, not a prerequisite. If a worktree is unavailable, use an isolated copy, non-overlapping write paths, or serialized execution.
3. Create a fresh independent Codex task for each implementation, investigation, or review role. Include the immediate coordinator task identifier and coordinator report channel in every brief. Add root task and root notification fields only when an optional root notification is useful.
4. Apply the runtime defaults unless the project or current user request already supplies an override. Record the effective runtime when the host exposes it.
5. Let the worker own its internal method. Do not extend the brief into micro-management of worker-internal subagents.
6. Wait for the worker’s completion, blocker, failure, or context event. Collect the required report and verify important claims against the workspace or host state.
7. For implementation work, dispatch a fresh independent reviewer. Integrate only after the required review and parent-owned final verification pass.

Read [task and report contracts](references/task-contracts.md) before dispatching a task. Read [capability fallback rules](references/capability-fallbacks.md) at the start of coordination and whenever a required capability is missing or changes.

## Planning and memory boundaries

The parent owns the project’s authoritative coordination state. It records the project goal and phase, dispatched tasks and roles, allowed scopes, dependencies, status, report receipt, blockers, review verdicts, decisions, and next action. Workers report changes to the parent instead of editing that state directly.

A worker may keep a worker-local execution plan for its own bounded task when useful. It cannot redefine the goal, authority, write scope, or acceptance criteria, and it does not need continuous synchronization with the parent. Summarize worker-local information in the final report only when the parent needs it for continuation or integration.

Durable state is reserved for stable facts that matter beyond the current task, such as durable constraints, architectural decisions, or reliable continuation pointers. Routine progress, temporary status, test output, volatile identifiers, and facts already authoritative in project files remain task-local or project-local. Workers do not write project-level durable state by default; they report potentially durable facts for the parent to curate.

Use the strongest suitable capability already available, then an ordinary project-local record, then the current task context for short-lived work. Reduced continuity must be reported honestly, but the absence of an optional planning or durable-state capability does not block an otherwise authorized task.

## Event-driven waiting

The parent waits for events rather than repeatedly inspecting unchanged workers. It does not routinely poll. Parent activity resumes when a worker reports completion, a blocker, or a request for context; when the host reports task failure; or when the user sends a new instruction.

If direct task-to-task messaging is unavailable, follow the bounded fallback in the capability reference: the worker leaves a structured final result visible, and the parent performs one bounded collection check. This fallback is not permission for routine polling, and a worker that knows delivery failed must not claim normal completion.

## Direct coordinator and report routing

Resolve the report route in this order:

1. Use the explicit direct coordinator ID and coordinator report channel from the task brief.
2. If those are unavailable, use the host implicit reply-to-source route to the task that created the current window.
3. After a completion event, let the direct coordinator perform one bounded collection of the worker's visible result when needed.

If neither a completion event nor a collectable result exists, the delivery must be marked `BLOCKED`; do not present it as a normal completion. If only a root channel is available and no direct coordinator channel can be established, mark the route as `degraded routing` and must not claim direct delivery to the coordinator. A root notification is supplemental, not a substitute for direct delivery.

## Completion and reporting

Every worker must send one terminal report through the channel in its contract before ending. The allowed terminal statuses are exactly `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`. A completion report includes work completed, files changed, verification, evidence, blockers, remaining concerns, and uncertainty.

The parent treats a report as delivered only after it receives the message or verifies the documented fallback. A result left only in the worker task is not delivered. The parent then updates authoritative coordination state, verifies the evidence, and decides whether to integrate, repair, escalate, or stop.

Terminal `status` and review `verdict` are separate fields. A review verdict is `APPROVED` or `CHANGES_REQUIRED`; neither value is a terminal status.

Before integration or a final claim, the parent verifies at minimum:

- report delivery and routing;
- changed paths or `none`;
- required checks and evidence;
- review verdict;
- blockers and remaining concerns;
- runtime claim evidence level.

## Review and repair loop

Use this bounded loop:

1. Parent dispatches an implementation worker.
2. Worker sends a terminal report with reproducible evidence.
3. Parent dispatches a fresh independent reviewer.
4. Reviewer returns `APPROVED` or `CHANGES_REQUIRED` with evidence.
5. If changes are required, parent dispatches a bounded repair task.
6. A fresh reviewer checks the repaired scope.
7. Parent integrates only after the required review and final verification pass.

Review findings must be reproducible and tied to acceptance criteria. Record environmental limitations separately from implementation defects, and do not reopen the same issue under new wording without new evidence. Ask the user when risk tolerance or release timing, rather than implementation evidence, is the unresolved decision.

## Escalate to the user

The parent asks the user when requirements admit materially different outcomes, scope or ownership is ambiguous, or a decision changes cost, release authority, privacy, destructive risk, external state, or the user’s intent. The parent also asks when the available evidence cannot support a safe architectural choice.

Ordinary implementation details within an approved brief do not require user confirmation. Workers must not make final product, release, publication, cost, privacy, or risk decisions on the user's behalf.

Live user constraints outrank fallback preferences. If the current user forbids file creation, do not create a project-local status or coordination file merely for record keeping; use the current task context instead. If the current request explicitly overrides a runtime default, apply that override without a repeated confirmation prompt.

## Safety boundaries

Unless the user explicitly authorizes otherwise, worker tasks do not merge into the canonical branch, push or publish, create or change remotes, modify unrelated files, perform destructive cleanup, or make final user-facing release claims. The parent verifies important task reports against the workspace or host state before integrating or claiming completion.

This first release supports Codex independent task windows only. Planning, durable state, Git, worktrees, and messaging are capability-based enhancements, not named product requirements. Public Skill files must remain reusable: do not embed developer-specific paths, usernames, live task identifiers, secrets, or local repository details.

## References

- [Task and report contracts](references/task-contracts.md) — read before creating a worker task and before formatting a terminal report.
- [Capability fallbacks](references/capability-fallbacks.md) — read when selecting state, messaging, or isolation behavior.
