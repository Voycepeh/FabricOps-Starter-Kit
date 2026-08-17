"""Tests for the scoped catalogue widget and its reader-facing views."""

from __future__ import annotations

from datetime import datetime
import importlib
import inspect
import sys
import types

import pytest

import fabricops_kit
from fabricops_kit.widgets.shared import _prepare_selected_guardrail_views, dataset_label

pytestmark = pytest.mark.unit


def test_public_catalogue_widget_is_the_only_catalogue_viewer():
    """The consolidated catalogue widget is exported from the package root."""
    assert callable(fabricops_kit.widget_view_catalogue)
    assert [name for name in fabricops_kit.__all__ if name.startswith("widget_view_")] == [
        "widget_view_catalogue",
    ]


def test_catalogue_widget_rejects_invalid_mode():
    """Mode selection is explicit and closed to the three supported values."""
    with pytest.raises(ValueError, match="mode must be one of"):
        fabricops_kit.widget_view_catalogue(mode="data")


@pytest.mark.parametrize("mode", ["pipeline", "agreement", "explore"])
def test_catalogue_widget_dispatches_only_scope_resolution(monkeypatch, mode):
    """Every supported mode hands allowed table IDs to one reader builder."""
    module = importlib.import_module("fabricops_kit.widgets.widget_view_catalogue")
    selected = {"pipeline": "pipeline-id", "agreement": "agreement-id", "explore": "explore-id"}[mode]
    inventory = [
        {"table_id": selected},
        {"table_id": "out-of-scope-id"},
    ]
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: (object(), "dev", {}))
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(module, "collect_catalogue_inventory", lambda *_args: inventory)
    scope = ({selected}, None, {"environment_name": "dev"}, {"Environment": "dev"})
    monkeypatch.setattr(module, "_resolve_pipeline_catalogue_scope", lambda **_kwargs: scope)
    monkeypatch.setattr(module, "_resolve_agreement_catalogue_scope", lambda **_kwargs: scope)
    monkeypatch.setattr(module, "_resolve_explore_catalogue_scope", lambda **_kwargs: scope)
    monkeypatch.setattr(module, "build_catalogue_widget", lambda **kwargs: kwargs)

    result = module.widget_view_catalogue(mode=mode, agreement={"agreement_id": "agreement"})

    assert result["inventory_rows"] == [{"table_id": selected}]
    assert result["role_options"] is None
    if mode == "agreement":
        assert result["display_context"]["Linked datasets"] == 1


def test_dataset_labels_are_consistent_and_pipeline_roles_are_explicit():
    """Shared labels stay readable when the normalized reader supplies its table ID fallback."""
    row = {"layer": "raw", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "key"}
    assert dataset_label(row) == "raw / sales / orders"
    assert dataset_label(row, "Source") == "[Source] raw / sales / orders"
    assert dataset_label(row, "Target") == "[Target] raw / sales / orders"


def test_guardrail_views_keep_stable_empty_schemas(spark_session):
    """A selected dataset without an execution returns two typed empty views."""
    results = spark_session.createDataFrame(
        [],
        "metadata_table_key string, run_id string, rule_type string, column_name string, status string, "
        "severity string, actual_value_json string, reason string, can_continue boolean, _committed_at timestamp",
    )
    row_results = spark_session.createDataFrame(
        [],
        "metadata_table_key string, run_id string, rule_type string, row_identity string, "
        "involved_columns_json string, failed_values_json string, failure_reason string",
    )

    views = _prepare_selected_guardrail_views(results, row_results, metadata_table_key="missing-key")

    assert views["guardrail_results"].count() == 0
    assert views["guardrail_results"].columns == [
        "rule_type",
        "columns",
        "status",
        "severity",
        "failed_rows",
        "failed_percent",
        "total_count",
        "reason",
        "can_continue",
        "run_id",
    ]
    assert views["guardrail_row_results"].count() == 0
    assert views["guardrail_row_results"].columns == [
        "rule_type",
        "row_identity",
        "involved_columns",
        "failed_values",
        "failure_reason",
        "run_id",
    ]


