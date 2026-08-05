from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
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
