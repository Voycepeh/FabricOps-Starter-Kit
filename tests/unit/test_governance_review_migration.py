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
    "widget_select_agreement",
    "get_selected_agreement",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "write_warehouse_table",
    "profile_dataframe",
    "validate_schema",
    "enforce_freshness",
    "enforce_profile_behavior",
    "stop_if_failed",
    "enforce_dq_rules",
    "prepare_pipeline_table_configs",
    "run_table_guardrails",
    "write_catalogue_evidence",
    "write_pipeline_lineage",
    "write_pipeline_run_summary",
    "widget_select_governance_profile_target",
    "get_selected_catalogue_table",
    "load_catalogue_profile_rows",
    "widget_review_column_context",
    "widget_review_dq_rules",
    "widget_review_column_classification",
    "record_table_governance",
]


def test_public_v1_callable_list_remains_unchanged():
    """Verify public v1 callable list remains unchanged."""
    assert fabricops_kit.__all__ == EXPECTED_V1_CALLABLES


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


def test_business_context_ai_parsing_and_suggestion_extraction():
    """Verify business context ai parsing and suggestion extraction."""
    parsed = governance._parse_ai_dict_response("BUSINESS_CONTEXT = {'column_name': 'customer_id', 'business_context': 'Customer identifier'}")
    assert parsed["column_name"] == "customer_id"

    suggestions = governance._extract_assignment_payload(
        [{"ai_business_context_response": json.dumps({"column_name": "amount", "business_context": "Order value"})}],
        response_col="ai_business_context_response",
    )
    assert suggestions == [{"column_name": "amount", "business_context": "Order value"}]


def test_governance_sensitivity_and_pii_suggestion_extraction():
    """Verify governance sensitivity and pii suggestion extraction."""
    rows = [
        {
            "ai_governance_response": json.dumps(
                {
                    "column_name": "email",
                    "ai_suggested_personal_identifier_classification": "direct_identifier",
                    "confidentiality_label": "restricted",
                }
            )
        }
    ]
    assert governance._extract_assignment_payload(rows, response_col="ai_governance_response") == [
        {
            "column_name": "email",
            "ai_suggested_personal_identifier_classification": "direct_identifier",
            "confidentiality_label": "restricted",
        }
    ]


def test_dq_ai_response_parsing_and_candidate_rule_extraction():
    """Verify dq ai response parsing and candidate rule extraction."""
    payload = "DQ_RULES = {'orders': [{'rule_id': 'id_required', 'rule_type': 'not_null', 'columns': ['order_id'], 'severity': 'error', 'description': 'Required'}]}"
    parsed = governance._parse_ai_dict_response(payload)
    assert parsed["orders"][0]["rule_id"] == "id_required"
    assert governance._extract_assignment_payload(
        [{"ai_dq_response": payload}],
        response_col="ai_dq_response",
        assignment_key="DQ_RULES",
        table_name="orders",
    ) == parsed["orders"]


def test_dq_rule_validation_rejects_unsupported_runtime_rule_types():
    """Verify dq rule validation rejects unsupported runtime rule types."""
    rules = [{"rule_id": "id_required", "rule_type": "not_null", "columns": ["id"], "severity": "error", "description": "Required"}]
    assert governance._validate_dq_rules(rules) == rules
    with pytest.raises(ValueError):
        governance._validate_dq_rules([{**rules[0], "rule_type": "custom"}])

    with pytest.raises(ValueError):
        governance._validate_dq_rules([{**rules[0], "rule_type": "unsupported_rule"}])


def test_record_table_governance_writes_context_dq_and_classification(monkeypatch):
    """Verify record table governance writes context dq and classification."""
    writes = []
    monkeypatch.setattr(governance, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((table, df.rows, env, target, kwargs)))
    profile_rows = [
        {
            "environment_name": "dev",
            "dataset_name": "sales",
            "table_name": "orders",
            "column_name": "order_id",
            "metadata_table_key": "dev|sales|orders",
            "metadata_column_key": "dev|sales|orders|order_id",
        }
    ]

    result = governance.record_table_governance(
        framework_config(),
        "dev",
        profile_rows,
        spark_session=FakeSpark(),
        context_reviews=[{"column_name": "order_id", "business_context": "Order identifier", "commit": True}],
        dq_rule_reviews=[{"rule_id": "order_id_required", "rule_type": "not_null", "columns": ["order_id"], "severity": "error", "description": "Required", "commit": True}],
        classification_reviews=[{"column_name": "order_id", "sensitivity_label": "internal", "personal_data_classification": "not_personal_data", "commit": True}],
        approved_by="reviewer@example.com",
    )

    assert {table for table, *_ in writes} == {
        governance.COLUMN_CONTEXT_TABLE,
        governance.GUARDRAIL_RULES_TABLE,
        governance.COLUMN_CLASSIFICATION_TABLE,
    }
    assert all((env, target) == ("dev", "metadata") for _, _, env, target, _ in writes)
    assert result["column_context"][0]["business_context"] == "Order identifier"
    assert result["dq_rules"][0]["rule_id"] == "order_id_required"
    assert result["dq_rules"][0]["guardrail_type"] == "dq"
    assert result["column_classification"][0]["sensitivity_label"] == "internal"



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
    assert {
        "table_name",
        "column_name",
        "row_count",
        "null_count",
        "agreement_id",
        "environment_name",
        "dataset_name",
        "pipeline_name",
        "profile_run_id",
        "dq_status",
        "source_schema_check",
        "target_schema_check",
    } <= set(catalogue_fields)


