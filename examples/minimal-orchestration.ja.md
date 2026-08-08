# 最小オーケストレーション例

- 🇬🇧 [English](minimal-orchestration.en.md)
- 🇯🇵 [日本語](minimal-orchestration.ja.md)
- 🇨🇳 [简体中文](minimal-orchestration.zh-CN.md)


この例は、実装 → 報告 → レビュー → 統合という最小限の流れを示します。
値は再利用可能な記号例です。実際のプロジェクトとタスクの値に置き換えてください。

## 🧭 親タスクの brief

作業を、境界の明確な二つの独立タスクに分けます。

- `TASK-001`: 指定されたソースパスの parser を実装する。
- `TASK-002`: 指定されたテストパスに集中的なテストを追加する。

親タスクは、アーキテクチャ、タスク台帳、プロジェクトコンテキスト、統合、最終的な主張を
担当します。worker は、merge、push、publish、スコープの拡大を行いません。

## 📋 親タスク台帳

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

親タスクは child の作成後にプロジェクトコンテキストを確認し、対応する活動を待ちます。
メッセージと完了イベントは `task_id` と `thread_id` で関連付けます。同じタスクの report と
completion event が届いても、terminal result は一つだけ記録します。

## 🛠️ worker brief

```yaml
task_id: TASK-001
role: implementation
goal: 指定されたソースパスの parser validation を更新する。
coordinator_task_id: CURRENT_COORDINATOR_TASK
coordinator_report_channel: HOST_REPLY_TO_SOURCE
project_root: DETECTED_PROJECT_ROOT
allowed_write_paths:
  - assigned/source/path
acceptance_criteria:
  - 指定された動作が実装されている
  - 必須チェックが成功する
verification_required:
  - python -m unittest
report_required: true
```

worker は終了前に、構造化された terminal report を一度送信します。

## 📣 worker report

```yaml
status: DONE
task_id: TASK-001
work_completed: parser validation を更新した。
files_changed:
  - assigned/source/path
verification:
  - python -m unittest: PASS
evidence:
  - 再現可能なテスト出力
review_source:
  kind: worktree
  locator: REVIEWABLE_WORKTREE
blockers: none
remaining_concerns: none
uncertainty: none
```

## 🔍 fresh reviewer

実装 artifact にアクセスできるようになった後、親タスクは別の read-only reviewer task を作成します。
reviewer には、元の goal、acceptance criteria、required checks、具体的な `review_source` を渡します。
reviewer は `APPROVED` または `CHANGES_REQUIRED` を返し、自分で実装を修正しません。

## ✅ 統合ゲート

親タスクは、次の条件を満たした後だけ統合します。

1. 対応する report が受信され、検証されている。
2. 変更パスと必須チェックが確認されている。
3. reviewer が実際の artifact を確認している。
4. review verdict が `APPROVED` である。
5. blocker と remaining concern が解決されている。
