# Task and Report Contracts

Use these contracts as dispatch interfaces. The values below are neutral symbolic examples. Replace them with the detected project values and the assigned scope when creating a real task; do not copy local paths, private identifiers, or secrets into a public Skill package.

## Parent task ledger contract

The parent owns one authoritative task ledger keyed by `task_id`. Each row
keeps the task and thread identities together so that arrival order does not
determine ownership. The parent correlates every message and completion event
by the pair `task_id` and `thread_id`, then deduplicates a matching terminal
delivery instead of recording a second result.

```yaml
task_id: TASK-001
thread_id: CREATED_THREAD
project_context: CURRENT_PROJECT
role: implementation
depends_on: none
status: active
report_received: false
review_source:
  kind: pending
  locator: pending
review_verdict: pending
```

The ledger fields mean:

- `task_id` is the stable correlation key assigned before child creation.
- `thread_id` identifies the created independent task window once available.
- `project_context` records the selected project context for the task.
- `role` is the bounded responsibility, such as `implementation` or `review`.
- `depends_on` names the task whose verified result is required first.
- `status` is one of `active`, `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`,
  or `BLOCKED`.
- `report_received` becomes `true` only after the structured terminal report
  is validated.
- `review_source` records the artifact kind and locator, or a pending value
  before implementation is delivered.
- `review_verdict` remains separate from terminal status and is `pending` until
  review returns `APPROVED` or `CHANGES_REQUIRED`.

## Project context contract

Children inherit the current registered project; this is the same project as
the parent by default. The parent verifies the child-creation result
before considering dispatch complete. The default project context is:

```yaml
project_context:
  kind: project
  project_id: CURRENT_PROJECT
  environment: worktree
```

For a non-Git project, use `environment: local` while retaining the selected
project context. Projectless execution is valid only for genuinely no-file
work or an explicit user request. If the parent cannot choose or verify the
current project, it stops dispatch rather than silently degrading to a
projectless child.

## Implementation task contract

```yaml
task_id: TASK-001
role: implementation
goal: Implement the bounded deliverable described in this brief.
coordinator_task_id: CURRENT_COORDINATOR_TASK
coordinator_report_channel: SEND_MESSAGE_TO_COORDINATOR_TASK
root_task_id: OPTIONAL_ROOT_TASK
root_notification_channel: OPTIONAL_ROOT_NOTIFICATION_CHANNEL
project_root: DETECTED_PROJECT_ROOT
allowed_write_paths:
  - ASSIGNED_PATH
forbidden_actions:
  - broaden scope
  - edit parent coordination state
  - merge, push, publish, or change remotes
acceptance_criteria:
  - assigned behavior is implemented
  - required checks pass
verification_required:
  - run the checks listed in this brief
report_required: true
```

`coordinator_task_id` and `coordinator_report_channel` identify the immediate coordinator that created this worker. The root fields are optional notification targets; a root task cannot replace the immediate coordinator or its report channel. Do not place real task identifiers in a reusable contract template.

The implementation worker owns its internal method. The parent supplies the boundary and acceptance criteria, not micro-management of worker-internal subagents.

## Review task contract

```yaml
task_id: TASK-002
role: review
goal: Review the assigned implementation against its brief and return evidence.
coordinator_task_id: CURRENT_COORDINATOR_TASK
coordinator_report_channel: SEND_MESSAGE_TO_COORDINATOR_TASK
root_task_id: OPTIONAL_ROOT_TASK
root_notification_channel: OPTIONAL_ROOT_NOTIFICATION_CHANNEL
project_root: DETECTED_PROJECT_ROOT
allowed_write_paths:
  - none
forbidden_actions:
  - edit implementation files
  - broaden review scope
  - merge, push, publish, or change remotes
acceptance_criteria:
  - original acceptance criteria are checked
  - findings are reproducible
review_source:
  kind: shared_workspace
  locator: current_project_root
verification_required:
  - run the checks listed in this brief
report_required: true
```