def test_schema_field_validation_names_table_and_duplicate_logical_columns():
    """Verify schema field validation names table and duplicate logical columns."""
    string = governance._spark_types()[3]()

    with pytest.raises(ValueError, match="METADATA_DATA_CATALOGUE.*table_name.*table_name.*TABLE_NAME"):
        governance._validate_schema_field_names(
            governance.CATALOGUE_TABLE,
            [("table_name", string), ("TABLE_NAME", string)],
        )


def test_governance_metadata_schemas_include_guardrail_rules_without_failure_tables():
    """Verify governance metadata schemas include guardrail rules without failure tables."""
    schemas = governance._get_governance_metadata_schemas()

    assert governance.GUARDRAIL_RULES_TABLE in schemas
    assert governance.PIPELINE_RUNS_TABLE in schemas
    assert governance.GOVERNANCE_REVIEWS_TABLE in schemas
    assert "run_summary_json" in schemas[governance.PIPELINE_RUNS_TABLE].fieldNames()
    assert "outcome" in schemas[governance.GOVERNANCE_REVIEWS_TABLE].fieldNames()
    assert not any("FAILURE" in table or "QUARANTINE" in table for table in schemas)


def test_review_governance_evidence_reads_metadata_and_writes_approved_outcome(monkeypatch):
    """Verify review governance evidence reads metadata and writes approved outcome."""
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

    monkeypatch.setattr(governance, "read_lakehouse_table", lambda config, env, target, table, **kwargs: tables[table])
    monkeypatch.setattr(governance, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((table, df.rows, env, target, kwargs)))

    result = governance._review_governance_evidence(framework_config(), "dev", selection, spark_session=FakeSpark(), reviewed_by="reviewer@example.com")

    assert result["outcome"] == "approved"
    assert result["blockers"] == []
    assert writes[0][0] == governance.GOVERNANCE_REVIEWS_TABLE
    assert writes[0][1][0]["pipeline_run_id"] == "run-002"
    assert writes[0][1][0]["agreement_id"] == "agr-1"


def test_review_governance_evidence_blocks_missing_agreement_and_failed_dq(monkeypatch):
    """Verify review governance evidence blocks missing agreement and failed dq."""
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

    monkeypatch.setattr(governance, "read_lakehouse_table", lambda config, env, target, table, **kwargs: tables[table])
    monkeypatch.setattr(governance, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((table, df.rows)))

    result = governance._review_governance_evidence(framework_config(), "dev", selection, spark_session=FakeSpark())

    assert result["outcome"] == "rejected"
    assert {item["code"] for item in result["blockers"]} == {"missing_agreement_metadata", "dq_failed"}
    assert [item["code"] for item in result["blockers"]].count("dq_failed") == 1
    assert result["warnings"][0]["code"] == "target_guardrail_status_warning"
    assert writes[0][1][0]["outcome"] == "rejected"


def _run_governance_review_for_pipeline_dq_status(monkeypatch, pipeline_dq_status: str, *, catalogue_dq_status: str = ""):
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

    monkeypatch.setattr(governance, "read_lakehouse_table", lambda config, env, target, table, **kwargs: tables[table])
    monkeypatch.setattr(governance, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((table, df.rows)))

    result = governance._review_governance_evidence(framework_config(), "dev", selection, spark_session=FakeSpark())
    return result, writes


def test_review_governance_evidence_blocks_pipeline_failed_dq_status(monkeypatch):
    """Verify review governance evidence blocks pipeline failed dq status."""
    result, writes = _run_governance_review_for_pipeline_dq_status(monkeypatch, "failed")

    assert result["outcome"] == "rejected"
    assert [item["code"] for item in result["blockers"]].count("dq_failed") == 1
    assert result["warnings"] == []
    assert writes[0][1][0]["outcome"] == "rejected"


def test_review_governance_evidence_warns_on_pipeline_warning_dq_status(monkeypatch):
    """Verify review governance evidence warns on pipeline warning dq status."""
    result, writes = _run_governance_review_for_pipeline_dq_status(monkeypatch, "warning")

    assert result["outcome"] == "needs_remediation"
    assert result["blockers"] == []
    assert [item["code"] for item in result["warnings"]] == ["dq_warning"]
    assert writes[0][1][0]["outcome"] == "needs_remediation"


def test_review_governance_evidence_ignores_pipeline_passed_dq_status(monkeypatch):
    """Verify review governance evidence ignores pipeline passed dq status."""
    result, writes = _run_governance_review_for_pipeline_dq_status(monkeypatch, "passed", catalogue_dq_status="passed")

    assert result["outcome"] == "approved"
    assert result["blockers"] == []
    assert result["warnings"] == []
    assert writes[0][1][0]["outcome"] == "approved"
