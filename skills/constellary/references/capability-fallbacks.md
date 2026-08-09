# Capability Fallbacks

The workflow depends on capabilities, not on a named planning, memory, Git, or messaging product. At each boundary, use the strongest suitable option already available:

```text
Existing suitable capability
→ ordinary project-local record
→ current task context for short-lived work
```

Report reduced continuity or isolation honestly. The loss of an optional capability may lower recovery or concurrency quality, but it does not block an otherwise authorized task.

## Codex Desktop adapter boundary

Constellary v2 has one executable coordination surface:
`coordination_surface: codex_desktop` with the `desktop_required` policy. The
parent resolves the same registered project, calls the host `create_thread`
capability, and verifies `thread_id`, `project_id`, `host_id`, actual title,
and sidebar visibility after creation. It waits through `wait_threads` and
communicates reports with `send_message_to_thread`.

If a mandatory Desktop capability is missing, the result is `BLOCKED`. The
workflow never silently or explicitly uses `codex`, `codex exec`, `codex.exe`,
PowerShell, `pwsh`, `cmd`, Windows Terminal, `Start-Process`, subprocess,
background shell, a temporary prompt/report file, or an internal-only agent as
a successful Desktop route. A future CLI Adapter must be separately opted into,
documented, and tested.

## Granted authority and command failures

Before attempting elevation, inspect the granted authority or permission profile. Under full/unrestricted access, do not request elevation or approval. Do not reconfirm authority already granted.

Command or process failure alone is not evidence of missing permission. First diagnose cwd, path, quoting, shell, and process startup, including command existence and an alternate ordinary launch method. Request user authority only when a new authority is actually missing and required by the task.

## Environment mapping

Every downstream task retains the current registered project, including no-file
work. The file execution environment may use Local or Worktree; for file-writing
work, `worktree_when_writing` is a preference, not a prerequisite. If no
worktree is available, choose an isolated copy, non-overlapping write paths, or
serialized execution according to the risk of concurrent edits, and mark the
dispatch BLOCKED when safe execution cannot be established.

## Parent planning boundary

The parent is the sole owner of authoritative coordination state. It records the project goal and phase, each task’s role and owner, allowed write scope, dependencies, status, report receipt, blockers, review verdicts, decisions, and next action.

Choose the strongest existing mechanism for that state. If no suitable mechanism exists, keep a small ordinary project-local record. If the information is short-lived and no project-local record is justified, keep it in the current parent task context. Workers report updates to the parent; they do not edit the parent’s authoritative record directly.

Do not replace a missing planning capability with repeated worker inspection. The parent can continue with a concise state record and event-driven waiting.

## Worker planning boundary

A worker may make a local execution plan when its assigned task is complex enough to need one. The plan covers only the worker’s task and cannot redefine the goal, authority, allowed paths, acceptance criteria, or dependencies set by the parent.

Worker-local planning does not need continuous synchronization with the parent. Summarize it in the parent report only when the parent needs it to resume, verify, or integrate the work. Remove temporary planning records after successful delivery by default; retain them only for a blocker, a planned continuation, or an explicit audit need.

## Parent durable-state boundary

Durable state is for stable information that remains useful after the current task, such as durable user preferences, architectural decisions, stable constraints, or reliable continuation pointers. The parent verifies and curates such information before preserving it.

Do not promote routine progress, temporary task status, test output, volatile identifiers, or information already authoritative in project files merely because a worker reported it. If durable state is unavailable, keep necessary continuation information in the parent’s authoritative coordination record or normal project documentation, then report the reduced recall capability honestly.

## Worker temporary-state boundary

Workers do not write project-level durable state by default. They may keep temporary notes inside their own task or within an explicitly allowed work path. A worker reports any potentially durable fact to the parent, which decides whether to preserve, revise, or discard it.

If a worker task must continue later, it may keep a scoped continuation note using an available mechanism. The note remains worker-local, contains no secrets, and does not become authoritative project memory automatically. Short-lived work may remain only in the current task context.

## Task-to-task messaging fallback

Every worker contract must include `report_required: true` and a concrete parent message channel. On normal completion or blocking, the worker actively sends the terminal report before ending; merely leaving text in the worker window is not delivery.

If the host-created implicit reply-to-source route is unavailable and no machine result or independent query confirms the current coordinator's exact ID, the worker leaves the same structured final result visible in its task. It never substitutes an incoming parent or root ID as the coordinator's own ID. The parent performs one bounded collection check after the worker’s completion event or host signal. It does not routinely poll unchanged tasks. Mark degraded routing, and report delivery as blocked if the immediate coordinator did not receive the result. A root channel remains supplemental only and cannot justify a claim of direct delivery.

The parent verifies the collected result and records whether the required report was actually received. It must not represent an undelivered worker result as normal completion.

## Combined notification protocol

The worker actively sends the terminal report to its immediate coordinator.
The parent waits for events across the current active-task set rather than
inspecting unchanged tasks. A matching message or completion event may arrive
first; whichever arrives first wakes the parent. The parent correlates the
delivery by `task_id` and `thread_id`, validates the structured report, and
sets `report_received: true` only for a valid matching report. It records one
terminal result and deduplicates the other matching event, so the protocol does
not permit routine polling. The parent creates a dependent reviewer only for
the matching implementation task after its artifact is accessible.

## Review source branches

Shared directory + serialized implementation/review → reviewer reads the
current files directly.

Isolated worktree/copy → the parent supplies a worktree, commit, branch,
handoff, or diff that contains the implementation.

Concurrent writers in one shared directory remain prohibited when paths
overlap. Review is read-only by default; if the supplied source is missing,
stale, or inaccessible, the reviewer reports `BLOCKED` rather than reviewing
the untouched baseline.

## Git/worktree isolation fallback

For concurrent writers, choose the strongest available isolation in this order:

1. separate Git worktrees;
2. separate project copies or host-provided isolated environments;
3. non-overlapping write paths in one workspace;
4. serialized execution when safe isolation cannot be established.

Before dispatch, the parent checks that write ownership does not overlap or that the selected isolation prevents conflicts. If no safe concurrent option exists, serialize the tasks and state that constraint in the parent coordination record.

Read-only review does not require a write worktree unless the host requires one to create an independent task. Workers do not merge, push, publish, change remotes, or perform destructive cleanup unless the user explicitly authorizes that action in the task contract.
