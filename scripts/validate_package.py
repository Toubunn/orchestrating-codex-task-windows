from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


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

HOME_ROOT = "/" + "home/"
USERS_ROOT = "/" + "Users/"

TEXT_PRIVACY_PATTERNS = (
    (
        "machine_path",
        re.compile(
            r"(?i)(?:[a-z]:\\|"
            + re.escape(HOME_ROOT)
            + r"[^/\s]+/|"
            + re.escape(USERS_ROOT)
            + r"[^/\s]+/)"
        ),
    ),
    (
        "live_identifier",
        re.compile(r"(?i)(?:019[0-9a-f-]{20,}|local-[0-9a-f]{20,}|\b(?:task|project|thread)[-_][0-9a-f]{16,}\b)"),
    ),
    (
        "secret",
        re.compile(r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16})"),
    ),
)
FILENAME_PRIVACY_PATTERNS = (
    ("session_log", re.compile(r"(?i)^(?:session|conversation|transcript)[-_](?:log|dump)\.[a-z0-9]+$")),
    ("temporary_worker_file", re.compile(r"(?i)^(?:temporary|temp)[-_](?:prompt|report)\.[a-z0-9]+$")),
)


def is_public_file(path: Path, root: Path) -> bool:
    return path.is_file() and not any(part in PRIVATE_DIRS for part in path.relative_to(root).parts)


def public_files(root: Path) -> list[Path]:
    return sorted(
        [path for path in root.rglob("*") if is_public_file(path, root)],
        key=lambda path: path.as_posix(),
    )


def read_public_text(path: Path) -> str:
    """Decode every public file for privacy scanning without dropping binary bytes."""
    return path.read_bytes().decode("utf-8", errors="replace")


def find_privacy_violations(root: Path) -> list[tuple[str, str]]:
    """Return redacted category/path pairs without returning matched values."""
    violations: set[tuple[str, str]] = set()
    for path in public_files(root):
        relative = path.relative_to(root).as_posix()
        for category, pattern in FILENAME_PRIVACY_PATTERNS:
            if pattern.search(path.name):
                violations.add((category, relative))
        text = read_public_text(path)
        for category, pattern in TEXT_PRIVACY_PATTERNS:
            if pattern.search(text):
                violations.add((category, relative))
    return sorted(violations)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    privacy_violations = find_privacy_violations(root)
    if privacy_violations:
        for category, relative in privacy_violations:
            print(f"FAIL: privacy violation {category} in {relative}")
        return 1

    command = [
        sys.executable,
        "-B",
        "-m",
        "unittest",
        "tests.test_skill_contract",
        "tests.test_package_hygiene",
        "-v",
    ]
    result = subprocess.run(command, cwd=root, check=False)
    print("PASS: package validation" if result.returncode == 0 else "FAIL: package validation")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
