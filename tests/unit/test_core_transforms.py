"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

import fabricops_kit.governance_review as gr
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
    """Verify profile helper returns notebook ready structure."""
    profile = {"table_name": "orders", "row_count": 3, "columns": [{"column_name": "amount"}]}

    assert profile["table_name"] == "orders"
    assert profile["row_count"] == 3


def test_private_lineage_records_use_configured_audit_timezone():
    """Verify private lineage records use configured audit timezone."""
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
    """Verify private lineage records default to utc without config."""
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
    """Verify governance review builders commit only human approved records."""
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
        [{"rule_id": "amount_positive", "columns": ["amount"], "rule_type": "greater_than", "value": 0, "review_status": "governance_approved", "commit": True}],
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
    """Verify governance profile target groups profiles by physical table not stage or pipeline."""
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
    """Verify governance profile target defaults to latest successful profile."""
    rows = [
        {**_profile_rows("run-success")[0], "profile_status": "success", "profiled_at": "2026-01-02T00:00:00Z"},
        {**_profile_rows("run-failed")[0], "profile_status": "failed", "profiled_at": "2026-01-05T00:00:00Z"},
    ]

    model = _catalogue_profile_target_model(rows)
    table = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]

    assert table["default"]["profile_run_id"] == "run-success"
    assert [profile["profile_run_id"] for profile in table["profiles"]] == ["run-success"]
    assert [profile["profile_run_id"] for profile in table["history_profiles"]] == ["run-failed"]


def test_governance_profile_target_defaults_to_latest_when_no_status_column_exists():
    """Verify governance profile target defaults to latest when no status column exists."""
    older = {k: v for k, v in _profile_rows("run-old")[0].items() if k != "profile_status"}
    newer = {k: v for k, v in _profile_rows("run-new")[0].items() if k != "profile_status"}
    older["profiled_at"] = "2026-01-01T00:00:00Z"
    newer["profiled_at"] = "2026-01-06T00:00:00Z"

    model = _catalogue_profile_target_model([older, newer])
    table = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]

    assert table["default"]["profile_run_id"] == "run-new"


def test_governance_profile_target_profile_labels_are_readable():
    """Verify governance profile target profile labels are readable."""
    model = _catalogue_profile_target_model([
        {**_profile_rows("run-1")[0], "profile_stage": "target", "pipeline_name": "daily-pipeline", "profiled_at": "2026-01-02T00:00:00Z"}
    ])

    label = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]["profiles"][0]["label"]

    assert "2026-01-02T00:00:00Z" in label
    assert "run run-1" in label
    assert "stage target" in label
    assert "daily-pipeline" in label
    assert not label.startswith("{")


def test_governance_profile_target_supports_asset_name_without_dataset_name(monkeypatch):
    """Verify selector identities and loader rows work when only asset_name is populated."""
    rows = []
    for row in _profile_rows("run-asset"):
        updated = {**row, "asset_name": "sales", "lakehouse_name": "sales"}
        updated.pop("dataset_name")
        rows.append(updated)

    model = _catalogue_profile_target_model(rows)
    selection = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]["default"]
    monkeypatch.setattr(gr, "read_lakehouse_table", lambda *args, **kwargs: rows)

    loaded = gr.load_catalogue_profile_rows(framework_config(), "dev", selection, spark_session=None)

    assert selection["asset_name"] == "sales"
    assert selection["dataset_name"] == "sales"
    assert [row["column_name"] for row in loaded] == ["order_id", "amount"]


def test_governance_profile_target_keeps_source_and_target_profiles_selectable(monkeypatch):
    """Verify same physical table profiled as source and target can load exact selected stage."""
    source_rows = [{**row, "profile_run_id": "run-source", "profile_stage": "source", "profiled_at": "2026-01-03T00:00:00Z"} for row in _profile_rows("run-source")]
    target_rows = [{**row, "profile_run_id": "run-target", "profile_stage": "target", "profiled_at": "2026-01-04T00:00:00Z"} for row in _profile_rows("run-target")]
    rows = source_rows + target_rows

    model = _catalogue_profile_target_model(rows)
    profiles = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]["profiles"]
    source_selection = next(profile for profile in profiles if profile["profile_stage"] == "source")
    monkeypatch.setattr(gr, "read_lakehouse_table", lambda *args, **kwargs: rows)

    loaded = gr.load_catalogue_profile_rows(framework_config(), "dev", source_selection, spark_session=None)

    assert {profile["profile_stage"] for profile in profiles} == {"source", "target"}
    assert {row["profile_stage"] for row in loaded} == {"source"}
    assert {row["profile_run_id"] for row in loaded} == {"run-source"}


def test_governance_profile_target_hides_failed_latest_profile_from_review_options():
    """Verify failed latest profiles remain history only and do not become review targets."""
    rows = [
        {**_profile_rows("run-success")[0], "profile_status": "success", "profiled_at": "2026-01-02T00:00:00Z"},
        {**_profile_rows("run-failed")[0], "profile_status": "failed", "profiled_at": "2026-01-05T00:00:00Z"},
    ]

    model = _catalogue_profile_target_model(rows)
    table = model["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]

    assert table["default"]["profile_run_id"] == "run-success"
    assert [profile["profile_run_id"] for profile in table["profiles"]] == ["run-success"]
    assert table["history_profiles"][0]["profile_run_id"] == "run-failed"
    assert table["history_profiles"][0]["history_only"] is True


def test_catalogue_profile_loader_uses_physical_identity_helper(monkeypatch):
    """Verify loader delegates table matching to the shared physical identity helper."""
    rows = _profile_rows("run-shared")
    selection = _catalogue_profile_target_model(rows)["assets"]["dev / asset / sales"]["schemas"]["-"]["tables"]["orders"]["default"]
    calls = []
    original = gr._catalogue_physical_identity

    def tracking_identity(row):
        calls.append(row)
        return original(row)

    monkeypatch.setattr(gr, "read_lakehouse_table", lambda *args, **kwargs: rows)
    monkeypatch.setattr(gr, "_catalogue_physical_identity", tracking_identity)

    loaded = gr.load_catalogue_profile_rows(framework_config(), "dev", selection, spark_session=None)

    assert len(loaded) == 2
    assert selection in calls
    assert rows[0] in calls
