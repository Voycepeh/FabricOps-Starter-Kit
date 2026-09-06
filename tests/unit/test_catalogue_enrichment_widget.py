"""Focused tests for the standalone catalogue enrichment browser."""

from __future__ import annotations

import importlib
import inspect
import types

from fabricops_kit.widgets import enrichment_shared
from fabricops_kit.widgets import widget_enrich_table_metadata
from tests.unit.test_widget_author_guardrails import _install_fake_notebook_widgets


def _catalogue_rows():
    base = {
        "environment_name": "dev",
        "store_type": "lakehouse",
        "layer": "Governance Lakehouse",
        "schema_name": "dbo",
        "first_profiled_at": "2026-01-01",
        "last_profiled_at": "2026-02-01",
        "is_active": True,
        "_activity_id": "a",
    }
    return [
        {**base, "metadata_level": "table", "table_id": "table-students", "column_id": "", "table_name": "Students", "column_name": ""},
        {**base, "metadata_level": "column", "table_id": "table-students", "column_id": "col-id", "table_name": "Students", "column_name": "student_id"},
        {**base, "metadata_level": "column", "table_id": "table-students", "column_id": "col-name", "table_name": "Students", "column_name": "name"},
        {**base, "metadata_level": "column", "table_id": "table-students", "column_id": "col-legacy", "table_name": "Students", "column_name": "legacy_code", "last_profiled_at": "2026-01-01", "is_active": False},
        {**base, "metadata_level": "table", "table_id": "table-courses", "column_id": "", "table_name": "Courses", "layer": "Engineering Production", "schema_name": "curated"},
        {**base, "metadata_level": "column", "table_id": "table-courses", "column_id": "col-course", "table_name": "Courses", "column_name": "course_id", "layer": "Engineering Production", "schema_name": "curated"},
        {**base, "environment_name": "prod", "metadata_level": "table", "table_id": "table-students", "column_id": "", "table_name": "Students", "layer": "Engineering Production"},
        {**base, "environment_name": "prod", "metadata_level": "column", "table_id": "table-students", "column_id": "col-prod-only", "table_name": "Students", "column_name": "production_only", "layer": "Engineering Production"},
    ]


def _existing_enrichment():
    rows = [
        {"enrichment_id": "1", "table_id": "table-students", "column_id": "col-id", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "Description", "value": "Identifier", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "2", "table_id": "table-students", "column_id": "col-id", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "Classification", "value": "retired-label", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "3", "table_id": "table-students", "column_id": "col-legacy", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "Description", "value": "Historical", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "4", "table_id": "table-students", "column_id": "col-name", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "Description", "value": "Student name", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "5", "table_id": "table-students", "column_id": "col-name", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "Classification", "value": "public", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "6", "table_id": "table-students", "column_id": "col-name", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "Personal_identifier", "value": "none", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "7", "table_id": "table-students", "column_id": "col-id", "environment_name": "prod", "enrichment_level": "column", "enrichment_type": "Description", "value": "Production identifier", "_committed_at": "2026-03-01", "_activity_id": "z"},
    ]
    for row in rows:
        row["contract_id"] = "contract-students"
        row["contract_version"] = 1
        row.pop("table_id", None)
    return rows


def test_catalogue_browser_uses_stage2_ids_and_environment_isolation():
    """Table and column selection is scoped by environment while stable IDs remain shared."""
    options = enrichment_shared.catalogue_table_options(_catalogue_rows(), environment_name="dev")
    assert {row["table_id"] for row in options} == {"table-students", "table-courses"}
    current_values = enrichment_shared.latest_enrichment_values(_existing_enrichment(), environment_name="dev")
    state = enrichment_shared.catalogue_table_browser_state(
        _catalogue_rows(),
        "table-students",
        environment_name="dev",
        contract_id="contract-students",
        contract_version=1,
        current_values=current_values,
    )
    assert {row["column_id"] for row in state["current_columns"]} == {"col-id", "col-name"}
    assert [row["column_id"] for row in state["removed_columns"]] == ["col-legacy"]
    assert "col-prod-only" not in {row["column_id"] for row in state["all_historical_columns"]}
    assert next(row for row in state["current_columns"] if row["column_id"] == "col-id")["enrichment_values"]["Description"] == "Identifier"


def _build_widget(monkeypatch, *, auto_observe=False):
    module = importlib.import_module("fabricops_kit.widgets.widget_enrich_table_metadata")
    _install_fake_notebook_widgets(monkeypatch, auto_observe=auto_observe)
    reads = []
    writes = []
    contracts = [
        {"contract_id": "contract-students", "contract_version": 1, "table_id": "table-students", "status": "draft"},
        {"contract_id": "contract-courses", "contract_version": 1, "table_id": "table-courses", "status": "draft"},
    ]
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda table, *a, **k: reads.append(1) or (contracts if table == "METADATA_DATA_CONTRACT" else _catalogue_rows()))
    monkeypatch.setattr(enrichment_shared, "read_enrichment_records", lambda *a, **k: reads.append(1) or _existing_enrichment())
    monkeypatch.setattr(enrichment_shared, "write_enrichment_records", lambda records, **kwargs: writes.append(records))
    monkeypatch.setattr(
        enrichment_shared,
        "build_runtime_audit_fields",
        lambda **kwargs: {
            "_committed_by": "audit",
            "_committed_at": "2026-01-01T00:00:00",
            "_workspace_id": "audit",
            "_workspace_name": "audit",
            "_notebook_id": "audit",
            "_notebook_name": "audit",
            "_metadata_lakehouse_name": "audit",
            "_activity_id": "audit",
        },
    )
    config = types.SimpleNamespace(
        governance_config=types.SimpleNamespace(sensitivity_labels=["public"], pii_classifications=["none"])
    )
    widget = widget_enrich_table_metadata(spark_session=object(), context={"config": config, "env": "dev"})
    return widget, reads, writes


