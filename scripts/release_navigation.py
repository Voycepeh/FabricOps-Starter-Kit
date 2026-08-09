"""Synchronize MkDocs release navigation from Live release manifests."""

from __future__ import annotations

import argparse
import difflib
from pathlib import Path

from packaging.version import Version

try:
    from scripts.release_inventory import ROOT, load_release_manifests
except ModuleNotFoundError:  # Direct execution via ``python scripts/release_navigation.py``.
    from release_inventory import ROOT, load_release_manifests


MKDOCS_PATH = ROOT / "mkdocs.yml"
MANIFESTS_DIR = ROOT / "docs" / "releases" / "manifests"
RELEASES_HEADING = "  - Releases:"


def live_release_versions(manifests_dir: Path = MANIFESTS_DIR) -> list[str]:
    """Return Live release versions newest first."""
    manifests = load_release_manifests(manifests_dir)
    versions = [
        str(manifest["release_version"])
        for manifest in manifests
        if str(manifest.get("release_status") or "").lower() == "live"
    ]
    return sorted(versions, key=Version, reverse=True)


def render_release_navigation(manifests_dir: Path = MANIFESTS_DIR) -> str:
    """Render the canonical MkDocs Releases navigation block."""
    lines = [RELEASES_HEADING, "      - Overview: releases/index.md"]
    lines.extend(
        f"      - {version}: releases/{version}/index.md"
        for version in live_release_versions(manifests_dir)
    )
    return "\n".join(lines) + "\n"


def expected_mkdocs_text(current: str, manifests_dir: Path = MANIFESTS_DIR) -> str:
    """Return MkDocs content with the Releases block synchronized."""
    lines = current.splitlines(keepends=True)
    start = next((index for index, line in enumerate(lines) if line.rstrip("\n") == RELEASES_HEADING), None)
    if start is None:
        raise ValueError("mkdocs.yml does not contain the expected '  - Releases:' navigation section.")

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("  - ") and not line.startswith("      - "):
            end = index
            break

    replacement = render_release_navigation(manifests_dir)
    return "".join(lines[:start]) + replacement + "".join(lines[end:])


def sync_release_navigation(
    check: bool = False,
    mkdocs_path: Path = MKDOCS_PATH,
    manifests_dir: Path = MANIFESTS_DIR,
) -> Path:
    """Write or validate release sidebar navigation in ``mkdocs.yml``."""
    current = mkdocs_path.read_text(encoding="utf-8")
    expected = expected_mkdocs_text(current, manifests_dir)

    if check:
        if current != expected:
            diff = "".join(
                difflib.unified_diff(
                    current.splitlines(True),
                    expected.splitlines(True),
                    fromfile=str(mkdocs_path),
                    tofile="expected",
                )
            )
            raise SystemExit(
                "MkDocs release navigation is stale. Regenerate release contract pages or run "
                "python scripts/release_navigation.py.\n" + diff
            )
        return mkdocs_path

    if current != expected:
        mkdocs_path.write_text(expected, encoding="utf-8")
    return mkdocs_path


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for release navigation synchronization."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        path = sync_release_navigation(check=args.check)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Release navigation {'validated' if args.check else 'synchronized'}: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
