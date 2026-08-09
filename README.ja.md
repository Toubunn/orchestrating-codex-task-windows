# Constellary

- 🇬🇧 [English](README.md)
- 🇯🇵 [日本語](README.ja.md)
- 🇨🇳 [简体中文](README.zh-CN.md)

Constellary は、独立して可視化される Codex Desktop タスク間で、境界を
限定した作業を調整するための Codex Skill です。複数の独立タスクがそれぞれ
星のように動き、上位タスクがそれらを意味のある星群へ組織します。
中国語の承認文は「多个独立任务像星星一样各自运行，由上级任务把它们组织成一个有意义的星群。」です。

この候補のバージョンは `v2.0.0-alpha`、安定版の目標は `v2.0.0` です。
公開 Skill の slug は `constellary`、呼び出しは `$constellary` です。

## v2.0.0-alpha の更新内容

- **破壊的な名称変更:** プロジェクトと Skill を Constellary に統一しました。
  呼び出しは `$constellary`、インストール対象は `skills/constellary/` です。
  旧名称と旧呼び出しは migration record にだけ残します。
- **実体のある Desktop 下流タスク:** `coordination_surface: codex_desktop` と
  `desktop_required` により、親は同じ登録済み Codex プロジェクト内に、sidebar で
  別々に見えるタスクを作成します。必須ホスト機能がなければ `BLOCKED` とし、
  terminal や CLI へ fallback しません。
- **安全なファイル実行:** `execution_environment: auto_safe` は書き込みリスクに
  応じて Local、Worktree、または serialized execution を独立に選びます。
  Desktop の調整面は変更しません。
- **予測可能な識別と階層:** 作成時タイトルには決定的な 34 code-point protocol を
  適用し、creator identity、task contract、report route、親が所有する統合責任で
  論理的な上下関係を確立します。
- **明示的な配信と review:** worker は構造化 report を送り、親は host event を
  待機します。独立した read-only review は毎回新しいタスクを使い、修正も別の
  bounded implementation task で行います。
- **CLI の分離:** [FUTURE_WORK.md](FUTURE_WORK.md) には、Desktop workflow と
  混在させない、将来の明示的 opt-in CLI Adapter を記録しました。
- **公開時の hygiene:** すべての公開 regular file と path を対象に、machine-specific
  path、identifier、secret-shaped value、private state、旧名称、broken link、
  malformed title、cache artifact を検査します。
- **リリース証拠:** 英語・日本語・簡体字中国語の README と example が同じ contract
  を説明し、79 件の automated test と package validator で候補を保護します。

## 対象範囲

Constellary v2 の実行可能な調整面は Codex Desktop だけです。独立タスクは
固有のコンテキストとライフサイクルを持つ、別の可視タスクウィンドウであり、
worker 内部の subagent ではありません。親タスクがアーキテクチャ、task
ledger、プロジェクトコンテキスト、統合、report、最終的な主張を管理します。

ポリシーは決定的です。`coordination_surface: codex_desktop` と
`desktop_required` を適用し、現在登録されている同じ Codex プロジェクトを
解決します。親はホストの `create_thread` で下流タスクを作成し、`thread_id`、
`project_id`、`host_id`、実際のタイトル、sidebar visibility を検証します。
ホストイベントで待機し、ホストの thread で report を送ります。必須の Desktop
機能がない場合は `BLOCKED` です。

v2 に CLI fallback はありません。terminal、`codex`、`codex exec`、`codex.exe`、
PowerShell、`pwsh`、`cmd`、Windows Terminal、`Start-Process`、subprocess、
background shell、一時 prompt ファイル、internal-only agent は Desktop の
成功ルートではありません。

## インストール

`skills/constellary/` という単一ディレクトリを Codex の Skills ディレクトリへ
コピーしてください。リポジトリのテストと検証スクリプトはメンテナー向けで、
Skill 自体は単独でインストールできます。

## 例

好みの言語で同じ最小オーケストレーション例から始めてください。

- 🇬🇧 [English の最小オーケストレーション例](examples/minimal-orchestration.en.md)
- 🇯🇵 [日本語の最小オーケストレーション例](examples/minimal-orchestration.ja.md)
- 🇨🇳 [简体中文最小编排示例](examples/minimal-orchestration.zh-CN.md)

3 つの例は相互にリンクしています。今後の拡張は
[FUTURE_WORK.md](FUTURE_WORK.md) に記録します。

## タイトルプロトコル

下流タスクのタイトルは次の形式です。

`Constellary · <TaskID> · <Role> · <ShortGoal>`

ホストのタイトル予算は NFC 正規化後の Unicode code point 34 個です。NFC Unicode
normalization を適用し、余分な空白をまとめ、作成前に short goal を決定的に圧縮します。
プロジェクト名、TaskID、role は保持し、作成後にホストが返した/表示した actual
title を検証します。暗黙の切り詰めは受け入れません。短縮例は
`Constellary · T01 · 实现 · Desktop适配` で、review、repair、re-review には
`T01-R1`、`T01-F1`、`T01-R2` を使います。

## 実行時のデフォルト

実装 worker と独立 reviewer を含む全下流 role は、デフォルトで Luna Max、
つまり `gpt-5.6-luna` と `max` reasoning を使用します。現在のユーザー指示または
プロジェクト設定で、確認を繰り返さず model や reasoning を override できます。
Skill が reviewer を黙って昇格させることはありません。

実装と review は必ず別の新しい独立タスクで行います。review はデフォルトで
read-only です。修正は新しい実装タスクにします。sidebar-visible peer の論理的な
対応付けには creator identity、source thread、project context、task ledger、
report route を使います。

## レポート、イベント待機、ポーリング

すべての worker は終了前に直属 coordinator へ構造化された terminal report を
能動的に送ります。worker タスク内にだけ残る結果は配信済みではありません。親は
一致する message、completion、blocker、failure、user event を待機し、変更のない
タスクを routine polling しません。`task_id` と `thread_id` で対応付け、matching
completion event を重複排除し、`report_received` と review verdict、`review_source`
を分離します。

## 実行環境

調整面とファイル実行環境は別の判断です。公開ポリシーは
`execution_environment: auto_safe` です。準備済みの isolated copy または
serialized single-writer には Local、Git リポジトリでの同時書き込みや重複リスク
には Worktree を使います。ユーザーは override できます。安全な分離がなければ
serialize するか `BLOCKED` と報告します。

## 将来の CLI Adapter

CLI は `v2.0.0` ではサポートも実行もしません。[FUTURE_WORK.md](FUTURE_WORK.md)
に、明示的 opt-in の lifecycle supervision、cleanup、structured report transport、
identity、concurrency、reviewer 作成、security、cross-platform、end-to-end 検証を
記録しています。Desktop の自動 fallback にはしません。

## 検証

リポジトリのルートから決定的な contract と hygiene のチェックを実行します。

```text
python -B scripts/validate_package.py
```

チェック対象には Skill contract、3 言語リンク、machine-specific path、live task
または project ID、secret-shaped value、未解決 authoring marker、壊れた Skill
reference、old-name residue、cache artifact が含まれます。`review_source` と
`report_received` の契約も確認します。

## License

このリポジトリは [MIT License](LICENSE) で公開されています。
