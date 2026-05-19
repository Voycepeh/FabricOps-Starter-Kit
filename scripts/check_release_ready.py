#!/usr/bin/env python3
"""Check release version alignment between pyproject.toml and package __version__."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = ROOT / "pyproject.toml"
INIT_PATH = ROOT / "src" / "fabricops_kit" / "__init__.py"


def get_pyproject_version(pyproject_text: str) -> str:
    """Extract [project].version from pyproject.toml text."""
    if sys.version_info >= (3, 11):
        import tomllib

        data = tomllib.loads(pyproject_text)
        try:
            return str(data["project"]["version"])
        except KeyError as exc:
            raise ValueError("Could not find [project].version in pyproject.toml") from exc

    in_project_block = False
    for line in pyproject_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_block = stripped == "[project]"
            continue
        if in_project_block:
            match = re.match(r'version\s*=\s*["\']([^"\']+)["\']', stripped)
            if match:
                return match.group(1)

    raise ValueError("Could not find [project].version in pyproject.toml")


def get_init_version(init_text: str) -> str:
    """Extract __version__ from package __init__.py text."""
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_text)
    if not match:
        raise ValueError("Could not find __version__ in src/fabricops_kit/__init__.py")
    return match.group(1)


def main() -> int:
    pyproject_version = get_pyproject_version(PYPROJECT_PATH.read_text(encoding="utf-8"))
    init_version = get_init_version(INIT_PATH.read_text(encoding="utf-8"))

    if pyproject_version == init_version:
        print(f"Release-ready version check passed: {pyproject_version}")
        return 0

    print(
        "Release-ready version check failed: "
        f"pyproject.toml [project].version={pyproject_version} "
        f"!= src/fabricops_kit/__init__.py __version__={init_version}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
