# Constellary Desktop 最小编排示例

- 🇬🇧 [English](minimal-orchestration.en.md)
- 🇯🇵 [日本語](minimal-orchestration.ja.md)
- 🇨🇳 [简体中文](minimal-orchestration.zh-CN.md)

这个示例展示最小的 Constellary Desktop 流程：创建一个有明确标题的同项目任务，核验
宿主身份和侧边栏可见性，等待宿主事件，接收 report，然后创建一个全新的只读 reviewer。
下面的值都是符号示例，实际使用时替换成当前项目和任务值。

## 父任务 brief

使用 `$constellary`、`coordination_surface: codex_desktop` 与
`execution_environment: auto_safe`，把工作拆成边界清晰的任务：

- `T01`：在指定 source path 中实现修改。
- `T01-R1`：实现完成后只读审查实际 artifact。

父任务负责架构、任务台账、项目上下文、集成和最终结论。worker 不负责 merge、push、
publish，也不能自行扩大范围。

## 标题协议

创建前按宿主 NFC 归一化后的 34 个 Unicode code point 标题预算处理。先做 NFC Unicode normalization，折叠多余空白，
再对 short goal 做确定性压缩，创建后核验宿主返回的 actual title：

- `Constellary · T01 · 实现 · Desktop适配`
- `Constellary · T01-R1 · 审查 · 适配`
- `Constellary · T01-F1 · 修复 · 适配`
- `Constellary · T01-R2 · 复审 · 适配`

不接受宿主隐式截断或标题不匹配。

## 父任务台账

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

父任务通过 `create_thread` 创建，并核验 `thread_id`、`project_id`、`host_id`、实际
`title` 和 `sidebar_visible`，随后使用 `wait_threads`、`read_thread` 与
`send_message_to_thread`。匹配的 report 与 completion event 只产生一个终态结果。

## worker brief

```yaml
task_id: T01
role: implementation
goal: 更新指定 source path。
coordinator_task_id: CURRENT_COORDINATOR_TASK
coordinator_report_channel: HOST_REPLY_TO_SOURCE
project_root: DETECTED_PROJECT_ROOT
allowed_write_paths:
  - assigned/source/path
acceptance_criteria:
  - 已实现指定行为
  - 必要检查通过
verification_required:
  - python -m unittest
report_required: true
```

worker 在结束前主动向直属 coordinator 发送一次结构化 terminal report。

## 全新的 reviewer

实现 artifact 可以通过 `review_source` 访问后，父任务创建独立只读 reviewer，标题为
`Constellary · T01-R1 · 审查 · 适配`。reviewer 接收原始 acceptance criteria 与
实际 artifact，确认同一 registered project 和 sidebar-visible task，并返回 `APPROVED`
或 `CHANGES_REQUIRED`。修复使用新的 `T01-F1`，复审使用全新的 `T01-R2`。

如果必需 Desktop 能力缺失，父任务报告 `BLOCKED`。不得使用 CLI、terminal、PowerShell、
临时 prompt 文件或 internal-only agent 作为 fallback。

## 集成门槛

只有满足以下条件，父任务才能集成：

1. 已接收并验证匹配的 report；
2. 已核验 title、thread、host、project 和 sidebar 证据；
3. 已核对修改路径和必要检查；
4. reviewer 确实看到实际 artifact 且 verdict 为 `APPROVED`；
5. blocker、关注点和不确定性已解决或如实报告。
