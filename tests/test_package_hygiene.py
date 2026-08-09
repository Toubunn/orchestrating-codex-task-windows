from __future__ import annotations

import re
import subprocess
from tempfile import TemporaryDirectory
import unittest
from pathlib import Path

import scripts.validate_package as package_validator


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
VALIDATOR = ROOT / "scripts" / "validate_package.py"
CONSTELLARY_SKILL = ROOT / "skills" / "constellary"
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
PROJECT_ABSENT_TERM = "project" + "less"

ENGLISH_I18N_CONTRADICTIONS = (
    re.compile(
        r"\b(?:codex\s+)?desktop\b.{0,40}\b(?:may|can|could|is allowed to)\b"
        r".{0,40}\b(?:fall\s*back|fallback)\b.{0,20}\bcli\b",
        re.I,
    ),
    re.compile(
        r"\bdownstream\s+tasks?\b.{0,40}\b(?:may|can|could|are allowed to)\b"
        + r".{0,40}\b"
        + re.escape(PROJECT_ABSENT_TERM)
        + r"\b",
        re.I,
    ),
    re.compile(
        r"\b(?:codex\s+)?desktop\b.{0,30}\b(?:is|becomes?|remains?)\s+"
        r"(?:optional|elective)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:codex\s+)?desktop\b.{0,30}"
        r"\b(?:can|may|could|is able to|is allowed to)\b"
        r"(?!\s+(?:not|never)\b).{0,50}\b(?:route|rout(?:e|ing)|send|dispatch|pass)\w*\b"
        r".{0,50}\b(?:work|tasks?|jobs?)\b.{0,30}\b(?:through|via|using)\b.{0,20}\bcli\b",
        re.I,
    ),
    re.compile(
        r"\b(?:downstream\s+)?tasks?\b.{0,40}"
        r"\b(?:may|can|could|are allowed to)\b(?!\s+(?:not|never)\b)"
        r".{0,40}\b(?:run|execute|operate|dispatch|create)\b"
        r".{0,40}\bwithout\b.{0,25}\b(?:a\s+)?project\s+context\b",
        re.I,
    ),
    re.compile(
        r"\b(?:codex\s+)?desktop\b.{0,30}"
        r"\b(?:can|may|could|is allowed to)\b(?!\s+(?:not|never)\b)"
        r".{0,30}\b(?:be\s+)?(?:omitted|skipped|left\s+out|optional|not\s+required)\b",
        re.I,
    ),
)

JAPANESE_I18N_CONTRADICTIONS = (
    re.compile(
        r"(?:codex\s*)?desktop\s*(?:が|は).{0,20}cli.{0,20}"
        r"(?:経由|を通じて|を介して).{0,30}(?:作業|仕事|タスク).{0,15}(?:を)?"
        r"(?:送れる|送れます|送信できる|送信可能|ルーティングできる|ルーティング可能)",
        re.I,
    ),
    re.compile(
        r"タスク.{0,20}(?:は|が).{0,20}(?:プロジェクト文脈|プロジェクトコンテキスト)"
        r".{0,10}(?:なしで|無しで|なしに|無しに).{0,20}"
        r"(?:実行|動作|作成|運用).{0,10}(?:できる|できます|可能|可能です)",
        re.I,
    ),
    re.compile(
        r"(?:codex\s*)?desktop\s*(?:を|は).{0,10}"
        r"(?:省略|スキップ|除外).{0,10}(?:できる|できます|可能|可能です|よい|よいです)",
        re.I,
    ),
    re.compile(
        r"(?:codex\s+)?desktop.{0,50}cli.{0,50}(?:フォールバック|fallback)"
        r".{0,40}(?:できます|可能|許可|よい|可)",
        re.I,
    ),
    re.compile(
        r"下流タスク.{0,40}(?:プロジェクトなし|プロジェクト無し)"
        r".{0,40}(?:できます|可能|許可|よい|可)",
        re.I,
    ),
    re.compile(
        r"(?:codex\s+)?desktop.{0,20}(?:任意|オプション)"
        r".{0,20}(?:です|である|可能|可)?",
        re.I,
    ),
)

