"""Focused tests for the standalone catalogue enrichment browser."""

from __future__ import annotations

import inspect
import importlib
import types

import pytest

from fabricops_kit.widgets import shared
from fabricops_kit.widgets import widget_enrich_table_metadata
from tests.unit.test_guardrail_authoring_model import _install_fake_notebook_widgets


def _catalogue_rows():
    base = {"environment_name": "dev", "store_type": "lakehouse", "layer": "Governance Lakehouse", "schema_name": "dbo"}
    return [
        {**base, "metadata_table_key": "table-students", "metadata_column_key": "col-id", "schema_fingerprint": "fp-old", "table_name": "Students", "column_name": "student_id", "data_type": "long", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {**base, "metadata_table_key": "table-students", "metadata_column_key": "col-legacy", "schema_fingerprint": "fp-old", "table_name": "Students", "column_name": "legacy_code", "data_type": "string", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {**base, "metadata_table_key": "table-students", "metadata_column_key": "col-id", "schema_fingerprint": "fp-new", "table_name": "Students", "column_name": "student_id", "data_type": "bigint", "_committed_at": "2026-02-01", "_activity_id": "b"},
        {**base, "metadata_table_key": "table-students", "metadata_column_key": "col-name", "schema_fingerprint": "fp-new", "table_name": "Students", "column_name": "name", "data_type": "string", "_committed_at": "2026-02-01", "_activity_id": "b"},
        {**base, "layer": "Engineering Production", "schema_name": "curated", "metadata_table_key": "table-students-2", "metadata_column_key": "col-other", "schema_fingerprint": "fp-other", "table_name": "Students", "column_name": "student_id", "data_type": "long", "_committed_at": "2026-02-02", "_activity_id": "c"},
    ]


def test_catalogue_browser_uses_canonical_identity_and_complete_latest_fingerprint():
    """Canonical keys distinguish tables and latest membership uses the full fingerprint group."""
    options = shared.catalogue_table_options(_catalogue_rows())
    assert [row["metadata_table_key"] for row in options] == ["table-students-2", "table-students"]
    assert len({row["label"] for row in options}) == 2
    assert all("Students" in row["label"] for row in options)
    state = shared.catalogue_table_browser_state(_catalogue_rows(), "table-students", {})
    assert state["latest_schema_fingerprint"] == "fp-new"
    assert {row["metadata_column_key"] for row in state["latest_schema_rows"]} == {"col-id", "col-name"}
    assert {row["metadata_column_key"] for row in state["current_columns"]} == {"col-id", "col-name"}
    removed = state["removed_columns"]
    assert [(row["metadata_column_key"], row["data_type"], row["last_observed_at"]) for row in removed] == [("col-legacy", "string", "2026-01-01")]


def _build_widget(monkeypatch):
    module = importlib.import_module("fabricops_kit.widgets.widget_enrich_table_metadata")
    _install_fake_notebook_widgets(monkeypatch)
    reads = []
    writes = []
    existing = [
        {"enrichment_id": "1", "enrichment_level": "column", "metadata_key": "col-id", "enrichment_type": "Description", "value": "Identifier", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "2", "enrichment_level": "column", "metadata_key": "col-id", "enrichment_type": "Classification", "value": "retired-label", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "3", "enrichment_level": "column", "metadata_key": "col-legacy", "enrichment_type": "Description", "value": "Historical", "_committed_at": "2026-01-01", "_activity_id": "a"},
    ]
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda *a, **k: reads.append(1) or _catalogue_rows())
    monkeypatch.setattr(shared, "read_enrichment_records", lambda *a, **k: existing)
    monkeypatch.setattr(shared, "write_enrichment_records", lambda records, **kwargs: writes.append(records))
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kwargs: {name: "audit" for name in shared.STANDARD_RUNTIME_AUDIT_COLUMNS})
    config = types.SimpleNamespace(governance_config=types.SimpleNamespace(sensitivity_labels=["public"], pii_classifications=["none"]))
    widget = widget_enrich_table_metadata(spark_session=object(), context={"config": config, "env": "dev"})
    return widget, reads, writes


def _select(widget, token):
    if token != "table:table-students-2" and str(token).split(":", 1)[-1] != "col-other" and widget["table_selector"].value != "table-students":
        widget["table_selector"].value = "table-students"
        widget["table_selector"]._observer({"name": "value", "new": "table-students"})
    widget["column_selector"].value = token
    widget["column_selector"]._observer({"name": "value", "new": token})


def _change(control, value):
    control.value = value
    control._observer({"name": "value", "new": value})


def test_public_widget_is_standalone_and_table_and_column_editors_are_level_specific(monkeypatch):
    """The public signature needs no guardrail state and editors use canonical level keys."""
    signature = inspect.signature(widget_enrich_table_metadata)
    assert list(signature.parameters) == ["spark_session", "context"]
    widget, _, _ = _build_widget(monkeypatch)
    assert widget["column_selector"].value == "table:table-students-2"
    assert widget["controls"]["Personal_identifier"].layout.display == "none"
    _select(widget, "column:col-id")
    assert widget["controls"]["Description"].value == "Identifier"
    assert widget["controls"]["Classification"].value == "retired-label"
    assert "retired-label" in widget["controls"]["Classification"].options
    assert widget["controls"]["Personal_identifier"].layout.display == ""
    _change(widget["controls"]["Personal_identifier"], "none")
    records = widget["build_records"]()
    assert [(row["enrichment_level"], row["metadata_key"], row["enrichment_type"]) for row in records] == [("column", "col-id", "Personal_identifier")]
    _select(widget, "table:table-students")
    _change(widget["controls"]["Description"], "Student table")
    record = widget["build_records"]()[0]
    assert (record["enrichment_level"], record["metadata_key"]) == ("table", "table-students")
    assert "Personal_identifier" not in {row["enrichment_type"] for row in widget["build_records"]()}


def test_change_detection_drafts_removed_read_only_and_search_without_reads(monkeypatch):
    """Drafts survive selection changes, saves deduplicate, and removed columns cannot write."""
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
    assert len(reads) == 1
    assert list(widget["table_selector"].options) == [("Students — Engineering Production / curated", "table-students-2")]


def test_empty_description_is_not_written(monkeypatch):
    """Empty values are skipped rather than converted into tombstone rows."""
    widget, _, writes = _build_widget(monkeypatch)
    _select(widget, "column:col-name")
    _change(widget["controls"]["Description"], "   ")
    assert widget["save"]() == {"enrichment_records": []}
    assert writes == []
