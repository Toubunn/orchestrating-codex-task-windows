from __future__ import annotations

import re
import subprocess
from tempfile import TemporaryDirectory
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
VALIDATOR = ROOT / "scripts" / "validate_package.py"
PRIVATE_DIRS = {
    ".git",
    ".planning",
    ".engramory-memory",
    ".work",
    ".tmp",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".txt"}


def is_public_file(path: Path, root: Path) -> bool:
    return path.is_file() and not any(
        part in PRIVATE_DIRS for part in path.relative_to(root).parts
    )


def public_files(root: Path = ROOT) -> list[Path]:
    """Return all public source files without local coordination state."""
    candidates = root.rglob("*")
    return sorted(
        [path for path in candidates if is_public_file(path, root)],
        key=lambda path: path.as_posix(),
    )


def public_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in public_files()
        if path.suffix.lower() in TEXT_SUFFIXES
    )


def tracked_files(root: Path = ROOT) -> list[Path]:
    if not (root / ".git").exists():
        return []
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return []
    return [root / item for item in result.stdout.decode("utf-8").split("\0") if item]


class PackageHygieneTests(unittest.TestCase):
    def test_repository_entrypoints_exist(self) -> None:
        self.assertTrue(README.is_file(), "README.md must exist")
        self.assertTrue((ROOT / "README.ja.md").is_file(), "README.ja.md must exist")
        self.assertTrue((ROOT / "README.zh-CN.md").is_file(), "README.zh-CN.md must exist")
        self.assertTrue(VALIDATOR.is_file(), "scripts/validate_package.py must exist")

    def test_readme_language_versions_cross_link_in_english_japanese_chinese_order(self) -> None:
        expected = ["README.md", "README.ja.md", "README.zh-CN.md"]
        for filename in expected:
            path = ROOT / filename
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            links = re.findall(r"\[[^]]+\]\((README(?:\.ja|\.zh-CN)?\.md)\)", text)
            with self.subTest(filename=filename):
                self.assertEqual(expected, links[:3])

    def test_readme_language_versions_keep_shared_contract_markers(self) -> None:
        markers = [
            "examples/minimal-orchestration.en.md",
            "examples/minimal-orchestration.ja.md",
            "examples/minimal-orchestration.zh-CN.md",
            "FUTURE_WORK.md",
            "gpt-5.6-luna",
            "review_source",
            "report_received",
            "$orchestrating-codex-task-windows",
            "python -B scripts/validate_package.py",
            "MIT License",
        ]
        for filename in ("README.md", "README.ja.md", "README.zh-CN.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertEqual([], [marker for marker in markers if marker not in text])

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
            for path in public_files()
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

    def test_private_coordination_state_is_not_public_package_input(self) -> None:
        private = {".planning", ".engramory-memory", ".work"}
        leaked = [
            str(path.relative_to(ROOT))
            for path in public_files()
            if private.intersection(path.relative_to(ROOT).parts)
        ]
        self.assertEqual([], leaked)

    def test_public_files_source_archive_excludes_private_coordination_dirs(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("public", encoding="utf-8")
            for directory in (".planning", ".engramory-memory", ".work"):
                private = root / directory / "private.md"
                private.parent.mkdir(parents=True)
                private.write_text("private", encoding="utf-8")

            found = {path.relative_to(root) for path in public_files(root)}

        self.assertEqual({Path("README.md")}, found)

    def test_public_files_filters_tracked_private_paths_like_archive_paths(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("public", encoding="utf-8")
            private_paths = [
                root / directory / "private.md"
                for directory in (".planning", ".engramory-memory", ".work")
            ]
            for private in private_paths:
                private.parent.mkdir(parents=True, exist_ok=True)
                private.write_text("private", encoding="utf-8")

            subprocess.run(
                ["git", "-C", str(root), "init", "--quiet"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "add", "--", "."],
                check=True,
                capture_output=True,
            )

            tracked = {
                path.relative_to(root)
                for path in tracked_files(root)
            }
            found = {
                path.relative_to(root)
                for path in public_files(root)
            }

        self.assertEqual(
            {Path("README.md"), Path(".planning/private.md"), Path(".engramory-memory/private.md"), Path(".work/private.md")},
            tracked,
        )
        self.assertEqual({Path("README.md")}, found)


    def test_release_documents_and_mit_license_exist(self) -> None:
        license_path = ROOT / "LICENSE"
        future_work = ROOT / "FUTURE_WORK.md"
        self.assertTrue(license_path.is_file(), "LICENSE must exist before release")
        self.assertIn("MIT License", license_path.read_text(encoding="utf-8"))
        self.assertTrue(future_work.is_file(), "FUTURE_WORK.md must exist")

    def test_readme_links_examples_in_english_japanese_chinese_order(self) -> None:
        readme = README.read_text(encoding="utf-8") if README.is_file() else ""
        expected = [
            "examples/minimal-orchestration.en.md",
            "examples/minimal-orchestration.ja.md",
            "examples/minimal-orchestration.zh-CN.md",
        ]
        links = re.findall(r"\[[^]]+\]\((examples/minimal-orchestration\.[^)]+)\)", readme)
        self.assertEqual(expected, links[:3])
        self.assertIn("FUTURE_WORK.md", readme)
        for link in expected:
            self.assertTrue((ROOT / link).is_file(), f"missing example: {link}")

    def test_example_files_cross_link_in_english_japanese_chinese_order(self) -> None:
        expected = [
            "minimal-orchestration.en.md",
            "minimal-orchestration.ja.md",
            "minimal-orchestration.zh-CN.md",
        ]
        for filename in expected:
            path = ROOT / "examples" / filename
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            links = re.findall(r"\[[^]]+\]\((minimal-orchestration\.[^)]+)\)", text)
            with self.subTest(filename=filename):
                self.assertEqual(expected, links[:3])

    def test_public_files_include_untracked_public_files(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("public", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("public", encoding="utf-8")
            (root / ".planning" / "private.md").parent.mkdir(parents=True)
            (root / ".planning" / "private.md").write_text("private", encoding="utf-8")

            subprocess.run(
                ["git", "-C", str(root), "init", "--quiet"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "add", "--", "README.md"],
                check=True,
                capture_output=True,
            )

            found = {
                path.relative_to(root)
                for path in public_files(root)
            }

        self.assertEqual({Path("README.md"), Path("CHANGELOG.md")}, found)


if __name__ == "__main__":
    unittest.main()
