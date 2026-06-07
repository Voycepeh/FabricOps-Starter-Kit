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
    "build_lineage_records",
    "build_handover",
    "render_handover_markdown",
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


def test_no_source_test_or_docs_imports_deleted_runtime_modules():
    root = Path(__file__).parents[2]
    scanned_suffixes = {".py", ".md", ".yml", ".yaml", ".json"}
    offenders: list[str] = []
    for base in [root / "src", root / "tests", root / "docs"]:
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in scanned_suffixes:
                continue
            text = path.read_text(encoding="utf-8")
            for deleted in DELETED_MODULE_IMPORTS:
                if deleted in text:
                    offenders.append(f"{path.relative_to(root)} imports {deleted}")
    assert offenders == []


def test_business_context_ai_parsing_and_suggestion_extraction():
    parsed = governance._parse_ai_dict_response("BUSINESS_CONTEXT = {'column_name': 'customer_id', 'business_context': 'Customer identifier'}")
    assert parsed["column_name"] == "customer_id"

    suggestions = governance._extract_column_business_context_suggestions(
        [{"ai_business_context_response": json.dumps({"column_name": "amount", "business_context": "Order value"})}]
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
    assert governance._extract_pii_suggestions(rows) == [
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
    assert governance._extract_candidate_rules_from_responses([{"ai_dq_response": payload}], table_name="orders") == parsed["orders"]


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
