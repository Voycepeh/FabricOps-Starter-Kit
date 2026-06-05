"""Generate build-time release traceability documentation for MkDocs."""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UNKNOWN = "unknown"
OUTPUT_NAME = "release-info.md"


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
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        return package_version
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


def render_release_info() -> str:
    """Return the release traceability page body for the current build."""

    package_version = _package_version()
    doc_version = _doc_version(package_version)
    git_sha = _git_sha()
    return (
        "# Release traceability\n\n"
        "This page is generated at documentation build time from package metadata "
        "and release workflow environment variables.\n\n"
        "| Concept | Value |\n"
        "| --- | --- |\n"
        f"| Full package release version | `{package_version}` |\n"
        f"| Mike documentation version | `{doc_version}` |\n"
        f"| Git commit SHA | `{git_sha}` |\n\n"
        "Package release versions, documentation versions, source commits, agreement "
        "versions, and pipeline versions are separate traceability concepts. "
        "Metadata schema changes that persist additional traceability fields should "
        "be handled in a dedicated follow-up migration.\n"
    )


def write_release_info(docs_dir: str | Path | None = None) -> Path:
    """Write the generated release traceability page into the MkDocs docs directory."""

    output_dir = Path(docs_dir) if docs_dir is not None else ROOT / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / OUTPUT_NAME
    output_path.write_text(render_release_info(), encoding="utf-8")
    return output_path


def on_config(config: Any) -> Any:
    """MkDocs hook that materializes the nav target before strict validation."""

    write_release_info(config["docs_dir"])
    return config


if __name__ == "__main__":
    path = write_release_info(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"Generated {path}")
