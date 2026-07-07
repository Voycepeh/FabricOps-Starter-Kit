"""Validate freshness only for generated artifacts owned by changed paths."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ArtifactCheck:
    """Generated artifact freshness check selected by changed path ownership."""

    name: str
    command: tuple[str, ...]
    diff_paths: tuple[str, ...]


CALL_FLOW_CHECK = ArtifactCheck(
    name="public call-flow architecture contract",
    command=(sys.executable, "scripts/generate_public_function_call_flows_json.py"),
    diff_paths=("docs/reference/_data/public-function-call-flows.json",),
)
REFERENCE_CHECK = ArtifactCheck(
    name="individual function reference pages",
    command=(sys.executable, "scripts/generate_individual_function_reference_pages.py"),
    diff_paths=(
        "docs/api/reference",
        "docs/reference/index.md",
    ),
)
DASHBOARD_CHECK = ArtifactCheck(
    name="public call-flow dashboard HTML",
    command=(sys.executable, "scripts/generate_public_function_call_flows_dashboard.py"),
    diff_paths=("docs/assets/public-function-call-flows-dashboard.html",),
)


def _is_under(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(f"{prefix}/")


def owns_call_flow_contract(path: str) -> bool:
    """Return whether a path owns the committed call-flow architecture contract."""
    return (
        _is_under(path, "src/fabricops_kit") and path.endswith(".py")
    ) or path in {
        "scripts/generate_public_function_call_flows_json.py",
        "scripts/reference_docs_metadata.py",
        "docs/reference/_data/public-function-call-flows.json",
        "src/README.md",
    }


def owns_individual_reference_pages(path: str) -> bool:
    """Return whether a path owns individual generated reference page freshness."""
    return _is_under(path, "docs/api/reference") or path in {
        "scripts/generate_individual_function_reference_pages.py",
        "scripts/reference_docs_metadata.py",
        "docs/reference/index.md",
    }


def owns_dashboard_html(path: str) -> bool:
    """Return whether a path owns generated dashboard HTML freshness."""
    return path in {
        "scripts/generate_public_function_call_flows_dashboard.py",
        "docs/assets/public-function-call-flows-dashboard.html",
    } or _is_under(path, "dashboard") or _is_under(path, "frontend")


def select_checks(changed_paths: Iterable[str]) -> tuple[ArtifactCheck, ...]:
    """Select generated artifact checks owned by the changed paths."""
    paths = tuple(dict.fromkeys(path.strip().lstrip("./") for path in changed_paths if path.strip()))
    checks: list[ArtifactCheck] = []
    if any(owns_call_flow_contract(path) for path in paths):
        checks.append(CALL_FLOW_CHECK)
    if any(owns_individual_reference_pages(path) for path in paths):
        checks.append(REFERENCE_CHECK)
    if any(owns_dashboard_html(path) for path in paths):
        checks.append(DASHBOARD_CHECK)
    return tuple(checks)


def changed_paths_from_git(base_ref: str | None = None) -> tuple[str, ...]:
    """Return changed paths including deleted and renamed files."""
    if base_ref:
        subprocess.run(["git", "fetch", "--no-tags", "origin", base_ref], cwd=ROOT, check=False)
        diff_range = f"origin/{base_ref}...HEAD"
        command = ["git", "diff", "--name-only", "--diff-filter=ACMRD", diff_range]
    else:
        command = ["git", "diff-tree", "--no-commit-id", "--name-only", "--diff-filter=ACMRD", "-r", "HEAD"]
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    return tuple(line for line in result.stdout.splitlines() if line)


def restore_generated_metadata_and_page_timestamps(*, update_reference_pages: bool = False) -> None:
    """Keep informational generated timestamps from causing freshness failures."""
    metadata_path = Path("docs/reference/_data/generated-artifacts.json")
    result = subprocess.run(
        ["git", "show", f"HEAD:{metadata_path.as_posix()}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return
    committed = json.loads(result.stdout)
    artifacts = committed.get("artifacts", {}) if isinstance(committed, dict) else {}
    reference_timestamp = artifacts.get("individual_function_reference_pages", {}).get(
        "generated_at_sgt", "Generated timestamp unavailable"
    )
    call_flow_timestamp = artifacts.get("public_function_call_flows_json", {}).get(
        "generated_at_sgt", "Generated timestamp unavailable"
    )
    if update_reference_pages:
        reference_pattern = re.compile(r"^(\s*Reference pages generated: ).*$", re.MULTILINE)
        call_flow_pattern = re.compile(r"^(\s*Call-flow data generated: ).*$", re.MULTILINE)
        for page in (ROOT / "docs/api/reference").glob("*.md"):
            text = page.read_text(encoding="utf-8")
            text = reference_pattern.sub(rf"\g<1>{reference_timestamp}", text)
            text = call_flow_pattern.sub(rf"\g<1>{call_flow_timestamp}", text)
            page.write_text(text, encoding="utf-8")
    (ROOT / metadata_path).write_text(result.stdout, encoding="utf-8")


def run_check(check: ArtifactCheck) -> int:
    """Run one generator and diff only its owned generated artifacts."""
    print(f"Validating {check.name}...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    env["FABRICOPS_PRESERVE_GENERATED_ARTIFACT_TIMESTAMPS"] = "1"
    subprocess.run(check.command, cwd=ROOT, env=env, check=True)
    restore_generated_metadata_and_page_timestamps(update_reference_pages=check is REFERENCE_CHECK)
    diff = subprocess.run(["git", "diff", "--exit-code", "--", *check.diff_paths], cwd=ROOT, check=False)
    return diff.returncode


def validate(changed_paths: Sequence[str]) -> int:
    """Run selected ownership checks and return a process status code."""
    checks = select_checks(changed_paths)
    if not checks:
        print("No generated artifact ownership checks required for changed paths.")
        return 0
    print("Changed paths select generated artifact checks:")
    for check in checks:
        print(f"- {check.name}")
    status = 0
    for check in checks:
        status = run_check(check) or status
    return status


def main(argv: Sequence[str] | None = None) -> int:
    """Run generated artifact ownership validation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Changed paths to classify. Defaults to git diff scope.")
    parser.add_argument("--base-ref", default=os.environ.get("GITHUB_BASE_REF"), help="Base branch for PR diff detection.")
    args = parser.parse_args(argv)
    paths = tuple(args.paths) if args.paths else changed_paths_from_git(args.base_ref)
    return validate(paths)


if __name__ == "__main__":
    raise SystemExit(main())
