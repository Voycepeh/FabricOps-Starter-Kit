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
    "monitor_data_changes",
    "stop_if_failed",
    "enforce_dq_rules",
    "build_lineage_records",
    "widget_select_catalogue_table",
    "get_selected_catalogue_table",
    "load_catalogue_profile_rows",
    "widget_review_column_context",
    "widget_review_dq_rules",
    "widget_review_column_classification",
    "record_table_governance",
]


def test_public_v1_callable_list_remains_unchanged():
    assert fabricops_kit.__all__ == EXPECTED_V1_CALLABLES


def test_no_source_tests_docs_or_templates_reference_removed_modules_or_callables():
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
    parsed = governance._parse_ai_dict_response("BUSINESS_CONTEXT = {'column_name': 'customer_id', 'business_context': 'Customer identifier'}")
    assert parsed["column_name"] == "customer_id"

    suggestions = governance._extract_assignment_payload(
        [{"ai_business_context_response": json.dumps({"column_name": "amount", "business_context": "Order value"})}],
        response_col="ai_business_context_response",
    )
    assert suggestions == [{"column_name": "amount", "business_context": "Order value"}]


def test_governance_sensitivity_and_pii_suggestion_extraction():
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
    payload = "DQ_RULES = {'orders': [{'rule_id': 'id_required', 'rule_type': 'not_null', 'columns': ['order_id'], 'severity': 'error', 'description': 'Required'}]}"
    parsed = governance._parse_ai_dict_response(payload)
    assert parsed["orders"][0]["rule_id"] == "id_required"
    assert governance._extract_assignment_payload(
        [{"ai_dq_response": payload}],
        response_col="ai_dq_response",
        assignment_key="DQ_RULES",
        table_name="orders",
    ) == parsed["orders"]


def test_dq_rule_validation_and_enforcement_result_shape():
    rules = [{"rule_id": "id_required", "rule_type": "not_null", "columns": ["id"], "severity": "error", "description": "Required"}]
    assert governance._validate_dq_rules(rules) == rules
    with pytest.raises(ValueError):
        governance._validate_dq_rules([{**rules[0], "rule_type": "custom"}])

    result = governance.DQEnforcementResult(rules=rules, rule_results="results", valid_rows="valid", quarantine_rows="quarantine", failure_rows="failures")
    assert result.rules == rules
    assert result.rule_results == "results"
    assert result.valid_rows == "valid"
    assert result.quarantine_rows == "quarantine"
    assert result.failure_rows == "failures"


def test_record_table_governance_writes_context_dq_and_classification(monkeypatch):
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
        governance.DQ_RULES_TABLE,
        governance.COLUMN_CLASSIFICATION_TABLE,
    }
    assert all((env, target) == ("dev", "metadata") for _, _, env, target, _ in writes)
    assert result["column_context"][0]["business_context"] == "Order identifier"
    assert result["dq_rules"][0]["rule_id"] == "order_id_required"
    assert result["column_classification"][0]["sensitivity_label"] == "internal"



def test_governance_metadata_schemas_do_not_add_dq_failure_tables():
    schemas = governance._get_governance_metadata_schemas()

    assert governance.DQ_RULES_TABLE in schemas
    assert not any("FAILURE" in table or "QUARANTINE" in table for table in schemas)