def test_widget_documents_normalized_five_view_contract():
    """The public widget documents readable views without changing persisted schemas."""
    source = inspect.getsource(fabricops_kit.widget_view_catalogue)
    assert "guardrail_row_results" in source
    assert "frequency rows are enriched with ``column_name``" in source
    assert "without\n    changing their persisted schemas" in source


def _run_pipeline_widget(monkeypatch, *, context=None):
    """Run the pipeline widget with lightweight normalized lineage fakes."""
    module = importlib.import_module("fabricops_kit.widgets.widget_view_catalogue")
    comparisons = []

    class Expression:
        def __init__(self, name):
            self.name = name

        def __eq__(self, value):
            comparisons.append((self.name, value))
            return self

        def __and__(self, _other):
            return self

    class Frame:
        def filter(self, _predicate):
            return self

        def select(self, *_columns):
            return self

        def distinct(self):
            return self

        def collect(self):
            return [{"pipeline_role": "Source", "table_id": "table-id"}]

    functions = types.ModuleType("pyspark.sql.functions")
    functions.col = Expression
    sql = types.ModuleType("pyspark.sql")
    sql.functions = functions
    pyspark = types.ModuleType("pyspark")
    pyspark.sql = sql
    monkeypatch.setitem(sys.modules, "pyspark", pyspark)
    monkeypatch.setitem(sys.modules, "pyspark.sql", sql)
    monkeypatch.setitem(sys.modules, "pyspark.sql.functions", functions)
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda *_args, **_kwargs: Frame())
    monkeypatch.setattr(module, "collect_catalogue_inventory", lambda *_args: [{"table_id": "table-id"}])
    monkeypatch.setattr(module, "build_catalogue_widget", lambda **kwargs: kwargs)
    explicit = {"config": object(), "env": "dev", **(context or {})}
    result = module.widget_view_catalogue(mode="pipeline", context=explicit)
    return result, comparisons


def test_pipeline_widget_resolves_current_fabric_identity(monkeypatch, fake_notebookutils):
    """Current Fabric keys resolve end to end and scope normalized lineage audit fields."""
    fake_notebookutils.runtime.context.clear()
    fake_notebookutils.runtime.context.update(
        currentNotebookId="live-notebook",
        currentNotebookName="Live Notebook",
        currentWorkspaceId="live-workspace",
        currentWorkspaceName="Live Workspace",
    )

    result, comparisons = _run_pipeline_widget(monkeypatch)

    assert result["selection_context"]["notebook_id"] == "live-notebook"
    assert result["selection_context"]["notebook_name"] == "Live Notebook"
    assert result["display_context"]["Notebook"] == "Live Notebook"
    assert ("_notebook_id", "live-notebook") in comparisons
    assert ("environment_name", "dev") in comparisons
    assert ("_workspace_id", "live-workspace") in comparisons


def test_pipeline_widget_resolves_fallback_fabric_identity(monkeypatch, fake_notebookutils):
    """Fallback Fabric keys resolve end to end when current keys are absent."""
    fake_notebookutils.runtime.context.clear()
    fake_notebookutils.runtime.context.update(
        notebookId="fallback-notebook",
        notebookName="Fallback Notebook",
        workspaceId="fallback-workspace",
        workspaceName="Fallback Workspace",
    )

    result, comparisons = _run_pipeline_widget(monkeypatch)

    assert result["selection_context"]["notebook_id"] == "fallback-notebook"
    assert result["selection_context"]["notebook_name"] == "Fallback Notebook"
    assert result["display_context"]["Notebook"] == "Fallback Notebook"
    assert ("_workspace_id", "fallback-workspace") in comparisons


def test_pipeline_widget_explicit_identity_wins_live_runtime(monkeypatch, fake_notebookutils):
    """Explicit canonical identity overrides conflicting live Fabric values."""
    fake_notebookutils.runtime.context.update(
        currentNotebookId="live-notebook",
        currentNotebookName="Live Notebook",
        currentWorkspaceId="live-workspace",
    )
    explicit = {
        "notebook_id": "explicit-notebook",
        "notebook_name": "Explicit Notebook",
        "workspace_id": "explicit-workspace",
    }

    result, comparisons = _run_pipeline_widget(monkeypatch, context=explicit)

    assert result["selection_context"]["notebook_id"] == "explicit-notebook"
    assert result["display_context"]["Notebook"] == "Explicit Notebook"
    assert ("_workspace_id", "explicit-workspace") in comparisons
    assert ("_notebook_id", "live-notebook") not in comparisons


