from __future__ import annotations

import re
import unicodedata
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

import scripts.validate_package as package_validator


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "constellary"
SKILL_MD = SKILL / "SKILL.md"
CONSTELLARY_SKILL = SKILL
CONSTELLARY_SKILL_MD = SKILL_MD


def read(path: Path) -> str:
    """Return empty text for an uninitialized package so RED is assertion-based."""
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def normalize(text: str) -> str:
    return " ".join(text.casefold().replace("’", "'").split())


def markdown_section(text: str, heading: str) -> str:
    """Extract one authoritative Markdown section, ignoring fenced headings."""
    wanted = normalize(heading)
    active = False
    active_level = 0
    fenced = False
    body: list[str] = []

    for line in text.splitlines():
        fence = bool(re.match(r"^\s*```", line))
        match = None if fenced else re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            level = len(match.group(1))
            title = normalize(match.group(2))
            if active and level <= active_level:
                return "\n".join(body)
            if not active and title == wanted:
                active = True
                active_level = level
                continue
        if active:
            body.append(line)
        if fence:
            fenced = not fenced
    return "\n".join(body) if active else ""


def fenced_schema(section: str) -> str:
    """Return the first YAML schema fenced inside an authoritative section."""
    for match in re.finditer(
        r"(?ms)^```(?P<language>yaml|yml)\s*\r?\n(?P<body>.*?)^```[ \t]*$",
        section,
    ):
        return match.group("body")
    return ""


def schema_fields(schema: str) -> set[str]:
    return set(re.findall(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_-]*):", schema))


# Discovery deliberately accepts bounded same-line title-like candidates. Strict
# title validation below owns raw NFC, four-part, separator, and budget checks.
TITLE_EXAMPLE_PATTERN = re.compile(
    r"(?P<title>Constellary[^\S\r\n`\"\\]*·[^\S\r\n`\"\\]*"
    r"T\d+(?:-(?:R|F)\d+)?"
    r"[^\r\n`\"\\]*)"
)
EXPECTED_TITLE_COMPONENTS = {
    "T01": ("实现", "Desktop适配"),
    "T01-R1": ("审查", "适配"),
    "T01-F1": ("修复", "适配"),
    "T01-R2": ("复审", "适配"),
}
NO_PROJECT_TERM = "project" + "less"
NO_PROJECT_CONTRADICTION_PATTERNS = (
    r"\b(?:every|all)\s+(?:child|children|task|tasks)\b.{0,80}\b"
    + "project"
    + "less"
    + r"\b",
    r"\b(?:no-file|fileless)\b.{0,80}\b"
    + "project"
    + "less"
    + r"\b",
    r"\b(?:project|coordination)\b.{0,80}\b"
    + "project"
    + "less"
    + r"\b",
)


LEDGER_CONTRADICTION_PATTERNS = (
    r"\b(?:arrival|completion) order\b.{0,80}\b(?:determines|controls|assigns)\b.{0,40}\bownership\b",
    r"\bownership\b.{0,80}\b(?:assigned|determined|controlled)\b.{0,80}\b(?:whichever|first)\b",
    r"\b(?:both|two)\b.{0,60}\b(?:terminal|completion)\b.{0,60}\b(?:results?|states?)\b.{0,40}\b(?:retain|kept|recorded)\b",
)

PROJECT_CONTRADICTION_PATTERNS = (
    *NO_PROJECT_CONTRADICTION_PATTERNS,
    r"\b(?:verification|verify(?:ing)? the child)\b.{0,40}\b(?:optional|not required|unnecessary)\b",
    r"\b(?:silently|quietly)\b.{0,80}\b(?:fallback|fall\s+back)\b",
)

NOTIFICATION_CONTRADICTION_PATTERNS = (
    r"\broutine polling\b.{0,40}\b(?:required|mandatory|must)\b",
    r"\b(?:message|report)\b.{0,100}\b(?:and|with)\b.{0,100}\bcompletion event\b.{0,100}\b(?:separate|two|individually)\b.{0,40}\bresults?\b",
    r"\bcompletion event\b.{0,100}\b(?:alone|by itself|on its own)\b.{0,60}\b(?:sufficient|enough)\b.{0,80}\bbounded collection\b.{0,40}\b(?:optional|unnecessary|not required)\b",
    r"\b(?:one|a single) bounded collection\b.{0,100}\bwithout\b.{0,60}\bcompletion(?:-event)? wake-up\b",
)

REVIEW_CONTRADICTION_PATTERNS = (
    r"\bimplementer's reasoning\b.{0,40}\b(?:is|remains)\s+(?:required|mandatory|necessary)\b",
    r"\b(?:source|review source)\b.{0,100}\b(?:missing|absent|stale|outdated)\b.{0,100}\b(?:review|assess|inspect)\b.{0,80}\bbaseline\b",
)

