# Task and Report Contracts

Use these contracts as dispatch interfaces. The values below are neutral symbolic examples. Replace them with the detected project values and the assigned scope when creating a real task; do not copy local paths, private identifiers, or secrets into a public Skill package.

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
  - stated acceptance criteria are checked
  - findings are reproducible
verification_required:
  - run the checks listed in this brief
report_required: true
```

Review is read-only by default. The review verdict is a separate field with value `APPROVED` or `CHANGES_REQUIRED`. If the verdict is `CHANGES_REQUIRED`, the coordinator creates a new implementation task with its own contract and later requests a fresh review.

## Report-route resolution

Resolve delivery in this order: explicit direct coordinator ID and coordinator report channel; host implicit reply-to-source; then one bounded collection after a completion event. If neither a completion event nor a collectable result exists, the worker must be marked `BLOCKED`. If only a root channel is available, mark `degraded routing` and must not claim direct delivery to the immediate coordinator.

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
verification:
  - command and result
evidence:
  - reproducible evidence
blockers: none
remaining_concerns: none
uncertainty: none
```

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
