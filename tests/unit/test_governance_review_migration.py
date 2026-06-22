"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import fabricops_kit
import fabricops_kit.governance_review as governance
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit

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
    "setup_notebook",
    "setup_metadata_tables",
    "widget_render_data_steward",
    "widget_render_data_agreement",
    "widget_render_agreement_evidence",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "read_warehouse_query",
    "write_warehouse_table",
    "profile_dataframe",
    "get_latest_metadata_catalogue",
    "display_guardrail_results",
    "prepare_pipeline_table_configs",
    "run_table_guardrails",
    "start_pipeline_run",
    "write_pipeline_lineage",
    "write_pipeline_run_summary",
    "widget_select_guardrail_target",
    "widget_enrich_table_metadata",
    "widget_author_schema_freshness_profile_rules",
    "widget_author_dq_rules",
    "widget_review_guardrail_governance",
]

def test_public_callable_list_includes_guardrail_authoring_widgets():
    """Verify public callable list includes guardrail authoring widgets."""
    assert fabricops_kit.__all__ == EXPECTED_V1_CALLABLES
    assert len(fabricops_kit.__all__) == 26
    assert {"widget_select_agreement", "get_selected_agreement"}.isdisjoint(fabricops_kit.__all__)


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
    assert governance._validate_dq_rules(rules) == rules
    with pytest.raises(ValueError):
        governance._validate_dq_rules([{**rules[0], "rule_type": "custom"}])

    with pytest.raises(ValueError):
        governance._validate_dq_rules([{**rules[0], "rule_type": "unsupported_rule"}])


def test_governance_metadata_schemas_have_no_case_insensitive_duplicate_columns():
    """Verify governance metadata schemas have no case insensitive duplicate columns."""
    schemas = governance._get_governance_metadata_schemas()

    for table_name, schema in schemas.items():
        field_names = schema.fieldNames()
        assert len(field_names) == len({name.lower() for name in field_names}), table_name


