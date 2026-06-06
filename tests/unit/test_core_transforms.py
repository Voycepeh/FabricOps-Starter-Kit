from __future__ import annotations

import pytest

from fabricops_kit.data_lineage import _build_lineage_handover_markdown, build_lineage_records
from fabricops_kit.governance_review import (
    _build_classification_records,
    _build_column_context_records,
    _build_dq_rule_records,
    _catalogue_table_options,
    _latest_by_column,
)
from fabricops_kit.handover import build_handover, render_handover_markdown

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


def test_profile_lineage_and_handover_helpers_return_notebook_ready_structures():
    profile = {"table_name": "orders", "row_count": 3, "columns": [{"column_name": "amount"}]}
    lineage = build_lineage_records(
        dataset_name="sales",
        run_id="run-1",
        source_tables=["raw_orders"],
        target_table="orders",
        transformation_steps=[{"step": "clean", "description": "Clean source rows"}],
    )
    summary = build_handover(
        runtime_context={"run_id": "run-1"},
        contract={"dataset": {"name": "orders"}},
        source_profile=profile,
        lineage_summary={"records": lineage},
    )

    assert profile["table_name"] == "orders"
    assert profile["row_count"] == 3
    assert lineage[0]["target_table"] == "orders"
    assert "orders" in render_handover_markdown(summary)
    assert "orders" in _build_lineage_handover_markdown({"records": lineage})


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
        [{"rule_id": "amount_positive", "column_name": "amount", "rule_type": "value_range", "rule_parameters": {"min": 0}, "review_status": "approved", "commit": True}],
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


def test_catalogue_and_latest_review_selection_keep_latest_approved_values():
    options = _catalogue_table_options([
        {**_profile_rows("run-1")[0], "profiled_at": "2026-01-01T00:00:00Z"},
        *_profile_rows("run-2"),
        {**_profile_rows("run-3")[0], "profile_status": "failed", "profiled_at": "2026-01-03T00:00:00Z"},
    ])
    latest = _latest_by_column(
        [
            {"metadata_column_key": "col-order", "business_context": "old", "review_status": "approved", "approved_at": "2026-01-01"},
            {"metadata_column_key": "col-order", "business_context": "new", "review_status": "approved", "approved_at": "2026-01-02"},
            {"metadata_column_key": "col-amount", "business_context": "draft", "review_status": "pending", "approved_at": "2026-01-03"},
        ]
    )

    assert len(options) == 1
    assert options[0]["profile_run_id"] == "run-2"
    assert set(latest) == {"col-order"}
    assert latest["col-order"]["business_context"] == "new"