def test_pipeline_widget_public_signature_and_missing_identity(monkeypatch, fake_notebookutils):
    """The widget adds no identity arguments and reports exhausted resolution."""
    signature = inspect.signature(fabricops_kit.widget_view_catalogue)
    assert list(signature.parameters) == ["mode", "agreement", "spark_session", "target", "schema", "context"]

    module = importlib.import_module("fabricops_kit.widgets.widget_view_catalogue")
    fake_notebookutils.runtime.context.clear()
    with pytest.raises(ValueError, match="active FabricOps context or Fabric runtime context"):
        module.widget_view_catalogue(mode="pipeline", context={"config": object(), "env": "dev"})


def test_catalogue_inventory_reads_table_level_normalized_rows(spark_session):
    """Inventory uses normalized table rows instead of rebuilding physical context from profile rows."""
    module = importlib.import_module("fabricops_kit.widgets.widget_view_catalogue")
    rows = [
        ("table", "table-id", None, "dev", "lakehouse", "raw", "sales", "orders", None),
        ("column", "table-id", "column-id", "dev", "lakehouse", "raw", "sales", "orders", "id"),
        ("table", "other-id", None, "prod", "lakehouse", "curated", "sales", "orders", None),
    ]
    catalogue = spark_session.createDataFrame(
        rows,
        "metadata_level string, table_id string, column_id string, environment_name string, store_type string, "
        "layer string, schema_name string, table_name string, column_name string",
    ).withColumn("last_profiled_at", __import__("pyspark.sql.functions", fromlist=["lit"]).lit(None).cast("timestamp"))

    inventory = module.collect_catalogue_inventory(catalogue, "dev")

    assert inventory == [
        {
            "table_id": "table-id",
            "environment_name": "dev",
            "store_type": "lakehouse",
            "layer": "raw",
            "schema_name": "sales",
            "table_name": "orders",
            "last_profiled_at": None,
        }
    ]


