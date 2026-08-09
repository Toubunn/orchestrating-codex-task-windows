# Constellary

- 🇬🇧 [English](README.md)
- 🇯🇵 [日本語](README.ja.md)
- 🇨🇳 [简体中文](README.zh-CN.md)

Constellary 是一个 Codex Skill，用于在多个独立、可见的 Codex Desktop 任务之间
协调边界清晰的工作。多个独立任务像星星一样各自运行，由上级任务把它们组织成一个有意义的星群。

当前候选版本是 `v2.0.0-alpha`，稳定目标是 `v2.0.0`。公开 Skill slug 是
`constellary`，调用方式是 `$constellary`。

## v2.0.0-alpha 本次更新内容

- **破坏性更名：** 项目和 Skill 统一更名为 Constellary。请使用 `$constellary`，并安装
  `skills/constellary/`；旧名称和旧调用方式只保留在迁移记录中。
- **真正的 Desktop 下级任务：** `coordination_surface: codex_desktop` 与
  `desktop_required` 要求上级在同一个已注册 Codex 项目里创建侧边栏独立可见的任务。
  缺少必需宿主能力时必须报告 `BLOCKED`，绝不回退到终端或 CLI。
- **更安全的文件执行：** `execution_environment: auto_safe` 根据写入风险独立选择
  Local、Worktree 或串行执行，不会改变 Desktop 协调面。
- **可预测的身份与上下级关系：** 创建时标题遵循确定性的 34 code-point 协议；
  creator identity、任务合同、report route 和上级负责集成共同建立逻辑上下级关系。
- **明确的交付与审查：** worker 主动发送结构化 report，上级通过宿主事件等待；每次
  独立只读审查都创建全新任务，修复则创建另一个有边界的实现任务。
- **CLI 分离规划：** [FUTURE_WORK.md](FUTURE_WORK.md) 记录未来明确 opt-in 的
  CLI Adapter，不把它混入 Desktop 工作流，也不作为自动 fallback。
- **公开卫生检查：** 对每个公开 regular file 和 path 扫描机器专用路径、identifier、
  secret-shaped value、private state、旧名称残留、损坏链接、异常标题和缓存产物。
- **发布证据：** 英文、日文和简体中文 README 与示例保持同一 contract，并通过
  79 项 automated test 和 package validator 保护候选版本。

## 范围

Constellary v2 的唯一可执行协调面是 Codex Desktop。独立任务是拥有独立上下文和
生命周期的可见任务窗口，不是 worker 内部的 subagent。上级任务负责架构、任务台账、
项目上下文、集成、汇报和最终结论。

运行策略是确定性的：设置 `coordination_surface: codex_desktop`，使用
`desktop_required`，解析当前注册的同一 Codex 项目，通过宿主的 `create_thread` 创建
下级任务，然后核验 `thread_id`、`project_id`、`host_id`、实际标题和侧边栏可见性。
通过宿主事件等待，并使用宿主 thread 发送 report。任何必需 Desktop 能力缺失时，
dispatch 必须是 `BLOCKED`。

v2 不提供 CLI fallback。terminal、`codex`、`codex exec`、`codex.exe`、PowerShell、
`pwsh`、`cmd`、Windows Terminal、`Start-Process`、subprocess、background shell、
临时 prompt 文件或 internal-only agent，都不是成功的 Desktop 路径。

## 安装

将单独的目录 `skills/constellary/` 复制到 Codex Skills 目录。仓库级测试和验证脚本
面向维护者；Skill 本身可以独立安装。

## 示例

请选择熟悉的语言，从同一个最小编排示例开始：

- 🇬🇧 [English 最小编排示例](examples/minimal-orchestration.en.md)
- 🇯🇵 [日本語の最小オーケストレーション例](examples/minimal-orchestration.ja.md)
- 🇨🇳 [简体中文最小编排示例](examples/minimal-orchestration.zh-CN.md)

三个示例相互链接。未来扩展记录在
[FUTURE_WORK.md](FUTURE_WORK.md) 中。

## 标题协议

每个下级任务都使用以下格式：

`Constellary · <TaskID> · <Role> · <ShortGoal>`

宿主标题预算为 NFC 归一化后的 34 个 Unicode code point。创建前先执行 NFC Unicode normalization、
折叠多余空白，并对 short goal 做确定性压缩，保持项目名、TaskID 和 role 不变。
创建后核验宿主返回/显示的 actual title，不接受宿主隐式截断。紧凑示例是
`Constellary · T01 · 实现 · Desktop适配`；审查、修复、复审分别使用 `T01-R1`、
`T01-F1`、`T01-R2`。

## 运行时默认值

所有下级角色，包括实现 worker 和独立 reviewer，默认使用 Luna Max，即
`gpt-5.6-luna` 与 `max` reasoning。当前用户指令或项目配置可以覆盖 model、reasoning
等级或两者，不需要重复确认。Skill 不会静默提升 reviewer。

实现与审查始终使用两个全新的独立任务。审查默认只读；修复必须作为新的、有边界的
实现任务。侧边栏可见的 peer 通过 creator identity、source thread、project context、
task ledger 和 report route 建立逻辑关联。

## 汇报、事件等待与轮询

每个 worker 都必须在结束前主动向直属 coordinator 发送一次结构化 terminal report。
只留在 worker 任务窗口中的结果不算已交付。上级等待匹配的 message、completion、
blocker、failure 或 user event，不常规轮询未变化的任务。使用 `task_id` 与 `thread_id`
做关联，去重匹配的 completion event，并将 `report_received` 与 review verdict、
`review_source` 分开。

## 执行环境

协调面与文件执行环境是两个独立决策。公开策略是
`execution_environment: auto_safe`：准备好的 isolated copy 或串行单写者工作使用
Local，Git 仓库中的并发写入或实质重叠风险使用 Worktree。用户可以 override；如果没有
安全隔离，就串行执行或报告 `BLOCKED`。

## 未来 CLI Adapter

CLI 在 `v2.0.0` 中不支持也不可执行。[FUTURE_WORK.md](FUTURE_WORK.md) 记录了未来
明确 opt-in 的生命周期监督、清理、结构化 report transport、身份关联、并发、reviewer
创建、安全、跨平台和端到端验证要求。它绝不能自动成为 Desktop fallback。

## 验证

在仓库根目录运行确定性的 contract 与 hygiene 检查：

```text
python -B scripts/validate_package.py
```

检查包括 Skill contract、三语链接、机器专用路径、live task 或 project ID、secret-shaped
value、未解决的 authoring marker、损坏的 Skill reference、旧名残留和缓存产物，也会验证
`review_source` 与 `report_received` 契约。

## 许可证

本仓库根据 [MIT License](LICENSE) 开源。