ROUTING_IDENTITY_CONTRADICTION_PATTERNS = (
    r"\b(?:(?:must|may|should)\s+(?!not\b|never\b)|always\s+|says to\s+)copy\b.{0,80}\b(?:incoming\s+)?source_thread_id\b.{0,80}\bcoordinator_task_id\b",
    r"(?<!not )(?<!never )\b(?:use|substitute|treat)\b.{0,80}\b(?:root|parent)\s+(?:task\s+)?id\b.{0,80}\bcoordinator_task_id\b",
    r"\bsource_thread_id\b.{0,80}\b(?:is|means|identifies)\b(?!(?:\s+\w+){0,4}\s+(?:not|never)\b).{0,40}\bcurrent task(?:'s)? (?:own )?id\b",
    r"\bexplicit direct coordinator id\b.{0,30}\b(?:is\s+(?!not\b|never\b)(?:allowed|permitted)|(?:may|can|should)\s+(?!not\b|never\b)(?:be\s+)?used)\b.{0,100}\b(?:unconfirmed|not confirmed|without\b.{0,30}\bconfirm|manually transcribed|not passed verbatim)",
    r"\bimplicit routing\b.{0,80}\bunavailable\b.{0,80}\bcoordinator id\b.{0,50}\bunconfirmed\b.{0,80}(?<!not )(?<!never )\b(?:skip|omit|avoid|bypass)\b.{0,80}\b(?:completion-event wake-up|completion event|bounded collection)\b",
    r"\broot-only channel\b.{0,50}(?<!not )(?<!never )\b(?:replaces?|supersedes?)\b.{0,80}\bdirect delivery\b.{0,40}\bimmediate coordinator\b",
    r"\broot-only channel\b.{0,80}\bcan stand in for\b.{0,80}\bdirect delivery\b.{0,40}\bimmediate coordinator\b",
)

PERMISSION_CONTRADICTION_PATTERNS = (
    r"\bfull(?:/| or )unrestricted access\b.{0,80}\b(?:still|always|must|should)\b(?!\s+(?:not|never)\b).{0,40}\b(?:request|ask(?:ing)? for)\b.{0,40}\b(?:elevation|approval)\b",
    r"\bfull(?:/| or )unrestricted access\b(?![^.]{0,80}\b(?:not|never)\b)[^.]{0,80}\b(?:requires?|needs?)\b.{0,40}\b(?:elevation|approval)\b",
    r"\bcommand(?: or process)? failure\b.{0,80}(?<!not )(?<!never )\b(?:proves|is evidence of|means)\b.{0,60}\bmissing permission\b",
    r"\b(?:must|should|always)\b(?!\s+(?:not|never)\b).{0,40}\b(?:reconfirm|confirm again|repeat confirmation)\b.{0,80}\b(?:granted|existing) authority\b",
)


def has_forbidden(normalized_text: str, patterns: tuple[str, ...]) -> bool:
    """Reject only the small, explicit contradiction patterns listed by a contract."""
    return any(re.search(pattern, normalized_text, flags=re.IGNORECASE) is not None for pattern in patterns)


def section_contains(
    text: str,
    heading: str,
    phrases: tuple[str, ...],
    forbidden: tuple[str, ...] = (),
) -> bool:
    section = markdown_section(text, heading)
    normalized = normalize(section)
    return bool(section) and all(normalize(phrase) in normalized for phrase in phrases) and not has_forbidden(
        normalized, forbidden
    )


def contract_matches(
    text: str,
    heading: str,
    fields: tuple[str, ...] = (),
    schema_fragments: tuple[str, ...] = (),
    phrases: tuple[str, ...] = (),
    forbidden: tuple[str, ...] = (),
) -> bool:
    section = markdown_section(text, heading)
    schema = fenced_schema(section)
    normalized_section = normalize(section)
    normalized_schema = normalize(schema)
    return (
        bool(section)
        and (not fields and not schema_fragments or bool(schema))
        and set(fields).issubset(schema_fields(schema))
        and all(normalize(fragment) in normalized_schema for fragment in schema_fragments)
        and all(normalize(phrase) in normalized_section for phrase in phrases)
        and not has_forbidden(normalized_section, forbidden)
    )


KEYWORD_DECOY = """
# Keyword-only decoy

## Unrelated notes

The task ledger mentions task_id, thread_id, depends_on, report_received,
    review_source, and deduplicate. Same registered project, no-file, explicit
    user request, and verify the child are all terms in this note. A worker actively
sends a report, an event-driven wait sees whichever arrives first, and the text
says does not routinely poll. A reviewer can mention shared_workspace,
worktree, commit, branch, diff, the actual artifact, and the implementer's
reasoning without making any of those relationships authoritative.

## Contradictory notes

Arrival order determines ownership. Every child uses an unverified project
context, the child is never verified, routine polling is required, and the reviewer relies on the
implementer's reasoning instead of the original acceptance criteria.

```yaml
task_id: DECOY
thread_id: DECOY-THREAD
depends_on: none
report_received: false
review_source: fake
```
"""


CONTRADICTORY_LEDGER_DECOY = """
## Dispatch and collect

This broken example says arrival order does not determine ownership, matches
every message and completion event by task_id and thread_id, and can deduplicate
a matching completion event. It then contradicts itself by saying arrival order
determines ownership and terminal duplicates must be retained.

```yaml
task_id: DECOY
thread_id: DECOY-THREAD
depends_on: none
report_received: false
review_source: pending
```
"""


