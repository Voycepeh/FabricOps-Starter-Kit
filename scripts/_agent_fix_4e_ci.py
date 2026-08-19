"""One-run CI cleanup for the Stage 4E branch.

Deleted from the branch after execution.
"""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str, *, count: int = -1) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected text not found in {path}: {old!r}")
    target.write_text(text.replace(old, new, count), encoding="utf-8")


def remove_top_level_functions(path: str, names: set[str]) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    found = set()
    spans = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            found.add(node.name)
            start = node.lineno - 1
            while start > 0 and not lines[start - 1].strip():
                start -= 1
            spans.append((start, node.end_lineno))
    missing = names - found
    if missing:
        raise RuntimeError(f"Expected functions not found in {path}: {sorted(missing)}")
    for start, end in sorted(spans, reverse=True):
        del lines[start:end]
    target.write_text("".join(lines), encoding="utf-8")


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    # The shared fake-widget helper is now authoritative for standalone widget tests.
    replace(
        "tests/unit/test_widget_author_guardrails.py",
        "        def observe(self, callback, names=None):\n            self._observers.append(callback)\n",
        "        def observe(self, callback, names=None):\n            self._observer = callback\n            self._observers.append(callback)\n",
    )

    # Result persistence is intentionally version-specific after this breaking cleanup.
    replace(
        "tests/integration/test_spark_flows.py",
        'result={"guardrail_rule_id": "freshness-rule", "status": "failed", "can_continue": False, "severity": "blocking", "message": "too old"},',
        'result={"guardrail_rule_id": "freshness-rule", "guardrail_version": 1, "status": "failed", "can_continue": False, "severity": "blocking", "message": "too old"},',
        count=1,
    )
    replace(
        "tests/unit/test_metadata.py",
        'result={"guardrail_rule_id": "schema-rule", "status": "failed"},',
        'result={"guardrail_rule_id": "schema-rule", "guardrail_version": 1, "status": "failed"},',
        count=1,
    )
    replace(
        "tests/unit/test_metadata.py",
        'result={"guardrail_rule_id": "schema-rule", "status": "passed"},',
        'result={"guardrail_rule_id": "schema-rule", "guardrail_version": 1, "status": "passed"},',
        count=1,
    )

    # Remove stale timestamp expectations now owned by the standard audit timestamp.
    replace(
        "tests/unit/test_config.py",
        '            "max_value",\n            "profiled_at",\n        }',
        '            "max_value",\n        }',
        count=1,
    )
    replace(
        "tests/unit/test_config.py",
        '        "pipeline_role",\n        "recorded_at",\n        *audit_names,',
        '        "pipeline_role",\n        *audit_names,',
        count=1,
    )

    # Stage 4E deliberately removes review lifecycle constants from widget/shared.py.
    replace(
        "tests/unit/test_dq_rules.py",
        '    assert "governance_approved" in governance_authoring.GUARDRAIL_REVIEW_STATUSES\n',
        '    assert not hasattr(governance_authoring, "GUARDRAIL_REVIEW_STATUSES")\n',
        count=1,
    )

    # These tests existed only for the retired governance-readiness compatibility helper.
    remove_top_level_functions(
        "tests/unit/test_governance_review_migration.py",
        {
            "_run_governance_readiness_for_pipeline_dq_status",
            "test_evaluate_governance_readiness_blocks_pipeline_failed_dq_status",
            "test_evaluate_governance_readiness_warns_on_pipeline_warning_dq_status",
            "test_evaluate_governance_readiness_ignores_pipeline_passed_dq_status",
        },
    )

    for path in (
        "tests/unit/test_widget_author_guardrails.py",
        "tests/integration/test_spark_flows.py",
        "tests/unit/test_metadata.py",
        "tests/unit/test_config.py",
        "tests/unit/test_dq_rules.py",
        "tests/unit/test_governance_review_migration.py",
    ):
        run("uv", "run", "ruff", "check", "--fix", path)

    run(
        "uv",
        "run",
        "pytest",
        "tests/integration/test_spark_flows.py::test_write_guardrail_result_writes_runtime_outcome_to_results_table",
        "tests/unit/test_catalogue_enrichment_widget.py",
        "tests/unit/test_config.py::test_metadata_data_catalogue_and_profiled_schema_split",
        "tests/unit/test_config.py::test_lineage_schema_has_only_lineage_fields_and_canonical_audit_context",
        "tests/unit/test_dq_rules.py::test_governance_metadata_schemas_use_catalogue_for_profile_history",
        "tests/unit/test_metadata.py::test_guardrail_result_write_fails_before_persistence_when_audit_missing",
        "tests/unit/test_metadata.py::test_guardrail_result_fallback_uses_catalogue_logical_key",
        "tests/unit/test_widget_author_guardrails.py",
        "tests/unit/test_widget_author_dq_rules.py",
    )
    run("git", "diff", "--check")


if __name__ == "__main__":
    main()
