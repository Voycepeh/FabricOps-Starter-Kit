"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

from fabricops_kit.widgets import shared as gr
from tests.helpers import FakeSpark, framework_config

from fabricops_kit.widgets.shared import (
    _build_dq_rule_records,
    build_enrichment_rule_records,
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
    """Verify profile helper returns notebook ready structure."""
    profile = {"table_name": "orders", "row_count": 3, "columns": [{"column_name": "amount"}]}

    assert profile["table_name"] == "orders"
    assert profile["row_count"] == 3



def test_governance_review_builders_commit_only_human_approved_records():
    """Verify governed intent builders commit only human-approved records."""
    profile_rows = _profile_rows()
    enrichment = build_enrichment_rule_records(
        profile_rows,
        [
            {"column_name": "order_id", "business_description": "reviewed only", "commit": False},
            {"column_name": "amount", "business_description": "Approved amount", "sensitivity_label": "restricted", "commit": True},
        ],
        state={"governance_mode": "governed", "approval_policy": "approval_required"},
        actor="reviewer",
    )
    dq = _build_dq_rule_records(
        profile_rows,
        [{"rule_id": "amount_positive", "columns": ["amount"], "rule_type": "greater_than", "value": 0, "review_status": "governance_approved", "commit": True}],
    )

    assert [row["metadata_column_key"] for row in enrichment] == ["col-amount"]
    assert enrichment[0]["review_status"] == "pending_governance_review"
    assert enrichment[0]["enrichment_payload_json"]
    assert dq[0]["rule_key"]


def test_record_table_governance_returns_rule_intent_keys_only(monkeypatch):
    """Verify table governance persists only enrichment and guardrail rule rows."""
    writes = []

    def write_table(df, table, *, target, context, **kwargs):
        assert target == "metadata"
        assert context["env"] == "dev"
        writes.append((table, df))

    monkeypatch.setattr(gr, "write_lakehouse_table_core", write_table)
    monkeypatch.setattr(
        gr,
        "build_runtime_audit_fields",
        lambda **_kwargs: {
            "_committed_by": "reviewer",
            "_committed_at": "2026-01-01T00:00:00Z",
            "_workspace_id": "workspace-id",
            "_workspace_name": "workspace",
            "_notebook_id": "notebook-id",
            "_notebook_name": "notebook",
            "_metadata_lakehouse_name": "metadata",
            "_activity_id": "activity-id",
        },
    )

    result = gr.record_table_governance(
        framework_config(),
        "dev",
        _profile_rows(),
        spark_session=FakeSpark(),
        enrichment_reviews=[
            {
                "column_name": "amount",
                "business_description": "Approved amount",
                "classification": "financial",
                "commit": True,
            }
        ],
        guardrail_rule_reviews=[
            {
                "rule_id": "amount_positive",
                "column_name": "amount",
                "rule_type": "greater_than",
                "columns": ["amount"],
                "value": 0,
                "severity": "error",
                "commit": True,
            }
        ],
        approved_by="reviewer",
    )

    assert set(result) == {"enrichment_rules", "guardrail_rules", "readiness_summary"}
    assert "column_context" not in result
    assert "column_classification" not in result
    assert "governance_review" not in result
    assert [table for table, _ in writes] == [gr.ENRICHMENT_RULES_TABLE, gr.GUARDRAIL_RULES_TABLE]


def test_load_rule_review_history_reads_enrichment_and_guardrail_rows():
    """Verify approval history is derived from append-only rule rows."""
    rows = [
        {
            "enrichment_rule_id": "enrich-1",
            "enrichment_rule_version": "v1",
            "metadata_table_key": "table-key",
            "metadata_column_key": "col-amount",
            "column_name": "amount",
            "enrichment_type": "classification",
            "review_status": "proposed",
            "is_active": False,
            "submitted_by": "engineer",
            "submitted_at": "2026-01-01T00:00:00Z",
        },
        {
            "rule_id": "guardrail-1",
            "rule_version": "v2",
            "metadata_table_key": "table-key",
            "metadata_column_key": "col-amount",
            "column_name": "amount",
            "guardrail_type": "dq",
            "review_status": "governance_approved",
            "is_active": True,
            "reviewed_by": "steward",
            "reviewed_at": "2026-01-02T00:00:00Z",
        },
    ]

    history = gr.load_rule_review_history(rows, metadata_column_key="col-amount")

    assert [entry["rule_id"] for entry in history] == ["guardrail-1", "enrich-1"]
    assert [entry["record_type"] for entry in history] == ["guardrail", "enrichment"]
    assert history[0]["rule_version"] == "v2"
    assert history[1]["rule_version"] == "v1"


def test_catalogue_profile_loader_uses_physical_identity_helper(monkeypatch):
    """Verify loader delegates table matching to the shared physical identity helper."""
    rows = _profile_rows("run-shared")
    selection = {
        "environment_name": "dev",
        "asset_kind": "",
        "asset_name": "sales",
        "dataset_name": "sales",
        "schema_or_layer": "",
        "layer": "",
        "schema_name": "",
        "table_name": "orders",
        "metadata_table_key": "table-key",
        "profile_run_id": "run-shared",
        "profile_stage": "target",
    }
    calls = []
    original = gr._catalogue_physical_identity

    def tracking_identity(row):
        calls.append(row)
        return original(row)

    monkeypatch.setattr(gr, "read_lakehouse_table_core", lambda *args, **kwargs: rows)
    monkeypatch.setattr(gr, "_catalogue_physical_identity", tracking_identity)

    loaded = gr.load_catalogue_profile_rows(framework_config(), "dev", selection, spark_session=None)

    assert len(loaded) == 2
    assert selection in calls
    assert rows[0] in calls
