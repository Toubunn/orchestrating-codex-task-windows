# 简体中文最小编排示例

- 🇬🇧 [English](minimal-orchestration.en.md)
- 🇯🇵 [日本語](minimal-orchestration.ja.md)
- 🇨🇳 [简体中文](minimal-orchestration.zh-CN.md)


这个示例展示最小的“实现 → 汇报 → 审查 → 集成”流程。下面的值都是可复用的符号示例，
实际使用时要替换成当前项目和任务的真实值。

## 🧭 父任务 brief

把工作拆成两个边界清晰的独立任务：

- `TASK-001`：在指定源代码路径中实现 parser 修改。
- `TASK-002`：在指定测试路径中添加针对性测试。

父任务负责架构、任务台账、项目上下文、集成和最终结论。worker 不负责 merge、push、publish，
也不能自行扩大范围。

## 📋 父任务台账

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

父任务创建 child 后先验证项目上下文，然后等待匹配的活动。消息和完成事件都通过 `task_id` 与
`thread_id` 关联。同一个任务的 report 和 completion event 到达时，只记录一个 terminal result。

## 🛠️ worker brief

```yaml
task_id: TASK-001
role: implementation
goal: 更新指定源代码路径中的 parser validation。
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

worker 在结束前主动发送一次结构化 terminal report。

## 📣 worker report

```yaml
status: DONE
task_id: TASK-001
work_completed: 已更新 parser validation。
files_changed:
  - assigned/source/path
verification:
  - python -m unittest: PASS
evidence:
  - 可复现的测试输出
review_source:
  kind: worktree
  locator: REVIEWABLE_WORKTREE
blockers: none
remaining_concerns: none
uncertainty: none
```

## 🔍 fresh reviewer

实现 artifact 可以访问后，父任务再创建一个独立的、默认只读的 reviewer task。reviewer 会收到原始
目标、验收标准、必要检查和具体的 `review_source`。reviewer 返回 `APPROVED` 或
`CHANGES_REQUIRED`，不能为了让自己的结论通过而直接修改实现。

## ✅ 集成门槛

只有满足以下条件，父任务才能集成：

1. 已收到并验证匹配的 report；
2. 已核对修改路径和必要检查；
3. reviewer 确实看到了实际 artifact；
4. review verdict 是 `APPROVED`；
5. blocker 和 remaining concern 已解决。
