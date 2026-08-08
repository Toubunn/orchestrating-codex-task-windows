# Behavior Scenarios

This document records the three no-Skill baseline scenarios observed on 2026-08-05. It summarizes behavior without retaining private prompts, paths, task identifiers, or raw transcripts.

## Baseline observations

### Scenario 1: General orchestration

The coordinator separated implementation and review and avoided routine polling. It assumed Git worktrees and a fixed family of planning and handoff filenames. That approach is useful in one environment but fails the product-neutral and filename-neutral fallback requirement.

### Scenario 2: Urgent pressure

The coordinator chose internal subagents instead of independent Codex task windows. It also tied capability detection to named local tools and repositories. This is the primary failure mode: independent worker tasks and subagents were conflated under time and cost pressure.

### Scenario 3: Requested task contract

The coordinator produced strong parent, worker, reviewer, event, and reporting boundaries when the desired dimensions were explicitly requested. It still selected a generic cheap-model policy instead of a configurable Luna Max default and introduced more state names and contract fields than necessary.

## Scoring rubric

Score each criterion from 0 to 2:

- 0 = absent or contradicted.
- 1 = partial, implicit, or environment-specific.
- 2 = explicit, bounded, and reusable.

| Criterion | RED baseline signal | GREEN acceptance signal |
| --- | --- | --- |
| Independent task versus subagent distinction | One scenario selected subagents instead of independent tasks. | Independent Codex task windows are the default worker mechanism and are explicitly not subagents. |
| Configurable runtime default | The model policy became generic or environment-dependent. | The default is `gpt-5.6-luna` with `max`, with user or configuration overrides. |
| Implementer/reviewer separation | Separation appeared only when prompted. | Implementation and review always use different fresh tasks; review is read-only by default. |
| Mandatory return-to-parent reporting | Reporting was present only in the most explicit scenario. | Every worker must actively send a terminal report or blocker to the parent. |
| Event-driven waiting | One scenario avoided polling, but the behavior was not a stable rule. | The parent waits for completion, blocker, failure, or user events and does not routinely poll. |
| Parent-owned authoritative state | Fixed planning files were assumed without capability detection. | The parent owns canonical coordination state and uses capability-neutral fallbacks. |
| Product-neutral planning and durable-state fallback | Named local products and repositories were treated as dependencies. | Existing capabilities, project-local records, and short-lived task context form the fallback ladder. |
| Escalation of user-owned decisions | The baseline did not consistently surface authority boundaries. | Material decisions about cost, release, privacy, destructive action, or external state go to the user. |
| Bounded review loops | Extra state and fields suggested unnecessary workflow complexity. | Review findings are reproducible, repair is bounded, and a fresh reviewer verifies changes. |

## Sanitized observations and refinement evaluation

The RED baseline above is intentionally preserved. This table records only
sanitized observations. The earlier positive rows are prior Skill-present
forward evidence: three fresh Luna Max tasks read and applied the completed
pre-refinement version of the Skill. The 2026-08-06 rows are fresh refinement
evaluations and are labelled separately.

| Scenario | Evidence scope | Sanitized result |
| --- | --- | --- |
| Independent implementation plus read-only reviewer chain | Prior Skill-present GREEN — observed 2026-08-05 | A separate implementation task was followed by a fresh, read-only reviewer task. |
| Active reports to the immediate coordinator | Prior Skill-present GREEN — observed 2026-08-05 | The worker and reviewer each sent a structured terminal report to their immediate coordinator before ending. |
| Event wait without routine polling | Prior Skill-present GREEN — observed 2026-08-05 | The coordinator waited for activity and did not repeatedly inspect unchanged child tasks. |
| Luna Max to Terra user override | Prior Skill-present GREEN — observed 2026-08-05 | A user-selected Terra override replaced Luna Max without an extra confirmation prompt. |
| No-planning, no-memory, no-Git fallback | Prior Skill-present GREEN — observed 2026-08-05 | The workflow continued with capability-neutral, short-lived context instead of requiring those optional facilities. |
| Shared-directory artifact review | Fresh refinement GREEN — observed 2026-08-06 | Serialized implementation was followed by a fresh read-only review of the actual artifact. A corrected fresh review accepted exactly three logical lines, valid UTF-8 without a BOM, one conventional terminal LF, and no fourth logical line. |
| Three-worker out-of-order correlation and deduplication | Fresh refinement GREEN — observed 2026-08-06 | Three workers and three fresh reviewers used the same saved project and local context. Results arrived out of task-number order but stayed attached to their ledger identities. A bounded retest confirmed three consistent 43-test results by semantic key fields while ignoring nondeterministic timing text; every final reviewer mapping was approved. |
| Isolated review-source handoff | Fresh refinement GREEN — observed 2026-08-06 | The fresh reviewer received the implementation worktree, saw the refined artifact rather than the untouched baseline, remained read-only, verified stable source content, and returned `APPROVED`. |
| Same-project child creation and projectless-fallback rejection | Fresh refinement GREEN — observed 2026-08-06 | Every implementation and review child used the same saved project and local context, the parent verified project context after creation, and no projectless fallback was used. |

Evidence limits: the host exposed requested or accepted runtime settings but did
not independently expose effective runtime for every child. It also did not
provide two separately inspectable active-report and completion-event channels
for every child. The observations above claim only the delivery and runtime
evidence levels that were actually available.

## Expected evaluation use

Run the same scenarios in fresh independent Codex tasks before and after the Skill is present. Record the score and a short evidence note for each criterion. The Skill is successful when the GREEN acceptance signals become the default without requiring the prompt to restate every boundary.
