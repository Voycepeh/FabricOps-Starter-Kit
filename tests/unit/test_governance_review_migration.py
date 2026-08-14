"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import fabricops_kit
from fabricops_kit.pipeline import guardrails_shared as dq_runtime
from fabricops_kit.config import metadata_schemas
from fabricops_kit.widgets import shared as governance
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit

@pytest.fixture(autouse=True)
def _canonical_audit(monkeypatch):
    """Provide deterministic canonical audit fields for governance tests."""
    audit = {"_workspace_id": "workspace-id", "_workspace_name": "workspace", "_notebook_id": "notebook-id", "_notebook_name": "notebook", "_activity_id": "activity-id", "_committed_by": "user", "_committed_at": "2026-01-01T00:00:00+00:00", "_metadata_lakehouse_name": "metadata"}
    monkeypatch.setattr(governance, "build_runtime_audit_fields", lambda **kwargs: dict(audit))


DELETED_MODULE_SUFFIXES = (
    "business_context",
    "data_governance",
    "data_quality",
    "_utils",
    "versioning",
    "docs_metadata",
    "hand" + "over",
)
DELETED_MODULE_IMPORTS = tuple(f"fabricops_kit.{suffix}" for suffix in DELETED_MODULE_SUFFIXES)

EXPECTED_V1_CALLABLES = [
    'FabricStore',
    'PathConfig',
    'GovernanceConfig',
    'DataAgreementConfig',
    'FrameworkConfig',
    'ConfigSmokeCheckResult',
    'NotebookSetupContext',
    'setup_notebook',
    'setup_metadata_tables',
    'read_lakehouse_table',
    'write_lakehouse_table',
    'read_lakehouse_csv',
    'read_lakehouse_parquet',
    'read_lakehouse_excel',
    'read_warehouse_table',
    'read_warehouse_query',
    'write_warehouse_table',
    'check_schema',
    'check_freshness',
    'check_changes',
    'profile_and_register_table',
    'profile_dataframe',
    'profile_frequency_distribution',
    'display_guardrail_results',
    'observe_table',
    'run_table_guardrails',
    'widget_render_data_steward',
    'widget_render_data_agreement',
    'widget_select_guardrail_target',
    'widget_enrich_table_metadata',
    'widget_author_schema_freshness_profile_rules',
    'widget_view_agreement_catalogue',
    'widget_view_pipeline_catalogue',
    'widget_view_data_catalogue',
    'widget_register_data_contract',
    'widget_author_dq_rules',
    'widget_review_guardrail_governance',
]

def test_public_callable_list_includes_guardrail_authoring_widgets():
    """Verify public callable list includes guardrail authoring widgets."""
    assert fabricops_kit.__all__ == EXPECTED_V1_CALLABLES
    assert len(fabricops_kit.__all__) == len(EXPECTED_V1_CALLABLES)
    assert "get_selected_agreement" not in fabricops_kit.__all__


def test_widget_public_callables_live_under_widgets_package():
    """Verify the public widget surface is owned by fabricops_kit.widgets."""
    import fabricops_kit.widgets as widgets

    widget_names = {
        'widget_author_dq_rules',
        'widget_author_schema_freshness_profile_rules',
        'widget_view_agreement_catalogue',
        'widget_view_pipeline_catalogue',
        'widget_view_data_catalogue',
        'widget_enrich_table_metadata',
        'widget_render_data_agreement',
        'widget_render_data_steward',
        'widget_review_guardrail_governance',
        'widget_select_guardrail_target',
    }
    for name in widget_names:
        value = getattr(widgets, name)
        if not hasattr(value, "__module__"):
            import importlib

            value = getattr(importlib.import_module(f"fabricops_kit.widgets.{name}"), name)
        assert value.__module__.startswith(f"fabricops_kit.widgets.{name}")