def test_catalogue_views_are_readable_and_frequency_joins_through_profile_id(monkeypatch, spark_session):
    """Reader shapes normalized catalogue/profile/frequency tables without changing their schemas."""
    module = importlib.import_module("fabricops_kit.widgets.widget_view_catalogue")
    from tests.unit.test_widget_register_data_contract import _FakeWidgets

    _FakeWidgets.Dropdown = _FakeWidgets.Select

    class FakeHTML(_FakeWidgets.HTML):
        def __init__(self, value="", **kwargs):
            super().__init__(value=value, **kwargs)

    _FakeWidgets.HTML = FakeHTML
    displayed = []
    fake_display = types.ModuleType("IPython.display")
    fake_display.display = displayed.append
    fake_ipython = types.ModuleType("IPython")
    fake_ipython.display = fake_display
    monkeypatch.setitem(sys.modules, "IPython", fake_ipython)
    monkeypatch.setitem(sys.modules, "IPython.display", fake_display)
    monkeypatch.setattr(module, "require_ipywidgets", lambda: _FakeWidgets)

    old_snapshot = datetime(2026, 7, 30)
    latest_snapshot = datetime(2026, 7, 31)
    later_snapshot = datetime(2026, 8, 1)
    catalogue_schema = (
        "metadata_level string, table_id string, column_id string, environment_name string, store_type string, "
        "layer string, schema_name string, table_name string, column_name string, first_profiled_at timestamp, "
        "last_profiled_at timestamp, is_active boolean, _committed_at timestamp"
    )
    profile_schema = (
        "profile_id string, profile_snapshot_id string, table_id string, column_id string, environment_name string, "
        "data_type string, row_count long, non_null_count long, null_count long, null_percent double, "
        "distinct_count long, distinct_percent double, mean_value double, stddev_value double, min_value string, "
        "percentile_25_value double, median_value double, percentile_75_value double, max_value string, "
        "profiled_at timestamp, _committed_at timestamp"
    )
    frequency_schema = (
        "frequency_id string, profile_id string, profile_snapshot_id string, value string, frequency_count long, "
        "frequency_percent double, frequency_rank integer, profiled_row_count long, profiled_non_null_count long, "
        "profiled_at timestamp, _committed_at timestamp"
    )
    tables = {
        "METADATA_DATA_CATALOGUE": spark_session.createDataFrame(
            [
                ("table", "dataset-key", None, "dev", "lakehouse", "raw", "sales", "orders", None, old_snapshot, latest_snapshot, True, latest_snapshot),
                ("column", "dataset-key", "column-country", "dev", "lakehouse", "raw", "sales", "orders", "Country", old_snapshot, latest_snapshot, True, latest_snapshot),
                ("column", "dataset-key", "column-comment", "dev", "lakehouse", "raw", "sales", "orders", "Comment", old_snapshot, latest_snapshot, True, latest_snapshot),
                ("table", "unprofiled-key", None, "dev", "lakehouse", "curated", "sales", "customers", None, latest_snapshot, latest_snapshot, True, latest_snapshot),
                ("column", "unprofiled-key", "column-customer", "dev", "lakehouse", "curated", "sales", "customers", "customer_id", latest_snapshot, latest_snapshot, True, latest_snapshot),
            ],
            catalogue_schema,
        ),
        "METADATA_DATA_PROFILED": spark_session.createDataFrame(
            [
                ("old-country", "snapshot-old", "dataset-key", "column-country", "dev", "string", 4, 4, 0, 0.0, 2, 50.0, None, None, "DE", None, None, None, "SG", old_snapshot, old_snapshot),
                ("profile-country", "snapshot-latest", "dataset-key", "column-country", "dev", "string", 5, 5, 0, 0.0, 2, 40.0, None, None, "DE", None, None, None, "SG", latest_snapshot, latest_snapshot),
                ("profile-comment", "snapshot-latest", "dataset-key", "column-comment", "dev", "string", 5, 4, 1, 20.0, 4, 80.0, None, None, "a", None, None, None, "z", latest_snapshot, latest_snapshot),
            ],
            profile_schema,
        ),
        "METADATA_DATA_PROFILED_FREQUENCY": spark_session.createDataFrame(
            [
                ("freq-old", "old-country", "snapshot-old", "old", 1, 25.0, 1, 4, 4, old_snapshot, old_snapshot),
                ("freq-null", "profile-country", "snapshot-latest", None, 2, 40.0, 1, 5, 5, latest_snapshot, latest_snapshot),
                ("freq-current", "profile-country", "snapshot-latest", "current", 3, 60.0, 2, 5, 5, latest_snapshot, latest_snapshot),
                ("freq-future", "profile-country", "snapshot-future", "future", 4, 80.0, 1, 5, 5, later_snapshot, later_snapshot),
            ],
            frequency_schema,
        ),
        "METADATA_GUARDRAIL_RESULTS": spark_session.createDataFrame(
            [
                ("dataset-key", "old-run", "not_null", "Country", "failed", "error", False, "old", '{"failed_count":1,"failed_percent":25.0,"total_count":4}', old_snapshot),
                ("dataset-key", "latest-run", "not_null", "Country", "passed", "error", True, "Rule passed.", '{"failed_count":0,"failed_percent":0.0,"total_count":5}', latest_snapshot),
                ("unprofiled-key", "customer-run", "not_null", "customer_id", "passed", "error", True, "Rule passed.", '{"failed_count":0,"failed_percent":0.0,"total_count":2}', later_snapshot),
            ],
            "metadata_table_key string, run_id string, rule_type string, column_name string, status string, severity string, "
            "can_continue boolean, reason string, actual_value_json string, _committed_at timestamp",
        ),
        "METADATA_GUARDRAIL_ROW_RESULTS": spark_session.createDataFrame(
            [],
            "metadata_table_key string, run_id string, rule_type string, row_identity string, involved_columns_json string, "
            "failed_values_json string, failure_reason string",
        ),
    }
    read_calls = []

    def read_table(table, **_kwargs):
        read_calls.append(table)
        return tables[table]

    monkeypatch.setattr(module, "read_lakehouse_table_core", read_table)
    state = module.build_catalogue_widget(
        title="Pipeline Catalogue Viewer",
        description="View data catalogues used by the current pipeline notebook",
        selection_context={"notebook_id": "technical-id", "environment_name": "dev"},
        display_context={"Notebook": "Customer <pipeline>", "Environment": "dev", "Linked datasets": 1},
        inventory_rows=[
            {"table_id": "dataset-key", "environment_name": "dev", "store_type": "lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders", "last_profiled_at": latest_snapshot},
            {"table_id": "unprofiled-key", "environment_name": "dev", "store_type": "lakehouse", "layer": "curated", "schema_name": "sales", "table_name": "customers", "last_profiled_at": latest_snapshot},
        ],
        role_options=None,
        target="metadata",
        schema=None,
        spark_session=object(),
        runtime_context={},
        empty_message="No inventory.",
    )

    page = displayed[0]
    visible_html = page.children[1].children[1].value
    assert "<b>Notebook:</b> Customer &lt;pipeline&gt;" in visible_html
    assert "technical-id" not in visible_html
    selection = state["get_selection"]()
    assert selection["table_id"] == "dataset-key"
    assert selection["profile_snapshot_id"] is None
    assert selection["profile_id"] is None
    assert read_calls == []

    views = state["get_views"]()
    assert read_calls == [
        "METADATA_DATA_CATALOGUE",
        "METADATA_DATA_PROFILED",
        "METADATA_DATA_PROFILED_FREQUENCY",
        "METADATA_GUARDRAIL_RESULTS",
        "METADATA_GUARDRAIL_ROW_RESULTS",
    ]
    selection = state["get_selection"]()
    assert selection["profile_snapshot_id"] == "snapshot-latest"
    assert selection["profiled_at"] == latest_snapshot
    assert selection["profile_id"] == "profile-country"
    assert set(views) == {"catalogue", "profile", "frequency", "guardrail_results", "guardrail_row_results"}
    assert views["catalogue"].columns == [
        "metadata_level", "table_name", "column_name", "store_type", "layer", "schema_name",
        "first_profiled_at", "last_profiled_at", "is_active", "table_id", "column_id",
    ]
    assert views["profile"].columns[:6] == [
        "column_name", "data_type", "row_count", "non_null_count", "null_count", "null_percent",
    ]
    assert views["profile"].columns[-4:] == ["profile_id", "profile_snapshot_id", "column_id", "table_id"]
    assert {row.column_name for row in views["profile"].collect()} == {"Country", "Comment"}
    assert views["frequency"].columns == [
        "column_name", "value", "frequency_count", "frequency_percent", "frequency_rank",
        "profiled_row_count", "profiled_non_null_count", "profiled_at", "frequency_id", "profile_id",
        "profile_snapshot_id",
    ]
    frequency_rows = views["frequency"].collect()
    assert {row.column_name for row in frequency_rows} == {"Country"}
    assert {row.profile_id for row in frequency_rows} == {"profile-country"}
    assert {row.value for row in frequency_rows} == {None, "current"}
    assert {row.run_id for row in views["guardrail_results"].collect()} == {"latest-run"}

    state["_controls"]["profile_id"].value = "profile-comment"
    assert state["get_selection"]()["profile_id"] == "profile-comment"
    assert state["get_views"]()["frequency"].count() == 0
    assert len(read_calls) == 5

    state["_controls"]["search"].value = "does not exist"
    assert state["_controls"]["dataset"].value is None
    state["_controls"]["search"].value = ""
    assert state["_controls"]["dataset"].value == "\x1fdataset-key"

    state["_controls"]["dataset"].value = "\x1funprofiled-key"
    unprofiled = state["get_views"]()
    assert state["get_selection"]()["profile_snapshot_id"] is None
    assert unprofiled["profile"].count() == 0
    assert unprofiled["frequency"].count() == 0
    assert {row.run_id for row in unprofiled["guardrail_results"].collect()} == {"customer-run"}
