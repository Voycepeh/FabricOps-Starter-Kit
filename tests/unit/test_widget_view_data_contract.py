"""Tests for data-contract view selection helpers."""

from __future__ import annotations

import pytest
from datetime import datetime
import json

import fabricops_kit
from fabricops_kit.widgets import widget_view_data_contract as public_widget
from fabricops_kit.widgets.widget_view_data_contract import (
    _agreement_id_from_context,
    _normalize_metadata_ids,
    _options,
)
from fabricops_kit.widgets.shared import (
    export_dataframe_to_files,
    format_full_value,
    get_data_contract_views,
    get_current_notebook_lineage_scope,
    render_expandable_dataframe,
)

pytestmark = pytest.mark.unit


ROWS = [
    {"store_type": "lakehouse", "layer": "curated", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "one"},
    {"store_type": "lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "two"},
    {"store_type": "warehouse", "layer": "curated", "schema_name": "dbo", "table_name": "orders", "metadata_table_key": "three"},
]


def test_dependent_options_follow_canonical_location_hierarchy():
    """Each hierarchy choice constrains the next selector."""
    assert _options(ROWS, "layer", {"store_type": "lakehouse"}) == ["curated", "raw"]
    assert _options(ROWS, "schema_name", {"store_type": "warehouse", "layer": "curated"}) == ["dbo"]


def test_duplicate_table_names_resolve_exact_metadata_identity():
    """A table name alone never determines the registered dataset."""
    assert _options(ROWS, "metadata_table_key", {"store_type": "lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders"}) == ["two"]
    assert len(_options(ROWS, "metadata_table_key", {"table_name": "orders"})) == 3


def test_widget_is_publicly_importable_and_old_export_is_removed():
    """Only the intentional Preview rename is exported."""
    assert fabricops_kit.widget_view_data_contract is public_widget
    assert "widget_browse_metadata_catalogue" not in fabricops_kit.__all__
    with pytest.raises(AttributeError):
        getattr(fabricops_kit, "widget_browse_metadata_catalogue")


def test_agreement_context_resolves_records_and_widget_state():
    """Agreement records and agreement-widget selections resolve the same ID."""
    assert _agreement_id_from_context({"agreement_id": "agreement-1"}) == "agreement-1"

    class Selected:
        value = "agreement-2"

    state = {
        "existing_record": Selected(),
        "existing_records_by_id": {"agreement-2": {"agreement_id": "agreement-2"}},
    }
    assert _agreement_id_from_context(state) == "agreement-2"
    assert _agreement_id_from_context(None) == ""


def test_restricted_metadata_ids_preserve_roles_order_and_unique_identity():
    """Pipeline labels remain readable while canonical IDs remain the values."""
    assert _normalize_metadata_ids({"Source": "source-id", "Target": "target-id"}) == [
        ("Source", "source-id"),
        ("Target", "target-id"),
    ]
    assert _normalize_metadata_ids(["source-id", "target-id", "source-id", ""]) == [
        ("Dataset 1", "source-id"),
        ("Dataset 2", "target-id"),
    ]
    with pytest.raises(TypeError, match="mapping"):
        _normalize_metadata_ids("source-id")
    with pytest.raises(ValueError, match="pipeline_scope"):
        public_widget(pipeline_scope="all_notebooks")
    with pytest.raises(ValueError, match="either pipeline_scope or metadata_ids"):
        public_widget(pipeline_scope="current_notebook", metadata_ids=["source-id"])


def test_missing_optional_widgets_returns_clear_non_breaking_state(monkeypatch, capsys):
    """Role notebooks remain executable when the optional widget extra is absent."""
    import importlib

    module = importlib.import_module("fabricops_kit.widgets.widget_view_data_contract")
    monkeypatch.setattr(
        module,
        "require_ipywidgets",
        lambda: (_ for _ in ()).throw(ModuleNotFoundError("Install the widget extra.")),
    )
    state = public_widget(
        metadata_id="dataset-1", metadata_ids={"Target": "dataset-1"},
        schema_version="schema-2",
    )

    assert state["metadata_table_key"] == "dataset-1"
    assert state["schema_fingerprint"] == "schema-2"
    assert state["selection_mode"] == "restricted"
    assert state["allowed_metadata_ids"] == ["dataset-1"]
    assert "Install the widget extra" in state["error"]
    assert "Data contract viewer unavailable" in capsys.readouterr().out


def test_full_value_formatter_pretty_prints_json_and_preserves_invalid_text():
    """JSON detail is readable while malformed JSON remains inspectable."""
    assert format_full_value('{"values":["Active","Completed"]}') == (  # noqa: S105
        '{\n  "values": [\n    "Active",\n    "Completed"\n  ]\n}'
    )
    assert format_full_value("{invalid json") == "{invalid json"
    assert format_full_value(None) == ""


def test_expandable_viewer_collects_only_bounded_rows_and_retains_full_values(spark_session):
    """The compact preview truncates display only and reports bounded history."""
    pytest.importorskip("ipywidgets")
    long_json = '{"description":"' + ("x" * 100) + '"}'
    dataframe = spark_session.createDataFrame(
        [(1, long_json), (2, '{"status":"ok"}'), (3, "plain text")],
        "record_id int, payload string",
    ).orderBy("record_id")

    viewer = render_expandable_dataframe(
        dataframe, title="History", max_rows=2,
        preview_columns=["record_id", "payload"], expanded_columns=["payload"],
    )

    assert viewer["limited"] is True
    assert len(viewer["rows"]) == 2
    assert viewer["rows"][0]["payload"] == long_json
    assert "additional records are not loaded" in viewer["status"].value
    assert "…" in viewer["preview"].value
    assert viewer["field_selector"].options[0] == "payload"


def test_dataframe_download_writes_complete_source_with_configured_path(monkeypatch):
    """Exports write the source DataFrame rather than the bounded preview rows."""
    calls = []

    class Writer:
        def mode(self, value):
            calls.append(("mode", value))
            return self

        def option(self, key, value):
            calls.append(("option", key, value))
            return self

        def csv(self, path):
            calls.append(("csv", path))

    class DataFrame:
        write = Writer()

        def limit(self, _count):
            raise AssertionError("downloads must not inherit the preview limit")

    monkeypatch.setattr(
        "fabricops_kit.widgets.shared.resolve_configured_file_path",
        lambda target, relative_path, context: (object(), relative_path, f"abfss://metadata/Files/{relative_path}"),
    )

    exported = export_dataframe_to_files(
        DataFrame(), filename="data contract/id", file_format="csv",
        target="metadata", context={"env": "dev"},
    )

    assert exported["export_name"] == "data-contract-id"
    assert exported["relative_path"].startswith("Files/fabricops_exports/")
    assert exported["relative_path"].endswith("/data-contract-id/csv")
    assert calls[:2] == [("mode", "overwrite"), ("option", "header", True)]
    assert calls[2][0] == "csv"


def test_contract_assembly_preserves_rules_history_and_separate_views(monkeypatch, spark_session):
    """The assembly helper keeps contract grain and every related evidence surface."""
    old = datetime(2026, 1, 1)
    new = datetime(2026, 2, 1)
    tables = {
        "METADATA_DATA_CATALOGUE": spark_session.createDataFrame(
            [
                ("dataset", "c1", "schema-1", "dev", "lakehouse", "raw", "sales", "orders", "id", "long", old),
                ("dataset", "c2", "schema-1", "dev", "lakehouse", "raw", "sales", "orders", "status", "string", old),
                ("dataset", "c1", "schema-2", "dev", "lakehouse", "raw", "sales", "orders", "id", "long", new),
            ],
            "metadata_table_key string, metadata_column_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, column_name string, data_type string, _committed_at timestamp",
        ),
        "METADATA_ENRICHMENT": spark_session.createDataFrame(
            [("dataset", "c1", "Identifier", new, "orders", "id")],
            "metadata_table_key string, metadata_column_key string, business_meaning string, _committed_at timestamp, table_name string, column_name string",
        ),
        "METADATA_GUARDRAIL": spark_session.createDataFrame(
            [
                ("dataset", "c1", "rule-not-null", "g1", "r1", "not_null", "error", True, "active", old, "orders", "id"),
                ("dataset", "c1", "rule-unique", "g2", "r2", "unique", "warning", True, "active", new, "orders", "id"),
                ("dataset", "c1", "rule-retired", "g3", "r3", "between", "warning", False, "inactive", new, "orders", "id"),
            ],
            "metadata_table_key string, metadata_column_key string, rule_key string, guardrail_rule_id string, rule_id string, rule_type string, severity string, is_active boolean, activation_state string, _committed_at timestamp, table_name string, column_name string",
        ),
        "METADATA_DATA_PROFILED": spark_session.createDataFrame(
            [("dataset", "c1", "schema-1", "id", old, old), ("dataset", "c1", "schema-2", "id", new, new)],
            "metadata_table_key string, metadata_column_key string, schema_fingerprint string, column_name string, profiled_at timestamp, _committed_at timestamp",
        ),
        "METADATA_GUARDRAIL_RESULTS": spark_session.createDataFrame(
            [("dataset", "old", old), ("dataset", "new", new)],
            "metadata_table_key string, result_id string, _committed_at timestamp",
        ),
        "METADATA_DATA_ACCESS": spark_session.createDataFrame(
            [("dataset", "reader", old, None, old)],
            "metadata_table_key string, user_principal string, approved_at timestamp, expires_at timestamp, _committed_at timestamp",
        ),
    }
    monkeypatch.setattr(
        "fabricops_kit.widgets.shared.read_lakehouse_table_core",
        lambda name, **_kwargs: tables[name],
    )

    latest = get_data_contract_views("dataset", spark_session=spark_session)
    assert latest["summary"].first().schema_fingerprint == "schema-2"

    historical = get_data_contract_views(
        "dataset", schema_fingerprint="schema-1", spark_session=spark_session,
    )
    contract_rows = {row.column_name: row for row in historical["current_contract"].collect()}
    assert set(contract_rows) == {"id", "status"}
    assert contract_rows["id"].enrichment_business_meaning == "Identifier"
    assert contract_rows["status"].enrichment_business_meaning is None
    rules = json.loads(contract_rows["id"].guardrail_rules_json)
    assert {rule["rule_type"] for rule in rules} == {"not_null", "unique"}
    assert json.loads(contract_rows["status"].guardrail_rules_json) == []
    assert "not schema-versioned" in contract_rows["id"].governance_metadata_scope
    assert [row.schema_fingerprint for row in historical["data_profiled"].collect()] == ["schema-2", "schema-1"]
    assert [row.result_id for row in historical["guardrail_results"].collect()] == ["new", "old"]
    assert historical["data_access"].first().user_principal == "reader"

    for name in ("METADATA_ENRICHMENT", "METADATA_GUARDRAIL", "METADATA_GUARDRAIL_RESULTS", "METADATA_DATA_ACCESS"):
        tables[name] = tables[name].limit(0)
    without_related = get_data_contract_views(
        "dataset", schema_fingerprint="schema-1", spark_session=spark_session,
    )
    empty_related_rows = {row.column_name: row for row in without_related["current_contract"].collect()}
    assert empty_related_rows["id"].enrichment_business_meaning is None
    assert json.loads(empty_related_rows["id"].guardrail_rules_json) == []
    assert without_related["guardrail_results"].count() == 0
    assert without_related["data_access"].count() == 0


def test_current_notebook_scope_uses_historical_unique_lineage_roles(monkeypatch, spark_session):
    """Pipeline scope combines roles and excludes other notebook identities."""
    old = datetime(2026, 1, 1)
    new = datetime(2026, 2, 1)
    lineage = spark_session.createDataFrame(
        [
            ("dev", "workspace-1", "notebook-1", "customers", "source", old),
            ("dev", "workspace-1", "notebook-1", "customers", "target", new),
            ("dev", "workspace-1", "notebook-1", "summary", "target", new),
            ("dev", "workspace-1", "notebook-2", "other-notebook", "source", new),
            ("dev", "workspace-2", "notebook-1", "other-workspace", "source", new),
            ("prod", "workspace-1", "notebook-1", "other-environment", "source", new),
        ],
        "environment_name string, workspace_id string, notebook_id string, metadata_table_key string, profile_role string, profiled_at timestamp",
    )
    monkeypatch.setattr(
        "fabricops_kit.widgets.shared.read_lakehouse_table_core",
        lambda name, **_kwargs: lineage if name == "METADATA_DATA_LINEAGE" else None,
    )

    scope = get_current_notebook_lineage_scope(
        spark_session=spark_session,
        context={
            "config": object(), "env": "dev",
            "runtime_metadata": {"workspace_id": "workspace-1", "notebook_id": "notebook-1"},
        },
    )

    assert scope == [("Source / Target", "customers"), ("Target", "summary")]
    with pytest.raises(ValueError, match="workspace and notebook IDs"):
        get_current_notebook_lineage_scope(context={"config": object(), "env": "dev"})