PARAPHRASED_LEDGER_DECOY = """
## Dispatch and collect

The task ledger matches every message and completion event by task_id and
thread_id, can deduplicate a matching completion event, and says arrival order
does not determine ownership. In the counter-rule, ownership is assigned to
whichever completion arrives first.

```yaml
task_id: DECOY
thread_id: DECOY-THREAD
depends_on: none
report_received: false
review_source: pending
```
"""


ADVERSARIAL_PROJECT_DECOY = f"""
## Project context contract

The same project rule says children inherit the current registered project,
verifies the child-creation result before considering dispatch complete, and
no-file work still retains that project context. The coordinator stops dispatch
rather than silently degrading. The opposing rule says every child is
{NO_PROJECT_TERM} and a failed selection may quietly fall back.

```yaml
project_context:
  kind: project
  project_id: CURRENT_PROJECT
  environment: worktree
```
"""


ADVERSARIAL_NOTIFICATION_DECOY = """
## Combined notification protocol

The worker actively sends the terminal report and a completion event; whichever
arrives first wakes the parent, which records one terminal result, deduplicates
the other, and does not permit routine polling. The opposing rule says routine
polling is required, and the report and completion event are recorded as two
separate terminal results.
"""


ADVERSARIAL_NOTIFICATION_PARTIAL_REVERSALS = (
    """
## Combined notification protocol

The worker actively sends the terminal report and a completion event; whichever
arrives first wakes the parent, which records one terminal result, deduplicates
the other, and does not permit routine polling. The opposing rule says the
completion event alone is sufficient, so bounded collection is optional.
""",
    """
## Combined notification protocol

The worker actively sends the terminal report and a completion event; whichever
arrives first wakes the parent, which records one terminal result, deduplicates
the other, and does not permit routine polling. The opposing rule says one
bounded collection is performed without a completion-event wake-up.
""",
)


ADVERSARIAL_REVIEW_DECOY = """
## Review task contract

The reviewer receives the original acceptance criteria and the actual artifact
through review_source, and does not need the implementer's reasoning. The
opposing rule says the implementer's reasoning is required; when the source is
absent or stale, the reviewer may still assess the baseline.

```yaml
acceptance_criteria: ORIGINAL_CRITERIA
review_source:
  kind: shared_workspace
  locator: current_project_root
```
"""


ADVERSARIAL_ROUTING_IDENTITY_DECOY = """
## Nested coordinator routing

Machine-provided source_thread_id in the current delegation envelope identifies
the parent task that created the current task, not the current task's own ID.
Do not copy an incoming source_thread_id or root ID into a child brief as
coordinator_task_id. Prefer the host-created implicit reply-to-source route.
Use an explicit direct ID only when the current coordinator's exact ID was
confirmed by a machine result or independent query and passed verbatim. A
worker whose send tool requires an ID uses the exact source_thread_id from its
own envelope, not a manually transcribed or guessed ID from the brief. The
opposing rule says to copy the incoming source_thread_id into
coordinator_task_id whenever the current coordinator's own ID is unknown. It
also says an explicit direct coordinator ID is allowed even when the current
coordinator's exact ID is unconfirmed. When implicit routing is unavailable and
the coordinator ID is unconfirmed, it says to skip the completion-event wake-up
and bounded collection. Finally, it says a root-only channel replaces direct
delivery to the immediate coordinator. It also permits a machine-confirmed ID
that was manually transcribed instead of passed verbatim.
"""


ADVERSARIAL_PERMISSION_DECOY = """
## Granted authority and command failures

Before attempting elevation, inspect the granted authority or permission
profile. Under full/unrestricted access, do not request elevation or approval.
Command or process failure alone is not evidence of missing permission; first
diagnose cwd, path, quoting, shell, and process startup. Request user authority
only when a new authority is actually missing and required by the task, and do
not reconfirm authority already granted. The opposing rule says full/unrestricted
access still requires asking for approval, because command failure proves
missing permission.
"""


ROUTING_RELATIONSHIP_REVERSALS = (
    "An explicit direct coordinator ID is allowed even when the current coordinator's exact ID is unconfirmed.",
    "An explicit direct coordinator ID is allowed when machine-confirmed but manually transcribed instead of passed verbatim.",
    "When implicit routing is unavailable and the coordinator ID is unconfirmed, skip the completion-event wake-up and bounded collection.",
    "A root-only channel replaces direct delivery to the immediate coordinator.",
    "A root-only channel can stand in for direct delivery to the immediate coordinator.",
)


