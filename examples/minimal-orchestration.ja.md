# Constellary Desktop 最小オーケストレーション例

- 🇬🇧 [English](minimal-orchestration.en.md)
- 🇯🇵 [日本語](minimal-orchestration.ja.md)
- 🇨🇳 [简体中文](minimal-orchestration.zh-CN.md)

この例は、同じプロジェクトの名前付き Desktop タスクを作成し、host identity と
sidebar visibility を確認し、host event を待ち、report を受け取り、その後に
read-only の新しい reviewer を作成する最小の Constellary ループです。値は記号例なので、
現在の project と task の値に置き換えてください。

## 親タスクの brief

`$constellary`、`coordination_surface: codex_desktop`、
`execution_environment: auto_safe` を使い、作業を境界の明確なタスクへ分けます。

- `T01`: 指定された source path の変更を実装する。
- `T01-R1`: 実装後に実際の artifact を read-only で審査する。

親タスクはアーキテクチャ、task ledger、project context、統合、最終的な主張を担当します。
worker は merge、push、publish、スコープ拡大を行いません。

## タイトルプロトコル

作成前に NFC 正規化後の Unicode code point 34 個の host title budget に合わせます。NFC で normalize し、short goal を
決定的に圧縮してから作成し、作成後に actual title を検証します。

- `Constellary · T01 · 实现 · Desktop适配`
- `Constellary · T01-R1 · 审查 · 适配`
- `Constellary · T01-F1 · 修复 · 适配`
- `Constellary · T01-R2 · 复审 · 适配`

host の暗黙の切り詰めや title mismatch は受け入れません。

## 親タスク台帳

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

親は `create_thread` で作成し、`thread_id`、`project_id`、`host_id`、actual `title`、
`sidebar_visible` を確認します。その後 `wait_threads`、`read_thread`、
`send_message_to_thread` を使います。対応する report と completion event は terminal
result を一つだけ作ります。

## worker brief

```yaml
task_id: T01
role: implementation
goal: 指定された source path を更新する。
coordinator_task_id: CURRENT_COORDINATOR_TASK
coordinator_report_channel: HOST_REPLY_TO_SOURCE
project_root: DETECTED_PROJECT_ROOT
allowed_write_paths:
  - assigned/source/path
acceptance_criteria:
  - 指定された動作を実装する
  - 必須チェックが成功する
verification_required:
  - python -m unittest
report_required: true
```

worker は直属 coordinator に structured terminal report を一度送ります。

## fresh reviewer

実装 artifact が `review_source` からアクセスできるようになったら、親は
`Constellary · T01-R1 · 审查 · 适配` という別の read-only reviewer を作成します。
reviewer は original acceptance criteria と actual artifact、same registered project、
sidebar-visible task を確認し、`APPROVED` または `CHANGES_REQUIRED` を返します。修正は
新しい `T01-F1`、再審査は fresh な `T01-R2` です。

必須 Desktop capability がなければ `BLOCKED` と報告します。CLI、terminal、PowerShell、
temporary prompt-file、internal-only agent を fallback にしてはいけません。

## 統合ゲート

親タスクは次を満たした後だけ統合します。

1. matching report が受信・検証されている。
2. title、thread、host、project、sidebar の証拠が確認されている。
3. 変更パスと必須チェックが確認されている。
4. reviewer が実際の artifact を確認し `APPROVED` を返している。
5. blocker、concern、不確実性が解決または正直に報告されている。
