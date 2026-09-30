"""Generate coordinated current or frozen release function references."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import generate_individual_function_reference_pages as pages
from scripts import generate_public_function_call_flows_json as flows
from scripts.release_inventory import load_release_manifests

CURRENT_CONTRACT = ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json"
RELEASES_DIR = ROOT / "docs" / "releases"
TAG_SOURCE_REF_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def _manifest_for_release(version: str) -> dict[str, Any]:
    """Return the manifest for a requested release version."""
    for manifest in load_release_manifests():
        if str(manifest.get("release_version")) == version:
            return manifest
    raise RuntimeError(f"Release {version!r} is not present in docs/releases/manifests.")


def _release_source_ref(manifest: dict[str, Any]) -> str:
    """Return the deterministic source ref pinned by a release manifest."""
    ref = str(manifest.get("source_ref") or manifest.get("git_ref") or manifest.get("tag") or "").strip()
    if not ref:
        raise RuntimeError("Release manifest lacks required source_ref/git_ref/tag for freezing.")
    version = str(manifest.get("release_version") or "").strip()
    if TAG_SOURCE_REF_RE.match(ref):
        expected = f"v{version}"
        if ref != expected:
            raise RuntimeError(f"Release source_ref {ref!r} must match release_version {version!r} as {expected!r}.")
        return ref
    result = subprocess.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"Release source ref {ref!r} cannot be resolved.\n{result.stderr.strip()}")
    return ref


def _source_ref_exists(source_ref: str) -> bool:
    """Return whether a source ref already resolves in the local Git checkout."""
    result = subprocess.run(["git", "rev-parse", "--verify", f"{source_ref}^{{commit}}"], cwd=ROOT, text=True, capture_output=True)
    return result.returncode == 0


def generate_current_bundle() -> None:
    """Generate current call-flow JSON, then current individual pages."""
    flows.write_json(flows.build_payload(), CURRENT_CONTRACT)
    pages.main()


def _copy_release_manifest(worktree: Path, version: str) -> None:
    """Ensure the pinned source sees the same requested release manifest."""
    target = worktree / "docs" / "releases" / "manifests" / f"{version}.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "docs" / "releases" / "manifests" / f"{version}.yml", target)


def _build_release_payload(version: str, source_ref: str) -> dict[str, Any]:
    """Build the release payload from the pinned source revision."""
    if TAG_SOURCE_REF_RE.match(source_ref) and not _source_ref_exists(source_ref):
        payload = flows.build_payload()
        return flows.freeze_release_payload(payload, release_version=version, source_ref=source_ref)
    with tempfile.TemporaryDirectory(prefix="fabricops-release-ref-") as tmp:
        worktree = Path(tmp) / "src"
        subprocess.run(["git", "worktree", "add", "--detach", str(worktree), source_ref], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            _copy_release_manifest(worktree, version)
            payload = flows.build_payload(
                root=worktree,
                pkg_dir=worktree / "src" / "fabricops_kit",
                init_path=worktree / "src" / "fabricops_kit" / "__init__.py",
                manifests_dir=worktree / "docs" / "releases" / "manifests",
            )
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=ROOT, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return flows.freeze_release_payload(payload, release_version=version, source_ref=source_ref)


def generate_release_bundle(version: str, *, overwrite: bool = False) -> None:
    """Freeze release call-flow JSON and matching pages from the pinned release source."""
    manifest = _manifest_for_release(version)
    source_ref = _release_source_ref(manifest)
    release_dir = RELEASES_DIR / version
    contract_path = release_dir / "_data" / "public-function-call-flows.json"
    functions_dir = release_dir / "functions"
    if contract_path.exists() and not overwrite:
        display_path = contract_path.relative_to(ROOT) if contract_path.is_relative_to(ROOT) else contract_path
        raise RuntimeError(f"Release snapshot already exists at {display_path}. Use --overwrite-release to replace it.")
    payload = _build_release_payload(version, source_ref)
    flows.write_json(payload, contract_path)
    pages.generate_release_function_reference_pages(contract_path=contract_path, output_dir=functions_dir, release_version=version)


def main() -> None:
    """Run the coordinated reference generation workflow."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-version", help="Freeze references for the requested release version.")
    parser.add_argument("--overwrite-release", action="store_true", help="Replace an existing frozen release snapshot.")
    args = parser.parse_args()
    if args.release_version:
        generate_release_bundle(args.release_version, overwrite=args.overwrite_release)
    else:
        generate_current_bundle()


if __name__ == "__main__":
    main()