CHINESE_I18N_CONTRADICTIONS = (
    re.compile(
        r"desktop.{0,30}(?:可以|能够|可|允许).{0,20}cli.{0,20}"
        r"(?:回退|回落|fallback)|desktop.{0,20}cli.{0,20}"
        r"(?:回退|回落|fallback).{0,20}(?:可以|能够|可|允许)|desktop.{0,30}"
        r"(?:可以|能够|可|允许).{0,20}(?:回退|回落|fallback).{0,20}cli",
        re.I,
    ),
    re.compile(
        r"下级任务.{0,40}(?:可以|能够|可|允许).{0,30}"
        r"(?:无项目|没有项目|项目无关).{0,30}(?:创建|运行|执行)",
        re.I,
    ),
    re.compile(
        r"(?:codex\s+)?desktop.{0,20}(?:是|为).{0,10}"
        r"(?:可选|非必需|可不用)",
        re.I,
    ),
    re.compile(
        r"desktop.{0,20}(?<!不)(?:可以|能够|可|允许).{0,20}"
        r"(?:通过|经由|使用).{0,20}cli.{0,30}(?:路由|转发|派发|发送)"
        r".{0,20}(?:工作|任务)",
        re.I,
    ),
    re.compile(
        r"(?:下级|独立)?任务.{0,20}(?<!不)(?:可以|能够|可|允许).{0,20}"
        r"(?:不带|无需|无须|没有|无).{0,20}(?:项目上下文|项目文脉|项目语境)"
        r".{0,20}(?:运行|执行|创建)",
        re.I,
    ),
    re.compile(
        r"desktop.{0,20}(?<!不)(?:可以|能够|可|允许).{0,20}"
        r"(?<!不)(?:省略|跳过|不使用|不用)",
        re.I,
    ),
)

I18N_CONTRADICTION_PATTERNS = {
    "README.md": ENGLISH_I18N_CONTRADICTIONS,
    "examples/minimal-orchestration.en.md": ENGLISH_I18N_CONTRADICTIONS,
    "README.ja.md": JAPANESE_I18N_CONTRADICTIONS,
    "examples/minimal-orchestration.ja.md": JAPANESE_I18N_CONTRADICTIONS,
    "README.zh-CN.md": CHINESE_I18N_CONTRADICTIONS,
    "examples/minimal-orchestration.zh-CN.md": CHINESE_I18N_CONTRADICTIONS,
}


def has_i18n_contradiction(filename: str, text: str) -> bool:
    """Detect explicit language-specific permissions that reverse v2 semantics."""
    return any(pattern.search(text) for pattern in I18N_CONTRADICTION_PATTERNS[filename])


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
        path.read_bytes().decode("utf-8", errors="replace")
        for path in public_files()
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


LEGACY_SLUG = "-".join(("orchestrating", "codex", "task", "windows"))
LEGACY_DISPLAY_NAME = " ".join(("Orchestrating", "Codex", "Task", "Windows"))
MIGRATION_SECTION_PATTERN = re.compile(
    r"(?ms)^##\s+v2\.0\.0-alpha\s+—\s+Constellary migration history\s*$"
    r"(?P<body>.*?)(?=^##\s|\Z)"
)
MIGRATION_RENAME_BULLET_PATTERN = re.compile(
    r"(?ms)^- Renamed the public Skill from `"
    + re.escape(LEGACY_SLUG)
    + r"` \(display name\s+“"
    + re.escape(LEGACY_DISPLAY_NAME)
    + r"”\) to `Constellary`, with slug `constellary`\s+"
    r"and invocation `\$constellary`\.\s*$"
)


def _remove_allowed_migration_occurrence(text: str) -> str:
    """Remove only the exact existing rename bullet from the exact v2 history section."""
    section = MIGRATION_SECTION_PATTERN.search(text)
    if section is None:
        return text
    body = section.group("body")
    allowed = MIGRATION_RENAME_BULLET_PATTERN.search(body)
    if allowed is None:
        return text
    return text[: section.start("body")] + body[: allowed.start()] + body[allowed.end() :] + text[section.end("body") :]


