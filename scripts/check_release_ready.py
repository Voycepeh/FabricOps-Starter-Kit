#!/usr/bin/env python3
"""Check release version alignment for FabricOps Starter Kit."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = ROOT / "pyproject.toml"
MANIFESTS_DIR = ROOT / "docs" / "releases" / "manifests"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
TAG_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


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
            match = re.match(r"version\s*=\s*[\"\']([^\"\']+)[\"\']", stripped)
            if match:
                return match.group(1)

    raise ValueError("Could not find [project].version in pyproject.toml")


def get_runtime_package_version() -> str:
    """Import fabricops_kit from this checkout and return its runtime version."""
    command = [
        sys.executable,
        "-c",
        "import fabricops_kit; print(fabricops_kit.__version__)",
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def version_from_tag(tag_name: str) -> str:
    """Return the semantic version encoded by a vMAJOR.MINOR.PATCH Git tag."""
    if not TAG_RE.match(tag_name):
        raise ValueError(f"Tag {tag_name!r} does not match vMAJOR.MINOR.PATCH")
    return tag_name[1:]



def get_release_manifest_fields(version: str) -> dict[str, str]:
    """Return top-level scalar fields from the release manifest for a version."""
    path = MANIFESTS_DIR / f"{version}.yml"
    if not path.exists():
        raise ValueError(f"Release manifest not found: {path.relative_to(ROOT)}")
    fields: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith(" ") or ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        fields[key] = value.strip()
    return fields


def validate_manifest_release_alignment(version: str, tag_name: str) -> None:
    """Validate manifest release_version and source_ref match the pushed tag."""
    fields = get_release_manifest_fields(version)
    manifest_version = fields.get("release_version")
    source_ref = fields.get("source_ref")
    if manifest_version != version:
        raise ValueError(f"Manifest release_version={manifest_version!r} != package/tag version={version!r}")
    if source_ref != tag_name:
        raise ValueError(f"Manifest source_ref={source_ref!r} != release tag={tag_name!r}")

def main(tag_name: str | None = None) -> int:
    """Run the command-line workflow."""
    pyproject_version = get_pyproject_version(PYPROJECT_PATH.read_text(encoding="utf-8"))
    if not SEMVER_RE.match(pyproject_version):
        print(f"Release-ready version check failed: {pyproject_version!r} is not MAJOR.MINOR.PATCH")
        return 1

    runtime_version = get_runtime_package_version()
    if pyproject_version != runtime_version:
        print(
            "Release-ready version check failed: "
            f"pyproject.toml [project].version={pyproject_version} "
            f"!= fabricops_kit.__version__={runtime_version}"
        )
        return 1

    if tag_name:
        tag_version = version_from_tag(tag_name)
        if tag_version != pyproject_version:
            print(
                "Release-ready tag check failed: "
                f"tag version={tag_version} != pyproject.toml [project].version={pyproject_version}"
            )
            return 1
        try:
            validate_manifest_release_alignment(pyproject_version, tag_name)
        except ValueError as exc:
            print(f"Release-ready manifest check failed: {exc}")
            return 1

    print(f"Release-ready version check passed: {pyproject_version}")
    return 0


if __name__ == "__main__":
    tag_arg = sys.argv[1] if len(sys.argv) > 1 else None
    raise SystemExit(main(tag_arg))
