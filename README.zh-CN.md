# Orchestrating Codex Task Windows

- 🇬🇧 [English](README.md)
- 🇯🇵 [日本語](README.ja.md)
- 🇨🇳 [简体中文](README.zh-CN.md)

本仓库包含 `orchestrating-codex-task-windows` Skill，用于在多个可见、上下文相互隔离的 Codex 任务窗口之间，协调边界清晰的工作。

## 范围

这是一个仅面向 Codex 的 v1 版本。独立任务是一个单独的、可见的 Codex 窗口，拥有自己的上下文和生命周期；它不等同于 worker 内部使用的 subagent。worker 可以在内部使用 subagent，但由父任务负责协调独立任务，并拥有架构、集成、用户沟通和最终结论的责任。

## 安装

将单独的目录 `skills/orchestrating-codex-task-windows/` 复制到 Codex 的 Skills 目录中。仓库级别的测试和验证脚本面向维护者；Skill 本身可以独立安装。

## 示例

请选择你熟悉的语言，从同一个最小编排示例开始：

- 🇬🇧 [English 最小编排示例](examples/minimal-orchestration.en.md)
- 🇯🇵 [日语最小编排示例](examples/minimal-orchestration.ja.md)
- 🇨🇳 [简体中文最小编排示例](examples/minimal-orchestration.zh-CN.md)

三个示例互相链接。未来扩展记录在
[FUTURE_WORK.md](FUTURE_WORK.md) 中。

## 运行时默认值

所有下级角色，包括实现 worker 和独立 reviewer，默认使用 Luna Max，也就是 `gpt-5.6-luna` 和 `max` reasoning。当前用户指令或项目配置可以覆盖任意角色的模型、reasoning 等级，或者同时覆盖两者，不需要重复确认。

Luna Max 适合边界清晰的常规审查。对于安全、架构、并发、数据完整性或发布关键型审查，用户或项目配置可以选择 Sol，或者其他已经配置的更强 reviewer。如果没有人要求或配置升级，Skill 不会自动提升 reviewer 的模型。宿主暴露实际运行时信息时，父任务应该记录它，并如实报告任何替换或差异。

实现和审查使用两个不同的全新独立任务。审查默认是只读的；如果需要修复，应作为新的、有边界的实现任务派发。

## 直接使用 Sol，还是使用编排

如果修改很小、耦合紧密，或者需要持续的架构判断，直接使用 Sol 任务。如果有两个或更多边界清晰的职责可以独立完成，例如实现、测试、文档或分别调查，就使用这个 Skill。

对于安全、架构、并发、数据完整性或发布关键型工作，一个实用的混合方式是让 Sol 担任父任务或 reviewer，让 Luna Max 担任 worker。下游窗口数量上限为 6 个，但这不是目标；只从任务真正需要的独立 worker 数量开始。

## 报告、事件等待与轮询

下面三个概念并不相同：

- **Worker report：** worker 或 reviewer 在完成或受阻时，主动发送给直属 coordinator 的结构化结果。它包含工作结果、变更路径、检查、证据、阻塞点、担忧和不确定性。
- **Event wait：** 父任务等待相关消息、完成、阻塞、失败或用户事件，直到其中一种活动将其唤醒。父任务可以等待当前活动任务集合，而不需要持续查看它们。
- **Polling：** 为了确认是否发生变化，反复打开或检查没有变化的子任务。Skill 禁止常规轮询。

报告和事件等待应结合使用：worker 发送报告，父任务等待匹配的活动。先到达的完成事件只负责唤醒父任务，并不代表结构化报告已经接收或验证。只有在父任务验证匹配的结构化报告后，才设置 `report_received`（已收到报告）。如果结构化报告先到，之后到达的匹配完成事件就是第二次传递，应当去重。无论哪一种顺序，每个任务都只记录一个终态结果；另一条匹配传递不能产生第二个结果。

## 项目与子任务

独立子任务默认使用父任务已经注册的 Codex 项目。worktree 是同一个项目内的隔离工作区，并不会让子任务变成 projectless。Projectless 执行只适用于真正不处理文件的工作，或者用户明确要求的情况。

创建子任务后，coordinator 要验证它的项目上下文。如果无法选择或验证目标项目，coordinator 应在 dispatch 前停止，不得默默创建一个 projectless 窗口。

当多个子任务同时运行时，父任务要在 task ledger 中把每个 `task_id` 与 `thread_id` 配对。不能根据消息先后判断归属。报告和完成事件都通过这些标识符进行匹配；活跃报告与相应完成事件同时到达时，仍然只产生一个终态结果，而不是两个。

默认情况下，父任务同时最多运行 6 个下游窗口；如果把父任务也算在内，总活动窗口数为 7 个。用户可以选择不同的上限，但当前上限是硬上限，绝不能超过。如果还有剩余任务，应先完成当前批次，再开始下一批次。

子任务收到的 source address 是父任务的地址，而不是子任务自己的地址。子任务之后如果又创建了另一个任务，不能复制收到的地址并把它冒充成自己的地址；默认使用宿主创建的 reply route，只有在宿主确认 coordinator 的准确地址后，才使用直接地址。

## 审查成果与能力回退

reviewer 会收到原始目标、验收标准、必需检查，以及指向实际成果的具体 `review_source`。这个 source 可以是当前 shared workspace，也可以是隔离的 worktree、commit、branch、handoff 或 diff。reviewer 不需要实现者的推理或自我评价，也不能审查无法访问或已经过期的 baseline。

所有 worker 在结束前都必须向直属 coordinator 发送结构化终端报告。只留在 worker 任务窗口中的结果，不算已经交付。

planning、durable state、messaging、Git 和 worktree isolation 都是可选能力。工作流会依次使用当前可用的最强能力、普通的项目内记录、短期任务上下文。如果连续性或隔离能力降低，应如实报告；不能借此凭空增加依赖，也不能默默改变范围。

最小用法：

```text
Use $orchestrating-codex-task-windows to split this project into independent implementation and review tasks, collect each required report, and keep final integration in the parent task.
```

## 安全边界

Skill 不会自动 merge、push、publish、创建或修改 remote、执行破坏性清理，也不会自动做出最终发布结论。这些操作都需要明确授权，并由父任务负责验证。

如果系统已经授予 full access，子任务不应再次请求许可。单纯的命令失败不等于权限问题：应先检查命令、工作目录、绝对路径、引号、shell 和进程启动方式。只有任务确实需要尚未授予的权限时，才应该请求授权。

## 验证

请在仓库根目录运行确定性的合同检查和卫生检查：

```text
python -B scripts/validate_package.py
```

检查内容包括 Skill 合同、机器专用路径、当前任务或项目标识符、疑似秘密值、未解决的 authoring marker、损坏的 Skill 引用，以及被打包的缓存成果物。

## 许可证

本仓库根据 [MIT License](LICENSE) 开源。
