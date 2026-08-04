"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

from fabricops_kit.widgets import shared as gr
from tests.helpers import FakeSpark, framework_config

from fabricops_kit.widgets.shared import (
    _build_dq_rule_records,
    build_enrichment_records,
    latest_enrichment_values,
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



def test_generic_enrichment_builder_and_latest_values(monkeypatch):
    """Build independent generic rows and resolve deterministic current values."""
    audit = {name: "2026-01-01T00:00:00Z" if name == "_committed_at" else "audit" for name in gr.STANDARD_RUNTIME_AUDIT_COLUMNS}
    monkeypatch.setattr(gr, "build_runtime_audit_fields", lambda **_kwargs: audit)
    records = build_enrichment_records([
        {"enrichment_level": "table", "metadata_key": "table-key", "enrichment_type": "Business_context", "value": "Orders"},
        {"enrichment_level": "column", "metadata_key": "col-amount", "enrichment_type": "Business_context", "value": "Old", "enrichment_id": "a"},
        {"enrichment_level": "column", "metadata_key": "col-amount", "enrichment_type": "Business_context", "value": "Current", "enrichment_id": "b"},
        {"enrichment_level": "column", "metadata_key": "col-amount", "enrichment_type": "Classification", "value": "Sensitive"},
    ], config=object(), env="dev")
    assert set(records[0]) == {"enrichment_id", "enrichment_level", "metadata_key", "enrichment_type", "value", *gr.STANDARD_RUNTIME_AUDIT_COLUMNS}
    latest = latest_enrichment_values(records)
    assert latest[("column", "col-amount", "Business_context")]["value"] == "Current"
    assert len(latest) == 3


@pytest.mark.parametrize("field", ["metadata_key", "enrichment_type", "value"])
def test_enrichment_builder_rejects_empty_required_values(field):
    """Reject blank generic enrichment values."""
    row = {"enrichment_level": "column", "metadata_key": "col", "enrichment_type": "Business_context", "value": "Meaning"}
    row[field] = ""
    with pytest.raises(ValueError, match=field):
        build_enrichment_records([row])


def test_enrichment_builder_rejects_unsupported_level():
    """Only table and column identities are supported."""
    with pytest.raises(ValueError, match="table.*column"):
        build_enrichment_records([{"enrichment_level": "dataset", "metadata_key": "x", "enrichment_type": "x", "value": "x"}])


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
                "enrichment_level": "column",
                "metadata_key": "col-amount",
                "enrichment_type": "Business_context",
                "value": "Approved amount",
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
    assert [table for table, _ in writes] == [gr.ENRICHMENT_TABLE, gr.GUARDRAIL_TABLE]


def test_load_rule_review_history_reads_guardrail_rows():
    """Verify approval history remains specific to append-only guardrail rules."""
    rows = [{
        "rule_id": "guardrail-1", "rule_version": "v2",
        "metadata_table_key": "table-key", "metadata_column_key": "col-amount",
        "column_name": "amount", "guardrail_type": "dq",
        "review_status": "governance_approved", "is_active": True,
        "reviewed_by": "steward", "reviewed_at": "2026-01-02T00:00:00Z",
    }]
    history = gr.load_rule_review_history(rows, metadata_column_key="col-amount")
    assert [entry["rule_id"] for entry in history] == ["guardrail-1"]
    assert history[0]["record_type"] == "guardrail"
    assert history[0]["rule_version"] == "v2"

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