The reviewer receives the original acceptance criteria and the actual artifact
through `review_source`. It does not need the implementer's reasoning,
intermediate attempts, or self-assessment. Before issuing a verdict, the
reviewer confirms that the source contains the claimed modification. A stale,
missing, or inaccessible source is `BLOCKED`; the reviewer does not review the
baseline instead.

Review is read-only by default. The review verdict is a separate field with value `APPROVED` or `CHANGES_REQUIRED`. If the verdict is `CHANGES_REQUIRED`, the coordinator creates a new implementation task with its own contract and later requests a fresh review.

## Nested coordinator routing

A machine-provided source_thread_id in the current delegation envelope identifies the parent task that created the current task, not the current task's own ID. A nested coordinator must follow this rule: do not copy an incoming source_thread_id or root ID into a child brief as coordinator_task_id. An optional root remains only a supplemental notification target.

Use the host-created implicit reply-to-source route by default. Use an explicit direct ID only when the current coordinator's exact ID was confirmed by a machine result or independent query and passed verbatim. If a worker's send tool requires an ID, it uses the exact source_thread_id from its own envelope, not a manually transcribed or guessed ID from the brief.

If the implicit route is unavailable and the coordinator's own ID is not confirmed, never substitute a root or parent ID. Rely on the completion event and one bounded collection, mark `degraded routing`, and report `BLOCKED` if the immediate coordinator cannot receive the result.

## Report-route resolution

Resolve delivery in this order: host implicit reply-to-source; an explicit direct coordinator ID and coordinator report channel only when confirmed; then one bounded collection after a completion event. If neither a completion event nor a collectable result exists, the worker must be marked `BLOCKED`. If only a root channel is available, mark `degraded routing` and must not claim direct delivery to the immediate coordinator.

## Blocker report

Use this shape when the worker cannot safely continue or cannot deliver through the required channel.

```yaml
status: BLOCKED
task_id: TASK-003
work_completed: Investigation stopped at the stated blocker.
files_changed:
  - none
verification:
  - command and result
evidence:
  - concise evidence of the blocker
blockers:
  - missing decision or unavailable capability
remaining_concerns: none
uncertainty:
  - what cannot be established safely
```

A worker that finished the file changes but cannot send the required parent message reports the delivery failure as a blocker rather than claiming normal completion.

## Completion report

Use this shape for a successfully delivered implementation or review result.

```yaml
status: DONE
task_id: TASK-001
work_completed: concise summary
files_changed:
  - assigned/file
review_source:
  kind: shared_workspace
  locator: current_project_root
verification:
  - command and result
evidence:
  - reproducible evidence
blockers: none
remaining_concerns: none
uncertainty: none
```

For file-writing work, the completion report must return `review_source` with
both `kind` and `locator`. The allowed source kinds are `shared_workspace`,
`worktree`, `copy`, `commit`, `branch`, `handoff`, and `diff`; use `none` for a
genuinely no-file task. The locator identifies where the actual artifact can be
read, not proof that the artifact is correct. A no-file report may use
`kind: none` and `locator: none`.

The source kind describes how the reviewer reaches the actual artifact; it is
not the worker's execution environment. An isolated copy can use `kind: copy`
or be handed off through a concrete `diff`, `commit`, `branch`, or `handoff`.
A host-provided environment is not a review source by itself and must still
expose one of the concrete artifact sources above.

Use `DONE_WITH_CONCERNS` when the assigned work is delivered but a non-blocking concern remains. Use `NEEDS_CONTEXT` when a missing requirement or user-owned decision prevents safe continuation. The terminal status vocabulary is exactly:

- `DONE`
- `DONE_WITH_CONCERNS`
- `NEEDS_CONTEXT`
- `BLOCKED`

## Delivery checklist

Before ending a worker task, confirm that the report includes:

- the terminal status and task identifier;
- a concise account of work completed or the blocker;
- every changed path, or `none`;
- commands run and their results;
- reproducible evidence;
- blockers, remaining concerns, and uncertainty;
- delivery through the coordinator report channel or the explicitly assigned direct-coordinator route.
