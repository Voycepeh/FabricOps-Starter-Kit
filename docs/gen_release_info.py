"""Generate build-time release traceability documentation."""

from __future__ import annotations

import os
import subprocess
import tomllib
from pathlib import Path

import mkdocs_gen_files

ROOT = Path(__file__).resolve().parents[1]
UNKNOWN = "unknown"


def _package_version() -> str:
    override = os.environ.get("FABRICOPS_PACKAGE_VERSION")
    if override:
        return override
    with open(ROOT / "pyproject.toml", "rb") as handle:
        data = tomllib.load(handle)
    return str(data.get("project", {}).get("version") or UNKNOWN)


def _doc_version(package_version: str) -> str:
    override = os.environ.get("FABRICOPS_DOC_VERSION")
    if override:
        return override
    parts = package_version.split(".")
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{parts[0]}.{parts[1]}"
    return UNKNOWN


def _git_sha() -> str:
    override = os.environ.get("FABRICOPS_GIT_SHA") or os.environ.get("GITHUB_SHA")
    if override:
        return override
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else UNKNOWN


package_version = _package_version()
doc_version = _doc_version(package_version)
git_sha = _git_sha()

with mkdocs_gen_files.open("release-info.md", "w") as handle:
    handle.write(
        "# Release traceability\n\n"
        "This page is generated at documentation build time from package metadata "
        "and release workflow environment variables.\n\n"
        "| Concept | Value |\n"
        "| --- | --- |\n"
        f"| Full package release version | `{package_version}` |\n"
        f"| Mike documentation series | `{doc_version}` |\n"
        f"| Git commit SHA | `{git_sha}` |\n\n"
        "Package release versions, documentation series, source commits, agreement "
        "versions, and pipeline versions are separate traceability concepts. "
        "Metadata schema changes that persist additional traceability fields should "
        "be handled in a dedicated follow-up migration.\n"
    )
