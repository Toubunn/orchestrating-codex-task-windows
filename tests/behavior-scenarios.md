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

## Expected evaluation use

Run the same scenarios in fresh independent Codex tasks before and after the Skill is present. Record the score and a short evidence note for each criterion. The Skill is successful when the GREEN acceptance signals become the default without requiring the prompt to restate every boundary.