CORRECT_NEGATED_RULES = (
    (
        "source_thread_id is definitively not the current task's own ID",
        ROUTING_IDENTITY_CONTRADICTION_PATTERNS,
    ),
    (
        "A worker must not use a root task ID as coordinator_task_id.",
        ROUTING_IDENTITY_CONTRADICTION_PATTERNS,
    ),
    (
        "An explicit direct coordinator ID is not allowed when the current coordinator's exact ID is unconfirmed.",
        ROUTING_IDENTITY_CONTRADICTION_PATTERNS,
    ),
    (
        "When implicit routing is unavailable and the coordinator ID is unconfirmed, do not skip the completion event and bounded collection.",
        ROUTING_IDENTITY_CONTRADICTION_PATTERNS,
    ),
    (
        "A root-only channel must not replace direct delivery to the immediate coordinator.",
        ROUTING_IDENTITY_CONTRADICTION_PATTERNS,
    ),
    (
        "Full/unrestricted access should never require approval.",
        PERMISSION_CONTRADICTION_PATTERNS,
    ),
    (
        "Full/unrestricted access is not something that requires approval.",
        PERMISSION_CONTRADICTION_PATTERNS,
    ),
    (
        "A worker must not reconfirm already granted authority.",
        PERMISSION_CONTRADICTION_PATTERNS,
    ),
)


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
        self.assertRegex(text, r"(?ms)^---\s*\nname: constellary\s*$")
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

    def test_downstream_concurrency_has_a_user_adjustable_hard_ceiling(self) -> None:
        phrases = (
            "at most six downstream windows",
            "seven total including the parent",
            "user may adjust the limit",
            "hard ceiling",
            "start another batch only after",
            "must never be exceeded",
        )
        self.assertTrue(
            section_contains(
                read(SKILL_MD),
                "Dispatch and collect",
                phrases=phrases,
                forbidden=(
                    "may exceed the active limit",
                    "start another batch before the current batch ends",
                ),
            )
        )

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

    def test_parallel_work_is_correlated_and_deduplicated_by_task_id(self) -> None:
        self.assertTrue(
            contract_matches(
                read(SKILL_MD),
                "Dispatch and collect",
                fields=("task_id", "thread_id", "depends_on", "report_received", "review_source"),
                phrases=(
                    "task ledger",
                    "arrival order does not determine ownership",
                    "matches every message and completion event by task_id and thread_id",
                    "deduplicate a matching completion event",
                ),
                forbidden=("arrival order determines ownership",),
            )
        )

    def test_children_default_to_the_same_codex_project(self) -> None:
        self.assertTrue(
            contract_matches(
                read(SKILL / "references" / "task-contracts.md"),
                "Project context contract",
                fields=("project_context", "kind", "project_id", "environment"),
                schema_fragments=(
                    "kind: project",
                    "project_id: CURRENT_PROJECT",
                    "environment: worktree",
                ),
                phrases=(
                    "same registered project",
                    "children inherit the current registered project",
                    "verifies the child-creation result",
                    "before considering dispatch complete",
                    "no-file work still retains that project context",
                    "stops dispatch rather than silently degrading",
                ),
                forbidden=PROJECT_CONTRADICTION_PATTERNS,
            )
        )

    def test_active_report_and_event_wait_are_complementary(self) -> None:
        self.assertTrue(
            section_contains(
                read(SKILL / "references" / "capability-fallbacks.md"),
                "Combined notification protocol",
                phrases=(
                    "actively sends the terminal report",
                    "completion event",
                    "whichever arrives first wakes the parent",
                    "records one terminal result",
                    "deduplicates the other",
                    "does not permit routine polling",
                ),
                forbidden=("routine polling is required",),
            )
        )

    def test_reviewer_receives_the_real_artifact_without_implementer_reasoning(self) -> None:
        self.assertTrue(
            contract_matches(
                read(SKILL / "references" / "task-contracts.md"),
                "Review task contract",
                fields=("acceptance_criteria", "review_source"),
                schema_fragments=(
                    "kind: shared_workspace",
                    "locator: current_project_root",
                ),
                phrases=(
                    "original acceptance criteria",
                    "actual artifact",
                    "does not need the implementer's reasoning",
                ),
                forbidden=("implementer's reasoning is required",),
            )
        )
        self.assertTrue(
            section_contains(
                read(SKILL / "references" / "capability-fallbacks.md"),
                "Review source branches",
                phrases=(
                    "shared directory + serialized implementation/review",
                    "reviewer reads the current files directly",
                    "isolated worktree/copy",
                    "worktree, commit, branch, handoff, or diff",
                    "contains the implementation",
                ),
            )
        )

    def test_structure_aware_helpers_reject_keyword_decoys(self) -> None:
        required_keywords = (
            "task ledger",
            "task_id",
            "thread_id",
            "depends_on",
            "report_received",
            "review_source",
            "deduplicate",
            "same registered project",
            "no-file",
            "explicit user request",
            "verify the child",
            "actively sends",
            "event-driven wait",
            "does not routinely poll",
            "whichever arrives first",
            "shared_workspace",
            "worktree",
            "commit",
            "branch",
            "diff",
            "actual artifact",
            "implementer's reasoning",
        )
        self.assertEqual([], [term for term in required_keywords if normalize(term) not in normalize(KEYWORD_DECOY)])
        self.assertFalse(
            contract_matches(
                KEYWORD_DECOY,
                "Dispatch and collect",
                fields=("task_id", "thread_id", "depends_on", "report_received", "review_source"),
                phrases=("arrival order does not determine ownership", "deduplicate"),
            )
        )
        self.assertFalse(
            contract_matches(
                KEYWORD_DECOY,
                "Project context contract",
                fields=("project_context", "kind", "project_id", "environment"),
            )
        )
        self.assertFalse(
            section_contains(
                KEYWORD_DECOY,
                "Combined notification protocol",
                phrases=("actively sends", "whichever arrives first"),
            )
        )
        self.assertFalse(
            contract_matches(
                KEYWORD_DECOY,
                "Review task contract",
                fields=("acceptance_criteria", "review_source"),
            )
        )
        self.assertFalse(
            contract_matches(
                CONTRADICTORY_LEDGER_DECOY,
                "Dispatch and collect",
                fields=("task_id", "thread_id", "depends_on", "report_received", "review_source"),
                phrases=(
                    "arrival order does not determine ownership",
                    "matches every message and completion event by task_id and thread_id",
                    "deduplicate a matching completion event",
                ),
                forbidden=LEDGER_CONTRADICTION_PATTERNS,
            )
        )

    def test_contract_helper_rejects_project_context_contradiction_paraphrase(self) -> None:
        self.assertFalse(
            contract_matches(
                ADVERSARIAL_PROJECT_DECOY,
                "Project context contract",
                fields=("project_context", "kind", "project_id", "environment"),
                schema_fragments=(
                    "kind: project",
                    "project_id: CURRENT_PROJECT",
                    "environment: worktree",
                ),
                phrases=(
                    "same registered project",
                    "children inherit the current registered project",
                    "verifies the child-creation result",
                    "before considering dispatch complete",
                    "no-file work still retains that project context",
                    "stops dispatch rather than silently degrading",
                ),
                forbidden=PROJECT_CONTRADICTION_PATTERNS,
            )
        )

    def test_section_helper_rejects_notification_contradiction_paraphrase(self) -> None:
        self.assertFalse(
            section_contains(
                ADVERSARIAL_NOTIFICATION_DECOY,
                "Combined notification protocol",
                phrases=(
                    "actively sends the terminal report",
                    "completion event",
                    "whichever arrives first wakes the parent",
                    "records one terminal result",
                    "deduplicates the other",
                    "does not permit routine polling",
                ),
                forbidden=NOTIFICATION_CONTRADICTION_PATTERNS,
            )
        )

    def test_section_helper_rejects_notification_partial_reversals(self) -> None:
        phrases = (
            "actively sends the terminal report",
            "completion event",
            "whichever arrives first wakes the parent",
            "records one terminal result",
            "deduplicates the other",
            "does not permit routine polling",
        )
        for fixture in ADVERSARIAL_NOTIFICATION_PARTIAL_REVERSALS:
            with self.subTest(fixture=fixture):
                self.assertFalse(
                    section_contains(
                        fixture,
                        "Combined notification protocol",
                        phrases=phrases,
                        forbidden=NOTIFICATION_CONTRADICTION_PATTERNS,
                    )
                )

    def test_contract_helper_rejects_review_baseline_paraphrase(self) -> None:
        self.assertFalse(
            contract_matches(
                ADVERSARIAL_REVIEW_DECOY,
                "Review task contract",
                fields=("acceptance_criteria", "review_source"),
                schema_fragments=(
                    "kind: shared_workspace",
                    "locator: current_project_root",
                ),
                phrases=(
                    "original acceptance criteria",
                    "actual artifact",
                    "does not need the implementer's reasoning",
                ),
                forbidden=REVIEW_CONTRADICTION_PATTERNS,
            )
        )

    def test_contract_helper_rejects_ledger_ownership_paraphrase(self) -> None:
        self.assertFalse(
            contract_matches(
                PARAPHRASED_LEDGER_DECOY,
                "Dispatch and collect",
                fields=("task_id", "thread_id", "depends_on", "report_received", "review_source"),
                phrases=(
                    "arrival order does not determine ownership",
                    "matches every message and completion event by task_id and thread_id",
                    "deduplicate a matching completion event",
                ),
                forbidden=LEDGER_CONTRADICTION_PATTERNS,
            )
        )

    def test_nested_coordinator_identity_uses_machine_reply_routes(self) -> None:
        phrases = (
            "source_thread_id in the current delegation envelope identifies the parent task that created the current task",
            "not the current task's own ID",
            "do not copy an incoming source_thread_id or root ID into a child brief as coordinator_task_id",
            "host-created implicit reply-to-source",
            "current coordinator's exact ID was confirmed by a machine result or independent query and passed verbatim",
            "uses the exact source_thread_id from its own envelope",
            "not a manually transcribed or guessed ID from the brief",
            "completion event and one bounded collection",
            "degraded routing",
            "blocked",
        )
        text = read(SKILL / "references" / "task-contracts.md")
        self.assertTrue(
            section_contains(
                text,
                "Nested coordinator routing",
                phrases=phrases,
                forbidden=ROUTING_IDENTITY_CONTRADICTION_PATTERNS,
            )
        )
        self.assertFalse(
            section_contains(
                ADVERSARIAL_ROUTING_IDENTITY_DECOY,
                "Nested coordinator routing",
                phrases=phrases[:-3],
                forbidden=ROUTING_IDENTITY_CONTRADICTION_PATTERNS,
            )
        )

    def test_granted_authority_prevents_redundant_permission_prompts(self) -> None:
        phrases = (
            "before attempting elevation, inspect the granted authority or permission profile",
            "under full/unrestricted access, do not request elevation or approval",
            "command or process failure alone is not evidence of missing permission",
            "diagnose cwd, path, quoting, shell, and process startup",
            "only when a new authority is actually missing and required by the task",
            "do not reconfirm authority already granted",
        )
        text = read(SKILL / "references" / "capability-fallbacks.md")
        self.assertTrue(
            section_contains(
                text,
                "Granted authority and command failures",
                phrases=phrases,
                forbidden=PERMISSION_CONTRADICTION_PATTERNS,
            )
        )
        self.assertFalse(
            section_contains(
                ADVERSARIAL_PERMISSION_DECOY,
                "Granted authority and command failures",
                phrases=phrases,
                forbidden=PERMISSION_CONTRADICTION_PATTERNS,
            )
        )

    def test_routing_patterns_reject_each_relationship_reversal(self) -> None:
        for reversal in ROUTING_RELATIONSHIP_REVERSALS:
            with self.subTest(reversal=reversal):
                self.assertTrue(
                    has_forbidden(normalize(reversal), ROUTING_IDENTITY_CONTRADICTION_PATTERNS)
                )

    def test_authoritative_sections_reject_appended_relationship_reversals(self) -> None:
        routing_heading = "Nested coordinator routing"
        routing_section = markdown_section(
            read(SKILL / "references" / "task-contracts.md"), routing_heading
        )
        routing_phrases = (
            "source_thread_id in the current delegation envelope identifies the parent task that created the current task",
            "not the current task's own ID",
            "do not copy an incoming source_thread_id or root ID into a child brief as coordinator_task_id",
            "host-created implicit reply-to-source",
        )
        notification_heading = "Combined notification protocol"
        notification_section = markdown_section(
            read(SKILL / "references" / "capability-fallbacks.md"), notification_heading
        )
        notification_phrases = (
            "actively sends the terminal report",
            "completion event",
            "whichever arrives first wakes the parent",
            "records one terminal result",
            "deduplicates the other",
            "does not permit routine polling",
        )
        cases = (
            *(
                (
                    routing_heading,
                    routing_section,
                    reversal,
                    routing_phrases,
                    ROUTING_IDENTITY_CONTRADICTION_PATTERNS,
                )
                for reversal in ROUTING_RELATIONSHIP_REVERSALS
            ),
            *(
                (
                    notification_heading,
                    notification_section,
                    markdown_section(fixture, notification_heading).split("The opposing rule says", 1)[-1],
                    notification_phrases,
                    NOTIFICATION_CONTRADICTION_PATTERNS,
                )
                for fixture in ADVERSARIAL_NOTIFICATION_PARTIAL_REVERSALS
            ),
        )
        for heading, section, reversal, phrases, patterns in cases:
            with self.subTest(heading=heading, reversal=reversal):
                fixture = f"## {heading}\n\n{section}\n\n{reversal}"
                self.assertFalse(section_contains(fixture, heading, phrases, patterns))

    def test_routing_and_permission_patterns_accept_correct_negations(self) -> None:
        for rule, patterns in CORRECT_NEGATED_RULES:
            with self.subTest(rule=rule):
                self.assertFalse(has_forbidden(normalize(rule), patterns))

    def test_permission_patterns_reject_direct_full_access_reversal(self) -> None:
        contradiction = "Full/unrestricted access requires approval."
        self.assertTrue(has_forbidden(normalize(contradiction), PERMISSION_CONTRADICTION_PATTERNS))

    def test_main_skill_stays_at_or_below_1500_words(self) -> None:
        words = read(SKILL_MD).split()
        self.assertLessEqual(len(words), 1500)

    def test_environment_mapping_keeps_same_project_coordination_and_safe_overrides(self) -> None:
        text = (read(SKILL_MD) + read(SKILL / "references" / "capability-fallbacks.md")).lower()
        for phrase in (
            "no-file",
            "execution_environment: auto_safe",
            "same registered project",
            "local",
            "worktree",
            "worktree_when_writing",
            "preference, not a prerequisite",
            "isolated copy",
            "non-overlapping write paths",
            "serialized execution",
            "blocked",
            "user may override",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn(NO_PROJECT_TERM, text)

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


    def test_review_source_kind_vocabulary_is_explicit_and_distinguishes_environment(self) -> None:
        contracts = read(SKILL / "references" / "task-contracts.md").lower()
        for kind in (
            "shared_workspace",
            "worktree",
            "copy",
            "commit",
            "branch",
            "handoff",
            "diff",
            "none",
        ):
            with self.subTest(kind=kind):
                self.assertIn(f"`{kind}`", contracts)
        self.assertIn("environment is not a review source", contracts)


class ConstellaryIdentityTests(unittest.TestCase):
    def test_constellary_skill_directory_and_contract_exist(self) -> None:
        self.assertTrue(CONSTELLARY_SKILL_MD.is_file())
        self.assertTrue((CONSTELLARY_SKILL / "agents" / "openai.yaml").is_file())

    def test_constellary_frontmatter_uses_v2_identity(self) -> None:
        text = read(CONSTELLARY_SKILL_MD)
        self.assertRegex(text, r"(?ms)^---\s*\nname: constellary\s*$")
        self.assertIn("v2.0.0-alpha", text)
        self.assertIn("$constellary", text)

    def test_constellary_interface_uses_display_name_and_invocation(self) -> None:
        text = read(CONSTELLARY_SKILL / "agents" / "openai.yaml")
        self.assertIn('display_name: "Constellary"', text)
        self.assertIn("$constellary", text)


class DesktopRuntimeContractTests(unittest.TestCase):
    def test_v2_runtime_is_deterministically_desktop_required(self) -> None:
        text = read(CONSTELLARY_SKILL_MD).lower()
        required = (
            "coordination_surface: codex_desktop",
            "desktop_required",
            "same registered codex project",
            "create_thread",
            "wait_threads",
            "send_message_to_thread",
            "mark the dispatch blocked",
        )
        self.assertEqual([], [phrase for phrase in required if phrase not in text])

    def test_desktop_creation_verifies_identity_context_title_and_visibility(self) -> None:
        text = read(CONSTELLARY_SKILL_MD).lower()
        required = (
            "thread_id",
            "project_id",
            "host_id",
            "title",
            "sidebar visibility",
            "post-creation",
        )
        self.assertEqual([], [phrase for phrase in required if phrase not in text])

    def test_missing_desktop_capability_blocks_without_terminal_fallback(self) -> None:
        text = read(CONSTELLARY_SKILL_MD).lower()
        required = (
            "missing desktop capability",
            "blocked",
            "no cli fallback",
            "forbidden",
            "codex exec",
            "codex.exe",
            "powershell",
            "pwsh",
            "cmd",
            "windows terminal",
            "start-process",
            "subprocess",
            "background shell",
            "temporary prompt",
            "internal-only agent",
        )
        self.assertEqual([], [phrase for phrase in required if phrase not in text])
        self.assertNotRegex(text, r"(?i)silently\s+(?:fall\s*back|switch)\s+to\s+(?:cli|terminal)")

    def test_behavior_scenarios_include_sanitized_desktop_misrouting_regression(self) -> None:
        scenarios = read(ROOT / "tests" / "behavior-scenarios.md").lower()
        required = (
            "desktop-required regression",
            "same-project sidebar task",
            "terminal worker",
            "blocked",
            "sanitized",
        )
        self.assertEqual([], [phrase for phrase in required if phrase not in scenarios])


class DesktopTitleAndHierarchyTests(unittest.TestCase):
    def _contract_text(self) -> str:
        return read(CONSTELLARY_SKILL_MD) + read(CONSTELLARY_SKILL / "references" / "task-contracts.md")

    def _public_title_examples(self, root: Path = ROOT) -> list[tuple[Path, str]]:
        examples: list[tuple[Path, str]] = []
        for path in package_validator.public_files(root):
            text = package_validator.read_public_text(path)
            for match in TITLE_EXAMPLE_PATTERN.finditer(text):
                examples.append((path, match.group("title")))
        return examples

    def test_title_discovery_scans_extensionless_unknown_files_and_adjacent_separators(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = " · ".join(("Constellary", "T01", "实现", "Desktop" + "适配"))
            review = " · ".join(("Constellary", "T01-R1", "审查", "适配"))
            malformed = canonical.replace(" · 实现", " ·· 实现")
            (root / "LICENSE").write_bytes(
                (canonical + "\n").encode("utf-8") + b"\xff"
            )
            (root / "metadata.json").write_text(review + "\n", encoding="utf-8")
            (root / "malformed.md").write_text(malformed + "\n", encoding="utf-8")

            examples = self._public_title_examples(root)
            by_name = {path.name: title for path, title in examples}

        self.assertIn("LICENSE", by_name)
        self.assertIn("metadata.json", by_name)
        self.assertIn("malformed.md", by_name)

        malformed = by_name["malformed.md"]
        normalized = unicodedata.normalize("NFC", malformed)
        parts = normalized.split(" · ")
        is_strict = (
            malformed == normalized
            and len(parts) == 4
            and malformed == " · ".join(parts)
            and len(normalized) <= 34
        )
        self.assertFalse(is_strict)

    def test_title_discovery_finds_noncanonical_title_like_mutations_for_rejection(self) -> None:
        separator = " " + "·" + " "
        parts = ("Constellary", "T" + "01", "实" + "现", "Desktop" + "适配")
        canonical = separator.join(parts)
        mutations = (
            parts[0] + "  " + "·" + " " + separator.join(parts[1:]),
            parts[0] + separator + "\t" + parts[1] + separator.join(("", *parts[2:])),
            canonical + " " + "·" + " extra",
            separator.join((*parts[:3], "x" * 40)),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                candidates = [match.group("title") for match in TITLE_EXAMPLE_PATTERN.finditer(mutation)]
                self.assertEqual([mutation], candidates)
                normalized = unicodedata.normalize("NFC", candidates[0])
                parts = candidates[0].split(" · ")
                is_strict = (
                    candidates[0] == normalized
                    and len(parts) == 4
                    and candidates[0] == " · ".join(parts)
                    and len(normalized) <= 34
                )
                self.assertFalse(is_strict)

    def test_title_discovery_ignores_schema_placeholders_and_plain_explanations(self) -> None:
        text = (
            "Constellary · <TaskID> · <Role> · <ShortGoal>\n"
            "Constellary coordinates visible tasks."
        )
        candidates = [match.group("title") for match in TITLE_EXAMPLE_PATTERN.finditer(text)]
        self.assertEqual([], candidates)

    def test_title_protocol_has_deterministic_host_budget_and_post_creation_check(self) -> None:
        text = self._contract_text().lower()
        required = (
            "constellary · <taskid> · <role> · <shortgoal>",
            "title budget",
            "max_title_length: 34",
            "34 nfc-normalized unicode code points",
            "unicode normalization",
            "deterministic compression",
            "before creation",
            "post-creation title verification",
            "actual title",
            "mismatch",
            "blocked",
        )
        self.assertEqual([], [phrase for phrase in required if phrase not in text])

    def test_all_public_title_examples_are_nfc_bounded_and_structured(self) -> None:
        examples = self._public_title_examples()
        self.assertTrue(examples, "public title examples must be discoverable")
        seen: set[str] = set()
        for path, title in examples:
            with self.subTest(path=path.relative_to(ROOT), title=title):
                normalized = unicodedata.normalize("NFC", title)
                parts = normalized.split(" · ")
                self.assertLessEqual(len(normalized), 34)
                self.assertEqual(4, len(parts))
                self.assertEqual(title, normalized)
                self.assertEqual(title, " · ".join(parts))
                self.assertEqual(3, title.count(" · "))
                self.assertEqual("Constellary", parts[0])
                self.assertRegex(parts[1], r"^T\d+(?:-(?:R|F)\d+)?$")
                self.assertIn(parts[1], EXPECTED_TITLE_COMPONENTS)
                expected_role, expected_goal = EXPECTED_TITLE_COMPONENTS[parts[1]]
                self.assertEqual(expected_role, parts[2])
                self.assertEqual(expected_goal, parts[3])
                seen.add(parts[1])
        self.assertEqual(set(EXPECTED_TITLE_COMPONENTS), seen)

    def test_title_and_hierarchy_examples_preserve_visible_lineage(self) -> None:
        text = self._contract_text()
        required = (
            "Constellary · T01 · 实现 · Desktop适配",
            "Constellary · T01-R1 · 审查 · 适配",
            "Constellary · T01-F1 · 修复 · 适配",
            "Constellary · T01-R2 · 复审 · 适配",
            "creator_task_id",
            "source_thread_id",
            "same registered project",
            "sidebar-visible",
            "worker-internal",
            "not the primary downstream-task mechanism",
        )
        self.assertEqual([], [phrase for phrase in required if phrase not in text])

    def test_same_registered_project_is_required_for_every_downstream_task(self) -> None:
        contracts = read(CONSTELLARY_SKILL / "references" / "task-contracts.md")
        self.assertTrue(
            contract_matches(
                contracts,
                "Project context contract",
                fields=("project_context", "kind", "project_id", "environment"),
                schema_fragments=(
                    "kind: project",
                    "project_id: CURRENT_PROJECT",
                    "environment: worktree",
                ),
                phrases=(
                    "same registered project",
                    "children inherit the current registered project",
                    "verifies the child-creation result",
                    "before considering dispatch complete",
                    "stops dispatch rather than silently degrading",
                ),
                forbidden=NO_PROJECT_CONTRADICTION_PATTERNS,
            )
        )

        public_fallbacks = []
        for path in package_validator.public_files(ROOT):
            if path.suffix.lower() not in package_validator.TEXT_SUFFIXES:
                continue
            if NO_PROJECT_TERM in path.read_text(encoding="utf-8", errors="replace").casefold():
                public_fallbacks.append(str(path.relative_to(ROOT)))
        self.assertEqual([], public_fallbacks)

    def test_same_registered_project_contract_rejects_no_project_target_fallback(self) -> None:
        no_project_fallback = f"""
## Project context contract

The same registered project is verified before dispatch, but the opposing rule
says every child is {NO_PROJECT_TERM} and may fall back when project selection
fails.

```yaml
project_context:
  kind: project
  project_id: CURRENT_PROJECT
  environment: worktree
```
"""
        self.assertFalse(
            contract_matches(
                no_project_fallback,
                "Project context contract",
                fields=("project_context", "kind", "project_id", "environment"),
                schema_fragments=(
                    "kind: project",
                    "project_id: CURRENT_PROJECT",
                    "environment: worktree",
                ),
                phrases=(
                    "same registered project",
                    "verifies the child-creation result",
                ),
                forbidden=NO_PROJECT_CONTRADICTION_PATTERNS,
            )
        )


if __name__ == "__main__":
    unittest.main()