def test_widget_modules_do_not_call_public_widget_functions():
    """Verify widget entrypoint modules do not call other public widget functions."""
    import ast

    root = Path(__file__).parents[2]
    widgets_dir = root / "src" / "fabricops_kit" / "widgets"
    public_widget_names = {
        'widget_author_dq_rules',
        'widget_author_schema_freshness_profile_rules',
        'widget_view_agreement_catalogue',
        'widget_view_pipeline_catalogue',
        'widget_view_data_catalogue',
        'widget_enrich_table_metadata',
        'widget_render_data_agreement',
        'widget_render_data_steward',
        'widget_review_guardrail_governance',
        'widget_select_guardrail_target',
    }
    offenders = []
    for path in widgets_dir.glob("widget_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        owned = path.stem
        for node in ast.walk(tree):
            called = None
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called = node.func.id
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                called = node.func.attr
            if called in public_widget_names - {owned}:
                offenders.append(f"{path.relative_to(root)} calls {called}")
    assert offenders == []


def test_widget_modules_do_not_import_private_shared_widget_helpers():
    """Verify widget modules use architecture-visible helpers from widgets.shared."""
    import ast

    root = Path(__file__).parents[2]
    widgets_dir = root / "src" / "fabricops_kit" / "widgets"
    offenders = []
    for path in widgets_dir.glob("widget_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.module != "fabricops_kit.widgets.shared":
                continue
            for alias in node.names:
                if alias.name.startswith("_"):
                    offenders.append(f"{path.relative_to(root)} imports {alias.name} from widgets.shared")
    assert offenders == []


def test_no_source_tests_docs_or_templates_reference_removed_modules_or_callables():
    """Verify no source tests docs or templates reference removed modules or callables."""
    root = Path(__file__).parents[2]
    scanned_suffixes = {".py", ".md", ".yml", ".yaml", ".json", ".ipynb"}
    removed_callables = (
        "build" + "_hand" + "over",
        "render" + "_hand" + "over_markdown",
        "_build" + "_hand" + "over_record",
        "_write_metadata_rows" + "_leg" + "acy",
        "_get" + "_notebook_registry_schema",
        "configure" + "_ai",
        "Config" + "BootstrapResult",
        )
    removed_module_files = tuple(f"fabricops_kit/{suffix}.py" for suffix in DELETED_MODULE_SUFFIXES)
    offenders: list[str] = []
    for base in [root / "src", root / "tests", root / "docs", root / "templates"]:
        for path in base.rglob("*"):
            if path == Path(__file__) or not path.is_file() or path.suffix not in scanned_suffixes:
                continue
            text = path.read_text(encoding="utf-8")
            for deleted in (*DELETED_MODULE_IMPORTS, *removed_module_files, *removed_callables):
                comparable_text = text.replace("\\", "/")
                if deleted in comparable_text:
                    offenders.append(f"{path.relative_to(root)} references {deleted}")
    assert offenders == []


def test_dq_rule_validation_rejects_unsupported_runtime_rule_types():
    """Verify dq rule validation rejects unsupported runtime rule types."""
    rules = [{"rule_id": "id_required", "rule_type": "not_null", "columns": ["id"], "severity": "error", "description": "Required"}]
    assert dq_runtime._validate_dq_rules(rules) == rules
    with pytest.raises(ValueError):
        dq_runtime._validate_dq_rules([{**rules[0], "rule_type": "custom"}])

    with pytest.raises(ValueError):
        dq_runtime._validate_dq_rules([{**rules[0], "rule_type": "unsupported_rule"}])


def test_governance_metadata_schemas_have_no_case_insensitive_duplicate_columns():
    """Verify governance metadata schemas have no case insensitive duplicate columns."""
    schemas = metadata_schemas.metadata_table_schema_registry()

    for table_name, schema in schemas.items():
        field_names = schema.fieldNames()
        assert len(field_names) == len({name.lower() for name in field_names}), table_name


def test_catalogue_schema_uses_lowercase_canonical_columns_only():
    """Verify catalogue schema uses lowercase canonical columns only."""
    catalogue_fields = metadata_schemas.metadata_table_schema_registry()[governance.CATALOGUE_TABLE].fieldNames()

    assert all(field == field.lower() for field in catalogue_fields)

    duplicate_legacy_fields = {
        "TABLE_NAME",
        "COLUMN_NAME",
        "ROW_COUNT",
        "NULL_COUNT",
        "AGREEMENT_ID",
        "ENVIRONMENT_NAME",
        "DATASET_NAME",
        "PIPELINE_NAME",
        "PROFILE_RUN_ID",
    }
    assert duplicate_legacy_fields.isdisjoint(catalogue_fields)
    expected_catalogue_fields = [
        "metadata_table_key",
        "metadata_column_key",
        "schema_fingerprint",
        "environment_name",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "data_type",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
    retired_catalogue_fields = {
        "dataset_name",
        "asset_kind",
        "profile_stage",
        "profile_status",
        "evidence_role",
        "distribution_type",
        "distribution_json",
        "profile_mode",
        "watermark_column",
        "watermark_value",
        "profile_hash",
        "profile_payload_json",
        "row_count",
        "non_null_count",
        "null_count",
        "null_percent",
        "distinct_count",
        "distinct_percent",
        "mean_value",
        "stddev_value",
        "min_value",
        "percentile_25_value",
        "median_value",
        "percentile_75_value",
        "max_value",
        "frequency_json",
        "profiled_at",
        "agreement_id",
        "agreement_version",
    }
    removed_catalogue_fields = retired_catalogue_fields | {
        "baseline_status",
        "source_schema_check",
        "target_schema_check",
        "dq_status",
        "dq_rule_count",
        "dq_failed_rule_count",
        "dq_failed_row_count",
        "load_behavior",
        "source_data_change_check",
        "target_data_change_check",
        "source_change_signal_json",
    }
    assert catalogue_fields == expected_catalogue_fields
    assert removed_catalogue_fields.isdisjoint(catalogue_fields)


def test_schema_field_validation_names_table_and_duplicate_logical_columns():
    """Verify schema field validation names table and duplicate logical columns."""
    with pytest.raises(ValueError, match="METADATA_DATA_CATALOGUE.*table_name.*table_name.*TABLE_NAME"):
        metadata_schemas.build_metadata_schema(
            governance.CATALOGUE_TABLE,
            [("table_name", "string"), ("TABLE_NAME", "string")],
        )


def test_governance_metadata_schemas_include_guardrail_rules_without_failure_tables():
    """Verify governance metadata schemas include guardrail rules without failure tables."""
    schemas = metadata_schemas.metadata_table_schema_registry()

    assert governance.GUARDRAIL_TABLE in schemas
    assert "METADATA_DATA_PROFILED" in schemas
    assert governance.DATA_ACCESS_TABLE in schemas
    assert governance.ENRICHMENT_TABLE in schemas
    assert "metadata_table_key" in schemas["METADATA_DATA_PROFILED"].fieldNames()
    required_audit_fields = {
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    }
    for table_name, schema in schemas.items():
        assert required_audit_fields.issubset(schema.fieldNames()), table_name
    assert not any("FAILURE" in table or "QUARANTINE" in table for table in schemas)


def test_evaluate_governance_readiness_reads_metadata_and_writes_approved_outcome(monkeypatch):
    """Verify governance readiness reads metadata and writes approved outcome."""
    writes = []
    selection = {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "dev|sales|orders",
        "profile_run_id": "run-002",
        "profile_stage": "target",
    }
    tables = {
        governance.PROFILED_TABLE: [
            {**selection, "profile_status": "success", "column_name": "order_id", "agreement_id": "agr-1", "agreement_version": "1.0", "DQ_STATUS": "passed", "DQ_FAILED_RULE_COUNT": 0, "DQ_ERROR_RULE_COUNT": 0},
        ],
        governance.DATA_AGREEMENT_TABLE: [{"agreement_id": "agr-1", "agreement_version": "1.0", "agreement_name": "Orders"}],
    }

    def read_table(table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        return tables[table]

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((table, df.rows, context["env"], target, kwargs))

    monkeypatch.setattr(governance, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(governance, "write_lakehouse_table_core", write_table)

    result = governance._evaluate_governance_readiness(framework_config(), "dev", selection, spark_session=FakeSpark(), reviewed_by="reviewer@example.com")

    assert result["outcome"] == "approved"
    assert result["blockers"] == []
    assert writes == []
    assert result["review"]["pipeline_run_id"] == ""
    assert result["review"]["agreement_id"] == "agr-1"


def test_evaluate_governance_readiness_blocks_missing_agreement_and_failed_dq(monkeypatch):
    """Verify governance readiness blocks missing agreement and failed dq."""
    writes = []
    selection = {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "dev|sales|orders",
        "profile_run_id": "run-003",
        "profile_stage": "target",
    }
    tables = {
        governance.PROFILED_TABLE: [
            {**selection, "profile_status": "success", "column_name": "order_id", "agreement_id": "missing", "agreement_version": "1.0", "DQ_STATUS": "failed", "DQ_FAILED_RULE_COUNT": 1, "DQ_ERROR_RULE_COUNT": 1},
        ],
        governance.DATA_AGREEMENT_TABLE: [],
    }

    def read_table(table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        return tables[table]

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((table, df.rows))

    monkeypatch.setattr(governance, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(governance, "write_lakehouse_table_core", write_table)

    result = governance._evaluate_governance_readiness(framework_config(), "dev", selection, spark_session=FakeSpark())

    assert result["outcome"] == "rejected"
    assert {item["code"] for item in result["blockers"]} == {"missing_agreement_metadata", "dq_failed"}
    assert [item["code"] for item in result["blockers"]].count("dq_failed") == 1
    assert writes == []
    assert result["review"]["outcome"] == "rejected"


def _run_governance_readiness_for_pipeline_dq_status(monkeypatch, pipeline_dq_status: str, *, catalogue_dq_status: str = ""):
    writes = []
    selection = {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "dev|sales|orders",
        "profile_run_id": f"run-dq-{pipeline_dq_status or 'blank'}",
        "profile_stage": "target",
    }
    tables = {
        governance.PROFILED_TABLE: [
            {
                **selection,
                "profile_status": "success",
                "column_name": "order_id",
                "agreement_id": "agr-dq",
                "agreement_version": "1.0",
                "DQ_STATUS": catalogue_dq_status,
                "DQ_FAILED_RULE_COUNT": 0,
                "DQ_ERROR_RULE_COUNT": 0,
            },
        ],
        governance.DATA_AGREEMENT_TABLE: [{"agreement_id": "agr-dq", "agreement_version": "1.0", "agreement_name": "Orders"}],
    }

    def read_table(table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        return tables[table]

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((table, df.rows))

    monkeypatch.setattr(governance, "read_lakehouse_table_core", read_table)
    monkeypatch.setattr(governance, "write_lakehouse_table_core", write_table)

    result = governance._evaluate_governance_readiness(framework_config(), "dev", selection, spark_session=FakeSpark())
    return result, writes


def test_evaluate_governance_readiness_blocks_pipeline_failed_dq_status(monkeypatch):
    """Verify governance readiness blocks pipeline failed dq status."""
    result, writes = _run_governance_readiness_for_pipeline_dq_status(monkeypatch, "failed", catalogue_dq_status="failed")

    assert result["outcome"] == "rejected"
    assert [item["code"] for item in result["blockers"]].count("dq_failed") == 1
    assert result["warnings"] == []
    assert writes == []
    assert result["review"]["outcome"] == "rejected"


def test_evaluate_governance_readiness_warns_on_pipeline_warning_dq_status(monkeypatch):
    """Verify governance readiness warns on pipeline warning dq status."""
    result, writes = _run_governance_readiness_for_pipeline_dq_status(monkeypatch, "warning", catalogue_dq_status="warning")

    assert result["outcome"] == "needs_remediation"
    assert result["blockers"] == []
    assert [item["code"] for item in result["warnings"]] == ["dq_warning"]
    assert writes == []
    assert result["review"]["outcome"] == "needs_remediation"


def test_evaluate_governance_readiness_ignores_pipeline_passed_dq_status(monkeypatch):
    """Verify governance readiness ignores pipeline passed dq status."""
    result, writes = _run_governance_readiness_for_pipeline_dq_status(monkeypatch, "passed", catalogue_dq_status="passed")

    assert result["outcome"] == "approved"
    assert result["blockers"] == []
    assert result["warnings"] == []
    assert writes == []
    assert result["review"]["outcome"] == "approved"


def test_retired_governance_review_module_file_and_imports_are_absent():
    """Verify the stale mixed governance review module and imports are absent."""
    root = Path(__file__).parents[2]
    assert not (root / "src" / "fabricops_kit" / "governance_review.py").exists()
    assert not (root / "src" / "fabricops_kit" / "governance_lookup.py").exists()
    assert "get_latest_metadata_catalogue" not in fabricops_kit.__all__
    scanned_suffixes = {".py", ".md", ".yml", ".yaml", ".json", ".ipynb"}
    offenders = []
    for base in [root / "src", root / "templates", root / "docs"]:
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in scanned_suffixes:
                continue
            text = path.read_text(encoding="utf-8")
            if path == Path(__file__):
                continue
            if (
                "fabricops_kit.governance_review" in text
                or "from .governance_review import" in text
                or "import fabricops_kit.governance_lookup" in text
                or "from fabricops_kit.governance_lookup" in text
                or "from fabricops_kit import governance_lookup" in text
            ):
                offenders.append(str(path.relative_to(root)))

    for path in (root / "tests").rglob("*.py"):
        if path == Path(__file__):
            continue
        text = path.read_text(encoding="utf-8")
        if (
            "import fabricops_kit.governance_lookup" in text
            or "from fabricops_kit.governance_lookup" in text
            or "from fabricops_kit import governance_lookup" in text
        ):
            offenders.append(str(path.relative_to(root)))
    assert offenders == []


def test_pipeline_and_config_use_new_governance_owners():
    """Verify DQ runtime and metadata schema helpers are owned outside governance review."""
    root = Path(__file__).parents[2]
    pipeline_source = (root / "src" / "fabricops_kit" / "pipeline/shared.py").read_text(encoding="utf-8")
    config_source = (root / "src" / "fabricops_kit" / "config" / "shared.py").read_text(encoding="utf-8")

    assert "from fabricops_kit.pipeline.guardrails_shared import run_active_dq_guardrail" in pipeline_source
    assert "from .governance_review" not in pipeline_source
    assert "governance_lookup" not in pipeline_source
    assert "CATALOGUE_TABLE = \"METADATA_DATA_CATALOGUE\"" in pipeline_source
    assert "metadata_table_schema_registry" in config_source
    assert "governance_review" not in config_source



def test_99_explore_uses_metadata_catalogue_widget():
    """Verify 99_explore uses the public catalogue browser widget."""
    root = Path(__file__).parents[2]

    notebook = json.loads((root / "templates" / "notebooks" / "99_explore.ipynb").read_text(encoding="utf-8"))
    code = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code")

    assert "get_latest_metadata_catalogue" not in code
    assert "widget_view_data_catalogue" in code
    assert "widget_view_data_contract" not in code
    assert "METADATA_DATA_CATALOGUE" not in code
    assert 'F.col("table_name") == source_table_name' not in code


def test_root_public_governance_and_widget_imports_still_work():
    """Verify supported root governance and widget imports remain available."""
    for name in [
        "widget_author_dq_rules",
        "widget_author_schema_freshness_profile_rules",
        "widget_enrich_table_metadata",
        "widget_review_guardrail_governance",
        "widget_select_guardrail_target",
    ]:
        assert callable(getattr(fabricops_kit, name))
