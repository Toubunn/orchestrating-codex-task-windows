from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "orchestrating-codex-task-windows"
SKILL_MD = SKILL / "SKILL.md"


def read(path: Path) -> str:
    """Return empty text for an uninitialized package so RED is assertion-based."""
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class SkillContractTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = [
            SKILL_MD,
            SKILL / "agents" / "openai.yaml",
            SKILL / "references" / "task-contracts.md",
            SKILL / "references" / "capability-fallbacks.md",
        ]
        self.assertEqual([], [str(path.relative_to(ROOT)) for path in required if not path.is_file()])

    def test_frontmatter_identifies_the_skill(self) -> None:
        text = read(SKILL_MD)
        self.assertRegex(text, r"(?ms)^---\s*\nname: orchestrating-codex-task-windows\s*$")
        self.assertRegex(text, r"(?m)^description: Use when .+")

    def test_independent_tasks_are_not_described_as_subagents(self) -> None:
        text = read(SKILL_MD).lower()
        self.assertIn("independent codex task", text)
        self.assertIn("not a subagent", text)

    def test_runtime_is_a_configurable_default(self) -> None:
        text = read(SKILL_MD).lower()
        self.assertIn("gpt-5.6-luna", text)
        self.assertIn("max", text)
        self.assertIn("override", text)
        self.assertNotIn("must always use gpt-5.6-luna", text)

    def test_parent_worker_and_reviewer_boundaries_are_present(self) -> None:
        text = read(SKILL_MD)
        for heading in ("Parent coordinator", "Implementation worker", "Independent reviewer"):
            self.assertIn(heading, text)

    def test_event_driven_waiting_and_reporting_are_mandatory(self) -> None:
        text = read(SKILL_MD).lower()
        self.assertIn("event-driven", text)
        self.assertIn("does not routinely poll", text)
        self.assertIn("a result left only in the worker task is not delivered", text)
        self.assertIn("report_required: true", read(SKILL / "references" / "task-contracts.md"))

    def test_capability_and_state_boundaries_are_product_neutral(self) -> None:
        text = (read(SKILL_MD) + read(SKILL / "references" / "capability-fallbacks.md")).lower()
        required = [
            "depends on capabilities, not on a named",
            "strongest suitable option already available",
            "sole owner of authoritative coordination state",
            "workers report updates to the parent",
            "absence of an optional planning or durable-state capability does not block an otherwise authorized task",
        ]
        self.assertEqual([], [phrase for phrase in required if phrase not in text])

    def test_implementation_and_review_are_separate(self) -> None:
        text = read(SKILL_MD).lower()
        self.assertIn("fresh independent reviewer", text)
        self.assertIn("read-only by default", text)

    def test_contract_distinguishes_immediate_coordinator_from_optional_root(self) -> None:
        skill_text = read(SKILL_MD).lower()
        contract_text = read(SKILL / "references" / "task-contracts.md")
        self.assertIn("coordinator_task_id:", contract_text)
        self.assertIn("coordinator_report_channel:", contract_text)
        self.assertIn("root_task_id:", contract_text)
        self.assertIn("root_notification_channel:", contract_text)
        self.assertNotIn("parent_task_id:", contract_text)
        self.assertIn("immediate coordinator", skill_text)
        self.assertIn("optional root", skill_text)
        self.assertIn("cannot replace", skill_text)

    def test_report_route_resolution_is_ordered_and_degrades_honestly(self) -> None:
        text = (read(SKILL_MD) + read(SKILL / "references" / "task-contracts.md")).lower().replace("`", "")
        for phrase in (
            "explicit direct coordinator id",
            "host implicit reply-to-source",
            "one bounded collection after a completion event",
            "degraded routing",
            "only a root channel",
            "must be marked blocked",
        ):
            self.assertIn(phrase, text)
        self.assertIn("must not claim direct", text)

    def test_runtime_claims_use_requested_accepted_and_observed_evidence_levels(self) -> None:
        text = (read(SKILL_MD) + read(SKILL / "references" / "task-contracts.md")).lower().replace("`", "")
        for level in ("requested", "accepted", "observed"):
            self.assertIn(level, text)
        self.assertIn("accepted alone does not prove observed", text)

    def test_environment_mapping_prefers_projectless_or_worktree_and_has_fallbacks(self) -> None:
        text = (read(SKILL_MD) + read(SKILL / "references" / "capability-fallbacks.md")).lower()
        for phrase in (
            "no-file task",
            "projectless",
            "worktree_when_writing",
            "preference, not a prerequisite",
            "isolated copy",
            "non-overlapping write paths",
            "serialized execution",
        ):
            self.assertIn(phrase, text)

    def test_terminal_status_and_review_verdict_are_separate_contracts(self) -> None:
        text = (read(SKILL_MD) + read(SKILL / "references" / "task-contracts.md")).lower()
        for status in ("done", "done_with_concerns", "needs_context", "blocked"):
            self.assertIn(status, text)
        self.assertIn("review verdict", text)
        self.assertIn("approved", text)
        self.assertIn("changes_required", text)
        self.assertNotRegex(text, r"status:" + r"\s*(?:approved|changes_required)")

    def test_live_user_constraints_override_state_preferences(self) -> None:
        text = read(SKILL_MD).lower()
        self.assertIn("forbids file creation", text)
        self.assertIn("current task context", text)
        self.assertIn("without a repeated confirmation prompt", text)

    def test_parent_minimum_verification_covers_delivery_paths_checks_review_and_runtime_evidence(self) -> None:
        text = (read(SKILL_MD) + read(SKILL / "references" / "task-contracts.md")).lower().replace("`", "")
        for phrase in (
            "report delivery and routing",
            "changed paths or none",
            "required checks and evidence",
            "review verdict",
            "blockers and remaining concerns",
            "runtime claim evidence level",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
