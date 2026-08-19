"""One-run branch maintenance script for the Stage 4E cleanup PR.

This file is deleted from the branch immediately after it runs.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

LEGACY_WIDGET_HELPERS = {
    "resolve_table_governance_policy",
    "_is_no_approval_required",
    "_assert_governance_review_context",
    "_lifecycle_fields",
    "_authoring_lifecycle",
    "guardrail_authoring_status",
    "_record_identity",
    "apply_governance_rule_action",
    "load_rule_review_history",
    "_write_enrichment_records",
    "_base_guardrail_rule_record",
    "_filter_table_rows",
    "_load_guardrail_authoring_targets",
    "_latest_rule",
    "_rule_params",
    "_schema_freshness_profile_records_from_selection",
    "_dq_records_from_selection",
    "_is_success",
    "_first_present",
    "_catalogue_physical_identity",
    "load_catalogue_profile_rows",
    "_latest_row",
    "_status_is_failed",
    "_status_is_warning",
    "_read_metadata_rows",
    "_evaluate_governance_readiness",
    "record_table_governance",
    "build_table_governance_policy_record",
    "mark_table_governed",
    "mark_table_ungoverned",
    "_canonical_dq_rule_type",
    "_normalize_dq_severity",
    "_dq_rule_parameter_payload",
    "_build_dq_rule_records",
}

LEGACY_WIDGET_CONSTANTS = {
    "GUARDRAIL_REVIEW_STATUSES",
    "ACTIVATION_STATES",
    "REVIEW_STATES",
    "SOURCE_NOTEBOOK_TYPES",
    "CREATED_BY_ROLES",
}


def _remove_top_level_defs(path: Path, names: set[str]) -> set[str]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    spans: list[tuple[int, int]] = []
    found: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in names:
            found.add(node.name)
            start = node.lineno - 1
            while start > 0 and not lines[start - 1].strip():
                start -= 1
            spans.append((start, node.end_lineno))
    for start, end in sorted(spans, reverse=True):
        del lines[start:end]
    path.write_text("".join(lines), encoding="utf-8")
    return found


def _remove_unused_top_level_assignments(path: Path, names: set[str]) -> None:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    load_counts = {name: 0 for name in names}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in load_counts:
            load_counts[node.id] += 1
    removable = {name for name, count in load_counts.items() if count == 0}
    if not removable:
        return
    lines = text.splitlines(keepends=True)
    spans: list[tuple[int, int]] = []
    for node in tree.body:
        targets: set[str] = set()
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    targets.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets.add(node.target.id)
        if targets and targets <= removable:
            start = node.lineno - 1
            while start > 0 and not lines[start - 1].strip():
                start -= 1
            spans.append((start, node.end_lineno))
    for start, end in sorted(spans, reverse=True):
        del lines[start:end]
    path.write_text("".join(lines), encoding="utf-8")


def _remove_legacy_tests() -> None:
    legacy_file = ROOT / "tests/unit/test_guardrail_authoring_model.py"
    if legacy_file.exists():
        legacy_file.unlink()

    symbols = tuple(sorted(LEGACY_WIDGET_HELPERS, key=len, reverse=True))
    for path in (ROOT / "tests").rglob("test_*.py"):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        lines = text.splitlines(keepends=True)
        spans: list[tuple[int, int]] = []
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith("test_"):
                continue
            source = "".join(lines[node.lineno - 1 : node.end_lineno])
            if any(re.search(rf"\b{re.escape(symbol)}\b", source) for symbol in symbols):
                start = node.lineno - 1
                while start > 0 and not lines[start - 1].strip():
                    start -= 1
                spans.append((start, node.end_lineno))
        if spans:
            for start, end in sorted(spans, reverse=True):
                del lines[start:end]
            path.write_text("".join(lines), encoding="utf-8")


def _patch_guardrail_result_writer() -> None:
    path = ROOT / "src/fabricops_kit/pipeline/guardrails_shared.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '    """Append one runtime outcome for one configured Guardrail rule."""',
        '    """Append one runtime outcome for one exact Guardrail revision."""',
        1,
    )
    needle = '''    guardrail_rule_id = str(result.get("guardrail_rule_id") or "").strip()\n    if not guardrail_rule_id:\n        return\n    audit = build_runtime_audit_fields(config=config, env=env)\n'''
    replacement = '''    guardrail_rule_id = str(result.get("guardrail_rule_id") or "").strip()\n    if not guardrail_rule_id:\n        return\n    guardrail_version = int(result.get("guardrail_version") or 0)\n    if guardrail_version <= 0:\n        raise ValueError("guardrail_version is required to persist a Guardrail result.")\n    audit = build_runtime_audit_fields(config=config, env=env)\n'''
    if needle not in text:
        raise RuntimeError("Guardrail result writer identity block was not found.")
    text = text.replace(needle, replacement, 1)
    needle = '        "guardrail_rule_id": guardrail_rule_id,\n        "run_id": resolved_run_id,\n'
    replacement = '        "guardrail_rule_id": guardrail_rule_id,\n        "guardrail_version": guardrail_version,\n        "run_id": resolved_run_id,\n'
    if needle not in text:
        raise RuntimeError("Guardrail result writer row block was not found.")
    path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")


def _patch_current_contract_tests() -> None:
    config_test = ROOT / "tests/unit/test_config.py"
    text = config_test.read_text(encoding="utf-8")
    text = text.replace('            "profiled_at",\n', "")
    text = text.replace('            "recorded_at",\n', "")
    config_test.write_text(text, encoding="utf-8")

    dq_test = ROOT / "tests/unit/test_dq_rules.py"
    text = dq_test.read_text(encoding="utf-8").replace('            "profiled_at",\n', "")
    dq_test.write_text(text, encoding="utf-8")

    metadata_contract = ROOT / "tests/unit/test_guardrail_metadata_contract.py"
    text = metadata_contract.read_text(encoding="utf-8")
    text = text.replace(
        "from fabricops_kit.pipeline import guardrail_metadata, guardrail_results",
        "from fabricops_kit.pipeline import guardrail_metadata, guardrails_shared",
    )
    text = text.replace("guardrail_results", "guardrails_shared")
    metadata_contract.write_text(text, encoding="utf-8")


def _patch_reference_metadata() -> None:
    path = ROOT / "scripts/reference_docs_metadata.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("configuration_version", "guardrail_version")
    text = text.replace(
        '"primary_key": ["guardrail_rule_id"],',
        '"primary_key": ["guardrail_rule_id", "guardrail_version"],',
        1,
    )
    text = text.replace(
        '"statement": "One Guardrail rule can produce many Guardrail Results across pipeline runs through guardrail_rule_id."',
        '"statement": "One Guardrail revision can produce many Guardrail Results across pipeline runs through guardrail_rule_id and guardrail_version."',
        1,
    )
    writer = '"fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row"'
    dq_writer = '"fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"'
    marker = f'        "guardrail_rule_id": [{writer}, {dq_writer}],\n'
    if marker in text and '        "guardrail_version": [' not in text[text.index('"METADATA_GUARDRAIL_RESULTS"'):]:
        text = text.replace(
            marker,
            marker + f'        "guardrail_version": [{writer}, {dq_writer}],\n',
            1,
        )
    path.write_text(text, encoding="utf-8")


def _remove_stale_guardrail_metadata_alias() -> None:
    path = ROOT / "src/fabricops_kit/pipeline/guardrail_metadata.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("\n\nwrite_guardrail_result_row = runtime.write_guardrail_result_row\n", "\n")
    path.write_text(text, encoding="utf-8")


def _assert_no_source_users() -> None:
    offenders: list[str] = []
    for path in (ROOT / "src").rglob("*.py"):
        if path.as_posix().endswith("widgets/shared.py"):
            continue
        text = path.read_text(encoding="utf-8")
        for symbol in LEGACY_WIDGET_HELPERS:
            if re.search(rf"\b{re.escape(symbol)}\b", text):
                offenders.append(f"{path.relative_to(ROOT)}: {symbol}")
    if offenders:
        raise RuntimeError("Stage 4E helpers still have source users:\n" + "\n".join(sorted(offenders)))


def _run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args), flush=True)
    return subprocess.run(args, cwd=ROOT, check=check, text=True)


def main() -> None:
    shared = ROOT / "src/fabricops_kit/widgets/shared.py"
    _assert_no_source_users()
    found = _remove_top_level_defs(shared, LEGACY_WIDGET_HELPERS)
    missing = LEGACY_WIDGET_HELPERS - found
    if missing:
        raise RuntimeError(f"Expected Stage 4E helpers were not found: {sorted(missing)}")
    _remove_unused_top_level_assignments(shared, LEGACY_WIDGET_CONSTANTS)

    _patch_guardrail_result_writer()
    _remove_stale_guardrail_metadata_alias()
    _remove_legacy_tests()
    _patch_current_contract_tests()
    _patch_reference_metadata()

    _run("uv", "run", "ruff", "check", "--fix", "src/fabricops_kit/widgets/shared.py")
    _run("uv", "run", "ruff", "check", "--fix", "src/fabricops_kit/pipeline/guardrails_shared.py")
    _run("uv", "run", "ruff", "check", "--fix", "tests/unit/test_config.py")
    _run("uv", "run", "ruff", "check", "--fix", "tests/unit/test_dq_rules.py")
    _run("uv", "run", "ruff", "check", "--fix", "tests/unit/test_guardrail_metadata_contract.py")

    _run("uv", "run", "pytest", "tests/unit/test_metadata_schemas.py", "tests/unit/test_guardrail_metadata_contract.py", "tests/unit/test_widget_author_guardrails.py", "tests/unit/test_widget_author_dq_rules.py", "tests/unit/test_observation_guardrails.py", "tests/unit/test_profile_and_register_table.py")

    for _ in range(2):
        _run("bash", "-lc", "PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py")
    for _ in range(2):
        _run("bash", "-lc", "PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py")

    _run("git", "diff", "--check")
    _run("git", "status", "--short")


if __name__ == "__main__":
    main()
