# Minimal Orchestration Example

- 🇬🇧 [English](minimal-orchestration.en.md)
- 🇯🇵 [日本語](minimal-orchestration.ja.md)
- 🇨🇳 [简体中文](minimal-orchestration.zh-CN.md)


This example shows the smallest useful implementation → report → review →
integration loop. The values are symbolic; replace them with the current
project and task values.

## 🧭 Parent brief

Split the work into two bounded independent tasks:

- `TASK-001`: implement the parser change in the assigned source path.
- `TASK-002`: add focused tests in the assigned test path.

The parent owns the architecture, the task ledger, project context, integration,
and final claims. The workers do not merge, push, publish, or broaden scope.

## 📋 Parent ledger

```yaml
task_id: TASK-001
thread_id: CREATED_THREAD_001
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

The parent creates the task, verifies its project context, waits for matching
activity, and correlates messages and completion events by `task_id` and
`thread_id`. A matching report and completion event produce one terminal result,
not two.

## 🛠️ Worker brief

```yaml
task_id: TASK-001
role: implementation
goal: Update the parser validation in the assigned source path.
coordinator_task_id: CURRENT_COORDINATOR_TASK
coordinator_report_channel: HOST_REPLY_TO_SOURCE
project_root: DETECTED_PROJECT_ROOT
allowed_write_paths:
  - assigned/source/path
acceptance_criteria:
  - assigned behavior is implemented
  - required checks pass
verification_required:
  - python -m unittest
report_required: true
```

The worker sends one structured terminal report before ending.

## 📣 Worker report

```yaml
status: DONE
task_id: TASK-001
work_completed: Updated parser validation.
files_changed:
  - assigned/source/path
verification:
  - python -m unittest: PASS
evidence:
  - reproducible test output
review_source:
  kind: worktree
  locator: REVIEWABLE_WORKTREE
blockers: none
remaining_concerns: none
uncertainty: none
```

## 🔍 Fresh reviewer

After the implementation artifact is accessible, the parent creates a separate,
read-only reviewer task with the original goal, acceptance criteria, required
checks, and the concrete `review_source`. The reviewer returns either
`APPROVED` or `CHANGES_REQUIRED`; it does not repair the implementation itself.

## ✅ Integration gate

The parent integrates only when:

1. the matching report was received and validated;
2. the changed paths and required checks are verified;
3. the reviewer saw the actual artifact;
4. the review verdict is `APPROVED`;
5. blockers and remaining concerns are resolved.
