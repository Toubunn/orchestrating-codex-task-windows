# Minimal Constellary Desktop Orchestration Example

- 🇬🇧 [English](minimal-orchestration.en.md)
- 🇯🇵 [日本語](minimal-orchestration.ja.md)
- 🇨🇳 [简体中文](minimal-orchestration.zh-CN.md)

This example shows the smallest useful Constellary Desktop loop: create a
named same-project task, verify its host identity and sidebar visibility, wait
for host events, receive a report, then create a fresh read-only reviewer.
Values are symbolic; replace them with current project and task values.

## Parent brief

Use `$constellary` with `coordination_surface: codex_desktop` and
`execution_environment: auto_safe` to split the work into bounded tasks:

- `T01`: implement the change in the assigned source path.
- `T01-R1`: review the actual artifact read-only after implementation.

The parent owns architecture, the task ledger, project context, integration,
and final claims. Workers do not merge, push, publish, or broaden scope.

## Title protocol

Create titles before dispatch using the 34 NFC-normalized Unicode code-point
host budget. Normalize with NFC, deterministically compress the short goal before creation, and verify the
actual returned title afterward:

- `Constellary · T01 · 实现 · Desktop适配`
- `Constellary · T01-R1 · 审查 · 适配`
- `Constellary · T01-F1 · 修复 · 适配`
- `Constellary · T01-R2 · 复审 · 适配`

Do not accept implicit host truncation or a title mismatch.

## Parent ledger

```yaml
task_id: T01
thread_id: CREATED_THREAD
project_context: CURRENT_PROJECT
project_id: CURRENT_PROJECT_ID
host_id: CREATED_HOST
title: "Constellary · T01 · 实现 · Desktop适配"
sidebar_visible: true
coordination_surface: codex_desktop
execution_environment: auto_safe
role: implementation
depends_on: none
status: active
report_received: false
review_source:
  kind: pending
  locator: pending
review_verdict: pending
```

The parent creates the task through `create_thread`, verifies `thread_id`,
`project_id`, `host_id`, actual `title`, and `sidebar_visible`, then uses
`wait_threads`, `read_thread`, and `send_message_to_thread`. A matching report
and completion event produce one terminal result, not two.

## Worker brief

```yaml
task_id: T01
role: implementation
goal: Update the assigned source path.
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

The worker sends one structured terminal report to the immediate coordinator.

## Fresh reviewer

After the implementation artifact is accessible through `review_source`, the
parent creates a separate read-only reviewer titled
`Constellary · T01-R1 · 审查 · 适配`. The reviewer receives the original
acceptance criteria and actual artifact, confirms it is the same registered
project and sidebar-visible task, and returns `APPROVED` or `CHANGES_REQUIRED`.
Repair is a new bounded task (`T01-F1`) followed by a fresh reviewer (`T01-R2`).

If the required Desktop capability is absent, the parent reports `BLOCKED`.
There is no CLI, terminal, PowerShell, temporary prompt-file, or internal-only
agent fallback.

## Integration gate

The parent integrates only when:

1. the matching report was received and validated;
2. the title, thread, host, project, and sidebar evidence is verified;
3. the changed paths and required checks are verified;
4. the reviewer saw the actual artifact and returned `APPROVED`;
5. blockers, concerns, and uncertainty are resolved or reported honestly.