def test_catalogue_schema_uses_lowercase_canonical_columns_only():
    """Verify catalogue schema uses lowercase canonical columns only."""
    catalogue_fields = governance._get_governance_metadata_schemas()[governance.CATALOGUE_TABLE].fieldNames()

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
    expected_catalogue_fields = {
        "metadata_table_key",
        "metadata_column_key",
        "environment_name",
        "dataset_name",
        "table_name",
        "column_name",
        "layer",
        "asset_kind",
        "pipeline_name",
        "profile_run_id",
        "profile_stage",
        "profile_status",
        "profiled_at",
        "run_timestamp",
        "evidence_role",
        "data_type",
        "row_count",
        "null_count",
        "null_percent",
        "distinct_count",
        "distinct_percent",
        "min_value",
        "max_value",
        "distribution_type",
        "distribution_json",
        "profile_mode",
        "watermark_column",
        "watermark_value",
        "profile_hash",
        "profile_payload_json",
        "agreement_id",
        "contract_version",
        "notebook_registry_id",
        "notebook_id",
        "_committed_at",
        "_committed_by",
        "_workspace_name",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    }
    removed_catalogue_fields = {
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
    assert expected_catalogue_fields <= set(catalogue_fields)
    assert removed_catalogue_fields.isdisjoint(catalogue_fields)


def test_schema_field_validation_names_table_and_duplicate_logical_columns():
    """Verify schema field validation names table and duplicate logical columns."""
    string = governance._spark_types()[3]()

    with pytest.raises(ValueError, match="METADATA_DATA_CATALOGUE.*table_name.*table_name.*TABLE_NAME"):
        governance._check_metadata_schema_field_names(
            governance.CATALOGUE_TABLE,
            [("table_name", string), ("TABLE_NAME", string)],
        )


def test_governance_metadata_schemas_include_guardrail_rules_without_failure_tables():
    """Verify governance metadata schemas include guardrail rules without failure tables."""
    schemas = governance._get_governance_metadata_schemas()

    assert governance.GUARDRAIL_RULES_TABLE in schemas
    assert governance.PIPELINE_RUNS_TABLE in schemas
    assert governance.DATA_ACCESS_TABLE in schemas
    assert governance.ENRICHMENT_RULES_TABLE in schemas
    assert "run_summary_json" in schemas[governance.PIPELINE_RUNS_TABLE].fieldNames()
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
        governance.CATALOGUE_TABLE: [
            {**selection, "profile_status": "success", "column_name": "order_id", "agreement_id": "agr-1", "contract_version": "1.0", "DQ_STATUS": "passed", "DQ_FAILED_RULE_COUNT": 0, "DQ_ERROR_RULE_COUNT": 0},
        ],
        governance.PIPELINE_RUNS_TABLE: [
            {"environment_name": "dev", "run_id": "run-001", "agreement_id": "agr-1", "status": "completed", "source_guardrail_status": "passed", "target_guardrail_status": "passed", "completed_at": "2026-01-01T00:00:00+00:00"},
            {"environment_name": "dev", "run_id": "run-002", "agreement_id": "agr-1", "status": "completed", "source_guardrail_status": "passed", "target_guardrail_status": "passed", "completed_at": "2026-01-02T00:00:00+00:00"},
        ],
        governance.DATA_AGREEMENT_TABLE: [{"agreement_id": "agr-1", "contract_version": "1.0", "agreement_name": "Orders"}],
        governance.DATA_AGREEMENT_EVIDENCE_TABLE: [{"agreement_id": "agr-1", "contract_version": "1.0", "evidence_type": "Email Approval"}],
    }

    def read_table(table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        return tables[table]

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((table, df.rows, context["env"], target, kwargs))

    monkeypatch.setattr(governance, "read_lakehouse_table", read_table)
    monkeypatch.setattr(governance, "write_lakehouse_table", write_table)

    result = governance._evaluate_governance_readiness(framework_config(), "dev", selection, spark_session=FakeSpark(), reviewed_by="reviewer@example.com")

    assert result["outcome"] == "approved"
    assert result["blockers"] == []
    assert writes == []
    assert result["review"]["pipeline_run_id"] == "run-002"
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
        governance.CATALOGUE_TABLE: [
            {**selection, "profile_status": "success", "column_name": "order_id", "agreement_id": "missing", "contract_version": "1.0", "DQ_STATUS": "failed", "DQ_FAILED_RULE_COUNT": 1, "DQ_ERROR_RULE_COUNT": 1},
        ],
        governance.PIPELINE_RUNS_TABLE: [
            {"environment_name": "dev", "run_id": "run-003", "agreement_id": "missing", "status": "completed", "source_guardrail_status": "passed", "target_guardrail_status": "warning", "dq_status": "failed", "completed_at": "2026-01-03T00:00:00+00:00"},
        ],
        governance.DATA_AGREEMENT_TABLE: [],
        governance.DATA_AGREEMENT_EVIDENCE_TABLE: [],
    }

    def read_table(table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        return tables[table]

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((table, df.rows))

    monkeypatch.setattr(governance, "read_lakehouse_table", read_table)
    monkeypatch.setattr(governance, "write_lakehouse_table", write_table)

    result = governance._evaluate_governance_readiness(framework_config(), "dev", selection, spark_session=FakeSpark())

    assert result["outcome"] == "rejected"
    assert {item["code"] for item in result["blockers"]} == {"missing_agreement_metadata", "dq_failed"}
    assert [item["code"] for item in result["blockers"]].count("dq_failed") == 1
    assert result["warnings"][0]["code"] == "target_guardrail_status_warning"
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
        governance.CATALOGUE_TABLE: [
            {
                **selection,
                "profile_status": "success",
                "column_name": "order_id",
                "agreement_id": "agr-dq",
                "contract_version": "1.0",
                "DQ_STATUS": catalogue_dq_status,
                "DQ_FAILED_RULE_COUNT": 0,
                "DQ_ERROR_RULE_COUNT": 0,
            },
        ],
        governance.PIPELINE_RUNS_TABLE: [
            {
                "environment_name": "dev",
                "run_id": selection["profile_run_id"],
                "agreement_id": "agr-dq",
                "status": "completed",
                "source_guardrail_status": "passed",
                "target_guardrail_status": "passed",
                "dq_status": pipeline_dq_status,
                "completed_at": "2026-01-04T00:00:00+00:00",
            },
        ],
        governance.DATA_AGREEMENT_TABLE: [{"agreement_id": "agr-dq", "contract_version": "1.0", "agreement_name": "Orders"}],
        governance.DATA_AGREEMENT_EVIDENCE_TABLE: [{"agreement_id": "agr-dq", "contract_version": "1.0", "evidence_type": "Email Approval"}],
    }

    def read_table(table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        return tables[table]

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((table, df.rows))

    monkeypatch.setattr(governance, "read_lakehouse_table", read_table)
    monkeypatch.setattr(governance, "write_lakehouse_table", write_table)

    result = governance._evaluate_governance_readiness(framework_config(), "dev", selection, spark_session=FakeSpark())
    return result, writes


def test_evaluate_governance_readiness_blocks_pipeline_failed_dq_status(monkeypatch):
    """Verify governance readiness blocks pipeline failed dq status."""
    result, writes = _run_governance_readiness_for_pipeline_dq_status(monkeypatch, "failed")

    assert result["outcome"] == "rejected"
    assert [item["code"] for item in result["blockers"]].count("dq_failed") == 1
    assert result["warnings"] == []
    assert writes == []
    assert result["review"]["outcome"] == "rejected"


def test_evaluate_governance_readiness_warns_on_pipeline_warning_dq_status(monkeypatch):
    """Verify governance readiness warns on pipeline warning dq status."""
    result, writes = _run_governance_readiness_for_pipeline_dq_status(monkeypatch, "warning")

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


def test_get_latest_metadata_catalogue_returns_friendly_not_found(monkeypatch):
    """Verify exploratory catalogue lookup is read-only and tolerant of missing rows."""
    monkeypatch.setattr(governance, "resolve_fabric_context", lambda context=None: (object(), "dev", {"config": object(), "env": "dev"}))
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: [])

    result = governance.get_latest_metadata_catalogue(
        table_name="orders",
        agreement={"agreement_id": "agreement-1", "contract_version": "1"},
        spark_session=None,
    )

    assert result == [
        {
            "status": "not_found",
            "table_name": "orders",
            "message": "No metadata catalogue rows found for orders. Run 02_pipeline profiling to create governed catalogue evidence.",
        }
    ]


def test_get_latest_metadata_catalogue_filters_latest_agreement_rows(monkeypatch):
    """Verify exploratory catalogue lookup returns latest matching catalogue rows."""
    rows = [
        {"table_name": "orders", "column_name": "old", "profiled_at": "2026-01-01", "agreement_id": "agreement-1", "contract_version": "1"},
        {"table_name": "orders", "column_name": "latest_a", "profiled_at": "2026-01-02", "agreement_id": "agreement-1", "contract_version": "1"},
        {"table_name": "orders", "column_name": "latest_b", "profiled_at": "2026-01-02", "agreement_id": "agreement-1", "contract_version": "1"},
        {"table_name": "orders", "column_name": "other_agreement", "profiled_at": "2026-01-03", "agreement_id": "agreement-2", "contract_version": "1"},
    ]
    monkeypatch.setattr(governance, "resolve_fabric_context", lambda context=None: (object(), "dev", {"config": object(), "env": "dev"}))
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: rows)

    result = governance.get_latest_metadata_catalogue(
        table_name="orders",
        agreement={"agreement_id": "agreement-1", "contract_version": "1"},
        spark_session=None,
    )

    assert [row["column_name"] for row in result] == ["latest_a", "latest_b"]
