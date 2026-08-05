from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
VALIDATOR = ROOT / "scripts" / "validate_package.py"
PUBLIC_FILES = [
    path
    for path in ROOT.rglob("*")
    if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
]
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".txt"}


def public_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in PUBLIC_FILES
        if path.suffix.lower() in TEXT_SUFFIXES
    )


def tracked_files() -> list[Path]:
    if not (ROOT / ".git").exists():
        return []
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return []
    return [ROOT / item for item in result.stdout.decode("utf-8").split("\0") if item]


class PackageHygieneTests(unittest.TestCase):
    def test_repository_entrypoints_exist(self) -> None:
        self.assertTrue(README.is_file(), "README.md must exist")
        self.assertTrue(VALIDATOR.is_file(), "scripts/validate_package.py must exist")

    def test_readme_documents_required_public_contract(self) -> None:
        text = README.read_text(encoding="utf-8") if README.is_file() else ""
        required = [
            "Codex",
            "independent task",
            "gpt-5.6-luna",
            "override",
            "report",
            "python -B scripts/validate_package.py",
        ]
        self.assertEqual([], [term for term in required if term.lower() not in text.lower()])

    def test_no_machine_specific_absolute_paths(self) -> None:
        text = public_text()
        patterns = [
            r"(?i)[a-z]:\\",
            r"(?i)/" + "home/" + r"[^/]+/",
            r"(?i)/" + "Users/" + r"[^/]+/",
        ]
        for pattern in patterns:
            self.assertNotRegex(text, pattern)

    def test_no_live_thread_or_project_ids(self) -> None:
        text = public_text()
        patterns = [
            r"(?i)019[0-9a-f-]{20,}",
            r"(?i)local-[0-9a-f]{20,}",
            r"(?i)\b(?:task|project|thread)[-_][0-9a-f]{16,}\b",
        ]
        for pattern in patterns:
            self.assertNotRegex(text, pattern)

    def test_no_secret_shaped_values(self) -> None:
        text = public_text()
        patterns = [
            r"gh[pousr]_[A-Za-z0-9_]{20,}",
            r"sk-[A-Za-z0-9_-]{20,}",
            r"AKIA[0-9A-Z]{16}",
        ]
        for pattern in patterns:
            self.assertNotRegex(text, pattern)

    def test_no_unresolved_authoring_markers(self) -> None:
        text = public_text()
        marker_words = ["".join(parts) for parts in (("T", "ODO"), ("T", "BD"), ("FIX", "ME"))]
        pattern = r"(?i)\b(?:" + "|".join(marker_words) + r")\b"
        self.assertNotRegex(text, pattern)

    def test_skill_references_resolve(self) -> None:
        skill = ROOT / "skills" / "orchestrating-codex-task-windows" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        links = re.findall(r"\[[^]]+\]\((references/[^)]+)\)", text)
        self.assertTrue(links)
        self.assertEqual([], [link for link in links if not (skill.parent / link).is_file()])

    def test_no_cache_artifacts_are_packaged(self) -> None:
        cache_directories = {"__pycache__", ".pytest_cache", ".mypy_cache"}
        cache_suffixes = {".pyc", ".pyo", ".coverage"}

        public_cache_artifacts = [
            path
            for path in PUBLIC_FILES
            if any(part in cache_directories for part in path.parts)
            or path.suffix.lower() in cache_suffixes
        ]
        tracked_cache_artifacts = [
            path
            for path in tracked_files()
            if any(part in cache_directories for part in path.parts)
            or path.suffix.lower() in cache_suffixes
        ]
        self.assertEqual([], [str(path.relative_to(ROOT)) for path in public_cache_artifacts])
        self.assertEqual([], [str(path.relative_to(ROOT)) for path in tracked_cache_artifacts])


if __name__ == "__main__":
    unittest.main()