def _select(widget, token):
    if token != "table:table-courses" and str(token).split(":", 1)[-1] != "col-course" and widget["table_selector"].value != "table-students":
        widget["table_selector"].value = "table-students"
        widget["table_selector"]._observer({"name": "value", "new": "table-students"})
    widget["column_selector"].value = token
    widget["column_selector"]._observer({"name": "value", "new": token})


def _change(control, value):
    control.value = value
    control._observer({"name": "value", "new": value})


def test_public_widget_is_standalone_and_writes_stage3_identity(monkeypatch):
    """The public widget writes table/column IDs plus the current environment."""
    signature = inspect.signature(widget_enrich_table_metadata)
    assert list(signature.parameters) == ["spark_session", "context"]
    widget, reads, _ = _build_widget(monkeypatch)
    assert widget["spark_read_count"] == 3
    assert len(reads) == 3
    _select(widget, "column:col-id")
    assert widget["controls"]["Description"].value == "Identifier"
    assert widget["controls"]["Classification"].value == "retired-label"
    assert "retired-label" in widget["controls"]["Classification"].options
    assert widget["controls"]["Personal_identifier"].layout.display == ""
    _change(widget["controls"]["Personal_identifier"], "none")
    records = widget["build_records"]()
    assert [(row["enrichment_level"], row["contract_id"], row["contract_version"], row["column_id"], row["environment_name"], row["enrichment_type"]) for row in records] == [
        ("column", "contract-students", 1, "col-id", "dev", "Personal_identifier")
    ]
    assert "metadata_key" not in records[0]
    _select(widget, "table:table-students")
    _change(widget["controls"]["Description"], "Student table")
    record = widget["build_records"]()[0]
    assert (record["enrichment_level"], record["contract_id"], record["contract_version"], record["column_id"], record["environment_name"]) == (
        "table", "contract-students", 1, "", "dev"
    )
    assert "Personal_identifier" not in {row["enrichment_type"] for row in widget["build_records"]()}


def test_change_detection_drafts_inactive_read_only_and_search_without_reads(monkeypatch):
    """Drafts survive selection changes, saves deduplicate, and inactive columns cannot write."""
    widget, reads, writes = _build_widget(monkeypatch)
    _select(widget, "column:col-id")
    _change(widget["controls"]["Description"], "Draft identifier")
    _select(widget, "column:col-name")
    _select(widget, "column:col-id")
    assert widget["controls"]["Description"].value == "Draft identifier"
    first = widget["save"]()
    second = widget["save"]()
    assert len(first["enrichment_records"]) == 1
    assert second == {"enrichment_records": []}
    assert len(writes) == 1
    _select(widget, "column:col-legacy")
    assert all(control.disabled for control in widget["controls"].values())
    assert widget["save_button"].disabled is True
    assert widget["controls"]["Description"].value == "Historical"
    assert widget["build_records"]() == []
    widget["table_search"].value = "engineering"
    widget["table_search"]._observer({"name": "value", "new": "engineering"})
    assert len(reads) == 3
    assert list(widget["table_selector"].options) == [("Courses — Engineering Production / curated", "table-courses")]


def test_selection_hydration_does_not_create_or_cross_contaminate_drafts(monkeypatch):
    """Realistic value observers stay suspended while a new detail is hydrated."""
    widget, _, _ = _build_widget(monkeypatch, auto_observe=True)
    widget["table_selector"].value = "table-students"
    widget["column_selector"].value = "column:col-id"
    assert widget["controls"]["Description"].value == "Identifier"
    assert widget["controls"]["Classification"].value == "retired-label"
    assert widget["drafts"] == {}

    widget["column_selector"].value = "column:col-name"
    assert widget["controls"]["Description"].value == "Student name"
    assert widget["controls"]["Classification"].value == "public"
    assert widget["controls"]["Personal_identifier"].value == "none"
    assert widget["drafts"] == {}
    widget["column_selector"].value = "column:col-id"
    assert widget["controls"]["Description"].value == "Identifier"
    assert widget["controls"]["Classification"].value == "retired-label"
    assert widget["drafts"] == {}


def test_empty_description_is_not_written(monkeypatch):
    """Empty values are skipped rather than converted into tombstone rows."""
    widget, _, writes = _build_widget(monkeypatch)
    _select(widget, "column:col-name")
    _change(widget["controls"]["Description"], "   ")
    assert widget["save"]() == {"enrichment_records": []}
    assert writes == []