def legacy_name_violations(root: Path = ROOT) -> list[str]:
    """Return public relative paths with legacy slug/display-name residue."""
    violations: set[str] = set()
    for path in public_files(root):
        relative = path.relative_to(root).as_posix()
        relative_folded = relative.casefold()
        text = package_validator.read_public_text(path)
        if relative == "CHANGELOG.md":
            text = _remove_allowed_migration_occurrence(text)
        folded = text.casefold()
        if any(
            marker.casefold() in relative_folded or marker.casefold() in folded
            for marker in (LEGACY_SLUG, LEGACY_DISPLAY_NAME)
        ):
            violations.add(relative)
    return sorted(violations)


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
            "$constellary",
            "python -B scripts/validate_package.py",
            "MIT License",
        ]
        for filename in ("README.md", "README.ja.md", "README.zh-CN.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertEqual([], [marker for marker in markers if marker not in text])
                self.assertFalse(has_i18n_contradiction(filename, text))

    def test_readme_language_versions_explain_the_v2_alpha_update(self) -> None:
        headings = {
            "README.md": "What's new in v2.0.0-alpha",
            "README.ja.md": "v2.0.0-alpha の更新内容",
            "README.zh-CN.md": "v2.0.0-alpha 本次更新内容",
        }
        required = (
            "$constellary",
            "skills/constellary/",
            "coordination_surface: codex_desktop",
            "desktop_required",
            "execution_environment: auto_safe",
            "34",
            "FUTURE_WORK.md",
            "79",
        )
        for filename, heading in headings.items():
            text = (ROOT / filename).read_text(encoding="utf-8")
            marker = f"## {heading}"
            with self.subTest(filename=filename):
                self.assertIn(marker, text)
                section = text.split(marker, 1)[1].split("\n## ", 1)[0]
                self.assertEqual([], [item for item in required if item not in section])

    def test_readme_language_versions_reject_contradictory_runtime_mutations(self) -> None:
        mutations = {
            "README.md": (
                "Codex Desktop may fall back to the CLI for downstream tasks.",
                "Downstream tasks may be " + PROJECT_ABSENT_TERM + ".",
                "Codex Desktop is optional.",
            ),
            "README.ja.md": (
                "Codex Desktop は CLI にフォールバックして下流タスクを作成できます。",
                "下流タスクはプロジェクトなしで作成できます。",
                "Codex Desktop は任意です。",
            ),
            "README.zh-CN.md": (
                "Codex Desktop 可以回退到 CLI 来创建下级任务。",
                "下级任务可以在无项目状态下创建。",
                "Codex Desktop 是可选的。",
            ),
        }
        for filename, phrases in mutations.items():
            original = (ROOT / filename).read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(filename=filename, phrase=phrase):
                    mutated = original + "\n" + phrase + "\n"
                    self.assertTrue(has_i18n_contradiction(filename, mutated))

    def test_readmes_and_matching_examples_are_contradiction_free(self) -> None:
        filenames = (
            "README.md",
            "README.ja.md",
            "README.zh-CN.md",
            "examples/minimal-orchestration.en.md",
            "examples/minimal-orchestration.ja.md",
            "examples/minimal-orchestration.zh-CN.md",
        )
        for filename in filenames:
            with self.subTest(filename=filename):
                self.assertIn(filename, I18N_CONTRADICTION_PATTERNS)
                text = (ROOT / filename).read_text(encoding="utf-8")
                self.assertFalse(has_i18n_contradiction(filename, text))

    def test_i18n_contradiction_probes_cover_common_paraphrases_in_all_languages(self) -> None:
        mutations = {
            "README.md": (
                "Desktop can route work through CLI.",
                "Tasks may run without project context.",
                "Desktop can be omitted.",
            ),
            "README.ja.md": (
                "Desktop が CLI 経由で作業を送れる。",
                "タスクはプロジェクト文脈なしで実行できる。",
                "Desktop を省略できる。",
            ),
            "README.zh-CN.md": (
                "Desktop 可以通过 CLI 路由工作。",
                "任务可以不带项目上下文运行。",
                "Desktop 可以省略。",
            ),
            "examples/minimal-orchestration.en.md": (
                "Desktop can route work through CLI.",
                "Tasks may run without project context.",
                "Desktop can be omitted.",
            ),
            "examples/minimal-orchestration.ja.md": (
                "Desktop が CLI 経由で作業を送れる。",
                "タスクはプロジェクト文脈なしで実行できる。",
                "Desktop を省略できる。",
            ),
            "examples/minimal-orchestration.zh-CN.md": (
                "Desktop 可以通过 CLI 路由工作。",
                "任务可以不带项目上下文运行。",
                "Desktop 可以省略。",
            ),
        }
        for filename, phrases in mutations.items():
            original = (ROOT / filename).read_text(encoding="utf-8")
            patterns = I18N_CONTRADICTION_PATTERNS.get(filename, ())
            for phrase in phrases:
                with self.subTest(filename=filename, phrase=phrase):
                    mutated = original + "\n" + phrase + "\n"
                    self.assertTrue(
                        any(pattern.search(mutated) for pattern in patterns),
                        f"paraphrase was not detected for {filename}",
                    )

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
            matches = re.findall(pattern, text)
            self.assertEqual(0, len(matches), f"machine-specific path pattern matched: {pattern}")

    def test_no_live_thread_or_project_ids(self) -> None:
        text = public_text()
        patterns = [
            r"(?i)019[0-9a-f-]{20,}",
            r"(?i)local-[0-9a-f]{20,}",
            r"(?i)\b(?:task|project|thread)[-_][0-9a-f]{16,}\b",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            self.assertEqual(0, len(matches), f"live identifier pattern matched: {pattern}")

    def test_no_secret_shaped_values(self) -> None:
        text = public_text()
        patterns = [
            r"gh[pousr]_[A-Za-z0-9_]{20,}",
            r"sk-[A-Za-z0-9_-]{20,}",
            r"AKIA[0-9A-Z]{16}",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            self.assertEqual(0, len(matches), f"secret-shaped pattern matched: {pattern}")

    def test_no_unresolved_authoring_markers(self) -> None:
        text = public_text()
        marker_words = ["".join(parts) for parts in (("T", "ODO"), ("T", "BD"), ("FIX", "ME"))]
        pattern = r"(?i)\b(?:" + "|".join(marker_words) + r")\b"
        matches = re.findall(pattern, text)
        self.assertEqual(0, len(matches), "unresolved authoring marker detected")

    def test_structured_privacy_scan_passes_the_public_package(self) -> None:
        violations = package_validator.find_privacy_violations(ROOT)
        self.assertEqual([], violations)

    def test_skill_references_resolve(self) -> None:
        skill = ROOT / "skills" / "constellary" / "SKILL.md"
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

    def test_public_package_excludes_private_iteration_markers(self) -> None:
        private_iteration_markers = (
            ".".join(("8", "8")),
            "_".join(("local", "serialized")),
        )
        leaked = []
        for path in public_files():
            relative = path.relative_to(ROOT).as_posix().casefold()
            text = path.read_text(encoding="utf-8", errors="replace")
            if any(
                marker in relative or marker in text.casefold()
                for marker in private_iteration_markers
            ):
                leaked.append(str(path.relative_to(ROOT)))
        self.assertEqual([], leaked)

    def test_public_marker_checks_reject_clean_path_markers(self) -> None:
        legacy_slug = "-".join(("orchestrating", "codex", "task", "windows"))
        private_marker = "_".join(("local", "serialized"))
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            legacy_path = root / "skills" / legacy_slug / "SKILL.md"
            private_path = root / "reports" / private_marker / "notes.md"
            legacy_path.parent.mkdir(parents=True)
            private_path.parent.mkdir(parents=True)
            legacy_path.write_text("clean public content", encoding="utf-8")
            private_path.write_text("clean public content", encoding="utf-8")

            legacy_leaks = []
            private_leaks = []
            for path in public_files(root):
                relative = path.relative_to(root).as_posix().casefold()
                text = path.read_text(encoding="utf-8", errors="replace").casefold()
                if legacy_slug.casefold() in relative or legacy_slug.casefold() in text:
                    legacy_leaks.append(path.relative_to(root).as_posix())
                if private_marker.casefold() in relative or private_marker.casefold() in text:
                    private_leaks.append(path.relative_to(root).as_posix())

        self.assertIn(f"skills/{legacy_slug}/SKILL.md", legacy_leaks)
        self.assertIn(f"reports/{private_marker}/notes.md", private_leaks)

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


class ConstellaryIdentityPackageTests(unittest.TestCase):
    def test_public_identity_and_development_version_are_consistent(self) -> None:
        files = [
            CONSTELLARY_SKILL / "SKILL.md",
            CONSTELLARY_SKILL / "agents" / "openai.yaml",
            ROOT / "README.md",
            ROOT / "README.ja.md",
            ROOT / "README.zh-CN.md",
        ]
        contents = [path.read_text(encoding="utf-8") if path.is_file() else "" for path in files]
        self.assertEqual([], [str(path.relative_to(ROOT)) for path, text in zip(files, contents) if not text])
        for text in contents:
            with self.subTest(marker="Constellary"):
                self.assertIn("Constellary", text)
            with self.subTest(marker="$constellary"):
                self.assertIn("$constellary", text)
            with self.subTest(marker="v2.0.0-alpha"):
                self.assertIn("v2.0.0-alpha", text)

    def test_old_name_is_confined_to_explicit_migration_history(self) -> None:
        self.assertEqual([], legacy_name_violations())

    def test_legacy_migration_exception_is_narrow_and_checks_slug_display_and_paths(self) -> None:
        legacy_slug = "-".join(("orchestrating", "codex", "task", "windows"))
        legacy_display = " ".join(("Orchestrating", "Codex", "Task", "Windows"))
        migration_bullet = (
            f"- Renamed the public Skill from `{legacy_slug}` (display name\n"
            f"  “{legacy_display}”) to `Constellary`, with slug `constellary`\n"
            "  and invocation `$constellary`.\n"
        )
        migration_only = (
            "# Changelog\n\n"
            "## v2.0.0-alpha — Constellary migration history\n\n"
            + migration_bullet
        )

        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            changelog = root / "CHANGELOG.md"
            changelog.write_text(migration_only, encoding="utf-8")
            self.assertEqual([], legacy_name_violations(root))

            arbitrary_slug_note = migration_only + (
                "\n## Notes\n\n"
                f"- An unrelated note mentions `{legacy_slug}`.\n"
            )
            changelog.write_text(arbitrary_slug_note, encoding="utf-8")
            self.assertIn("CHANGELOG.md", legacy_name_violations(root))

            arbitrary_display_note = migration_only + (
                "\n## Notes\n\n"
                f"- An unrelated note mentions “{legacy_display}”.\n"
            )
            changelog.write_text(arbitrary_display_note, encoding="utf-8")
            self.assertIn("CHANGELOG.md", legacy_name_violations(root))

            legacy_path = root / "docs" / legacy_slug / "note.md"
            legacy_path.parent.mkdir(parents=True)
            legacy_path.write_text("clean public content", encoding="utf-8")
            self.assertIn("docs/" + legacy_slug + "/note.md", legacy_name_violations(root))

            display_path = root / "docs" / legacy_display / "note.md"
            display_path.parent.mkdir(parents=True)
            display_path.write_text("clean public content", encoding="utf-8")
            self.assertIn("docs/" + legacy_display + "/note.md", legacy_name_violations(root))


class PrivacyScannerTests(unittest.TestCase):
    def test_synthetic_machine_path_is_reported_without_echoing_the_value(self) -> None:
        self.assertTrue(hasattr(package_validator, "find_privacy_violations"))
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            drive_path = "C" + ":" + "\\" + "Users" + "\\" + "Example" + "\\" + "session.log"
            (root / "README.md").write_text(f"redacted fixture: {drive_path}", encoding="utf-8")
            violations = package_validator.find_privacy_violations(root)

        self.assertIn(("machine_path", "README.md"), violations)
        self.assertNotIn(drive_path, " ".join(f"{category}:{path}" for category, path in violations))

    def test_synthetic_temporary_worker_artifacts_are_reported_by_category(self) -> None:
        self.assertTrue(hasattr(package_validator, "find_privacy_violations"))
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "temporary-prompt.txt").write_text("fixture", encoding="utf-8")
            (root / "session-log.txt").write_text("fixture", encoding="utf-8")
            violations = package_validator.find_privacy_violations(root)

        self.assertIn(("temporary_worker_file", "temporary-prompt.txt"), violations)
        self.assertIn(("session_log", "session-log.txt"), violations)

    def test_all_public_regular_files_are_scanned_for_text_privacy(self) -> None:
        machine_path = "C" + ":" + "\\" + "Users" + "\\" + "Example" + "\\" + "session.log"
        secret = "sk-" + ("A" * 24)
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "LICENSE").write_text(f"approved text shape: {machine_path}", encoding="utf-8")
            (root / "metadata.json").write_text(f"private token shape: {secret}", encoding="utf-8")
            violations = package_validator.find_privacy_violations(root)

        rendered = " ".join(f"{category}:{path}" for category, path in violations)
        self.assertIn(("machine_path", "LICENSE"), violations)
        self.assertIn(("secret", "metadata.json"), violations)
        self.assertNotIn(machine_path, rendered)
        self.assertNotIn(secret, rendered)


if __name__ == "__main__":
    unittest.main()
