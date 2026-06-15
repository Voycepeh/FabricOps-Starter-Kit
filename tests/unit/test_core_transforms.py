from __future__ import annotations

import pytest

from fabricops_kit.data_lineage import _build_lineage_records
from tests.helpers import framework_config

from fabricops_kit.governance_review import (
    _build_classification_records,
    _build_column_context_records,
    _build_dq_rule_records,
    _catalogue_profile_target_model,
)

pytestmark = pytest.mark.unit


def _profile_rows(run: str = "run-2") -> list[dict]:
    return [
        {
            "metadata_table_key": "table-key",
            "metadata_column_key": "col-order",
            "environment_name": "dev",
            "dataset_name": "sales",
            "table_name": "orders",
            "column_name": "order_id",
            "profile_run_id": run,
            "profile_stage": "target",
            "profile_status": "success",
            "data_type": "string",
            "row_count": 10,
            "null_count": 0,
            "distinct_count": 10,
            "profiled_at": "2026-01-02T00:00:00Z",
        },
        {
            "metadata_table_key": "table-key",
            "metadata_column_key": "col-amount",
            "environment_name": "dev",
            "dataset_name": "sales",
            "table_name": "orders",
            "column_name": "amount",
            "profile_run_id": run,
            "profile_stage": "target",
            "profile_status": "success",
            "data_type": "double",
            "row_count": 10,
            "null_count": 1,
            "distinct_count": 8,
            "profiled_at": "2026-01-02T00:00:00Z",
        },
    ]


def test_profile_helper_returns_notebook_ready_structure():
    profile = {"table_name": "orders", "row_count": 3, "columns": [{"column_name": "amount"}]}

    assert profile["table_name"] == "orders"
    assert profile["row_count"] == 3


def test_private_lineage_records_use_configured_audit_timezone():
    config = framework_config()
    object.__setattr__(config, "audit_timezone", "Asia/Singapore")

    rows = _build_lineage_records(
        "sales",
        [{
            "source": "raw_orders",
            "target": "orders",
            "transformation": "clean",
            "reason": "prepare target",
            "source_type": "lakehouse_table",
            "target_type": "lakehouse_table",
            "confidence": "high",
        }],
        run_id="run-1",
        config=config,
    )

    assert rows[0]["created_ts"].endswith("+08:00")


def test_private_lineage_records_default_to_utc_without_config():
    rows = _build_lineage_records(
        "sales",
        [{
            "source": "raw_orders",
            "target": "orders",
            "transformation": "clean",
            "reason": "prepare target",
            "source_type": "lakehouse_table",
            "target_type": "lakehouse_table",
            "confidence": "high",
        }],
        run_id="run-1",
    )

    assert rows[0]["created_ts"].endswith("+00:00")


def test_governance_review_builders_commit_only_human_approved_records():
    profile_rows = _profile_rows()
    context = _build_column_context_records(
        profile_rows,
        [
            {"column_name": "order_id", "business_context": "AI only", "review_status": "approved"},
            {"column_name": "amount", "business_context": "Approved amount", "review_status": "approved", "commit": True},
        ],
        approved_by="reviewer",
    )
    dq = _build_dq_rule_records(
        profile_rows,
        [{"rule_id": "amount_positive", "columns": ["amount"], "rule_type": "greater_than", "value": 0, "review_status": "approved", "commit": True}],
    )
    classification = _build_classification_records(
        profile_rows,
        [{"column_name": "order_id", "sensitivity_label": "confidential", "personal_data_classification": "indirect_identifier", "review_status": "approved", "commit": True}],
    )

    assert [row["metadata_column_key"] for row in context] == ["col-amount"]
    assert dq[0]["rule_key"]
    assert classification[0]["metadata_column_key"] == "col-order"
    with pytest.raises(ValueError, match="Unsupported sensitivity"):
        _build_classification_records(
            profile_rows,
            [{"column_name": "order_id", "sensitivity_label": "secret", "personal_data_classification": "unknown", "review_status": "approved", "commit": True}],
        )


def test_governance_profile_target_groups_profiles_by_physical_table_not_stage_or_pipeline():
    rows = [
        {**_profile_rows("run-source-old")[0], "profile_stage": "source", "pipeline_name": "pipe-a", "profiled_at": "2026-01-01T00:00:00Z"},
        {**_profile_rows("run-target-new")[0], "profile_stage": "target", "pipeline_name": "pipe-b", "profiled_at": "2026-01-03T00:00:00Z"},
        {**_profile_rows("run-source-newer")[0], "profile_stage": "source", "pipeline_name": "pipe-c", "profiled_at": "2026-01-04T00:00:00Z"},
    ]

    model = _catalogue_profile_target_model(rows)
    asset = model["assets"]["dev / asset / sales"]
    table = asset["schemas"]["-"]["tables"]["orders"]

    assert len(table["profiles"]) == 3
    assert table["default"]["profile_run_id"] == "run-source-newer"
    assert table["default"]["profile_stage"] == "source"


def test_governance_profile_target_defaults_to_latest_successful_profile():
    rows = [
        {**_profile_rows("run-success")[0], "profile_status": "success", "profiled_at": "2026-01-02T00:00:00Z"},
        {**_profile_rows("run-failed")[0], "profile_status": "failed", "profiled_at": "2026-01-05T00:00:00Z"},
    ]

    model = _catalogue_profile_target_model(rows)
    table = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]

    assert table["default"]["profile_run_id"] == "run-success"
    assert [profile["profile_run_id"] for profile in table["profiles"]] == ["run-failed", "run-success"]


def test_governance_profile_target_defaults_to_latest_when_no_status_column_exists():
    older = {k: v for k, v in _profile_rows("run-old")[0].items() if k != "profile_status"}
    newer = {k: v for k, v in _profile_rows("run-new")[0].items() if k != "profile_status"}
    older["profiled_at"] = "2026-01-01T00:00:00Z"
    newer["profiled_at"] = "2026-01-06T00:00:00Z"

    model = _catalogue_profile_target_model([older, newer])
    table = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]

    assert table["default"]["profile_run_id"] == "run-new"


def test_governance_profile_target_profile_labels_are_readable():
    model = _catalogue_profile_target_model([
        {**_profile_rows("run-1")[0], "profile_stage": "target", "pipeline_name": "daily-pipeline", "profiled_at": "2026-01-02T00:00:00Z"}
    ])

    label = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]["profiles"][0]["label"]

    assert "2026-01-02T00:00:00Z" in label
    assert "run run-1" in label
    assert "stage target" in label
    assert "daily-pipeline" in label
    assert not label.startswith("{")
