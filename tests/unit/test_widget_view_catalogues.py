"""Tests for the scoped catalogue widgets and their shared contract."""

from __future__ import annotations

from datetime import datetime
import importlib
import inspect
import sys
import types

import pytest

import fabricops_kit
from fabricops_kit.widgets.shared import (
    _prepare_selected_guardrail_views,
    build_catalogue_widget,
    dataset_label,
    schema_version_options,
)

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
    """Every supported mode hands allowed keys to one shared widget builder."""
    module = importlib.import_module("fabricops_kit.widgets.widget_view_catalogue")
    selected = {"pipeline": "pipeline-key", "agreement": "agreement-key", "explore": "explore-key"}[mode]
    inventory = [
        {"metadata_table_key": selected},
        {"metadata_table_key": "out-of-scope-key"},
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

    assert result["inventory_rows"] == [{"metadata_table_key": selected}]
    assert result["role_options"] is None


def test_dataset_labels_are_consistent_and_pipeline_roles_are_explicit():
    """Shared labels are consistent and make lineage roles explicit."""
    row = {"layer": "raw", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "key"}
    assert dataset_label(row) == "raw / sales / orders"
    assert dataset_label(row, "Source") == "[Source] raw / sales / orders"
    assert dataset_label(row, "Target") == "[Target] raw / sales / orders"


def test_schema_versions_are_deduplicated_and_latest_is_deterministic():
    """Schema choices deduplicate column observations and choose the latest."""
    rows = [
        {"metadata_table_key": "key", "schema_fingerprint": "old", "_committed_at": datetime(2026, 1, 1)},
        {"metadata_table_key": "key", "schema_fingerprint": "new", "_committed_at": datetime(2026, 2, 1)},
        {"metadata_table_key": "key", "schema_fingerprint": "new", "_committed_at": datetime(2026, 2, 1)},
    ]
    options = schema_version_options(rows, "key")
    assert [value for _label, value in options] == ["new", "old"]
    assert options[0][0].startswith("Latest")


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


def test_widget_documents_common_five_view_contract():
    """The public owner documents the normalized common view contract."""
    source = inspect.getsource(fabricops_kit.widget_view_catalogue)
    assert "display(catalogue" not in source
    assert "guardrail_row_results" in source
    assert "All modes then use one shared selector" in source


def _run_pipeline_widget(monkeypatch, *, context=None):
    """Run the pipeline widget with lightweight lineage and rendering fakes."""
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
            return [{"profile_role": "Source", "metadata_table_key": "table-key"}]

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
    monkeypatch.setattr(
        module,
        "collect_catalogue_inventory",
        lambda *_args: [{"metadata_table_key": "table-key"}],
    )
    monkeypatch.setattr(module, "build_catalogue_widget", lambda **kwargs: kwargs)
    explicit = {"config": object(), "env": "dev", **(context or {})}
    result = module.widget_view_catalogue(mode="pipeline", context=explicit)
    return result, comparisons


def test_pipeline_widget_resolves_current_fabric_identity(monkeypatch, fake_notebookutils):
    """Current Fabric keys resolve end to end and scope workspace lineage."""
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
    assert ("notebook_id", "live-notebook") in comparisons
    assert ("environment_name", "dev") in comparisons
    assert ("workspace_id", "live-workspace") in comparisons


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
    assert ("workspace_id", "fallback-workspace") in comparisons


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
    assert ("workspace_id", "explicit-workspace") in comparisons
    assert ("notebook_id", "live-notebook") not in comparisons


def test_pipeline_widget_public_signature_and_missing_identity(monkeypatch, fake_notebookutils):
    """The widget adds no identity arguments and reports exhausted resolution."""
    signature = inspect.signature(fabricops_kit.widget_view_catalogue)
    assert list(signature.parameters) == ["mode", "agreement", "spark_session", "target", "schema", "context"]

    module = importlib.import_module("fabricops_kit.widgets.widget_view_catalogue")
    fake_notebookutils.runtime.context.clear()
    with pytest.raises(
        ValueError,
        match="active FabricOps context or Fabric runtime context",
    ):
        module.widget_view_catalogue(mode="pipeline", context={"config": object(), "env": "dev"})


def test_catalogue_views_select_one_snapshot_and_one_frequency_column(monkeypatch, spark_session):
    """Views keep compact parents and normalized children on one exact snapshot."""
    import fabricops_kit.widgets.shared as shared
    from tests.unit.test_widget_register_data_contract import _FakeWidgets

    _FakeWidgets.Dropdown = _FakeWidgets.Select

    class FakeHTML(_FakeWidgets.HTML):
        """Capture positional HTML content like ipywidgets.HTML."""

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
    monkeypatch.setattr(shared, "require_ipywidgets", lambda: _FakeWidgets)

    old_snapshot = datetime(2026, 7, 30)
    latest_snapshot = datetime(2026, 7, 31)
    later_snapshot = datetime(2026, 8, 1)
    tables = {
        "METADATA_DATA_CATALOGUE": spark_session.createDataFrame(
            [
                ("dataset-key", "fingerprint", "id", "column-id", latest_snapshot),
                ("dataset-key", "previous-fingerprint", "id", "column-id", old_snapshot),
                ("unprofiled-key", "fingerprint-2", "id", "column-id-2", latest_snapshot),
            ],
            "metadata_table_key string, schema_fingerprint string, column_name string, "
            "metadata_column_key string, _committed_at timestamp",
        ),
        "METADATA_DATA_PROFILED": spark_session.createDataFrame(
            [
                ("dataset-key", "fingerprint", "column-a", "Country", old_snapshot, old_snapshot),
                ("dataset-key", "fingerprint", "column-a", "Country", latest_snapshot, latest_snapshot),
                ("dataset-key", "fingerprint", "column-b", "Comment", latest_snapshot, latest_snapshot),
                ("dataset-key", "previous-fingerprint", "column-a", "Country", old_snapshot, old_snapshot),
            ],
            "metadata_table_key string, schema_fingerprint string, metadata_column_key string, "
            "column_name string, profiled_at timestamp, _committed_at timestamp",
        ),
        "METADATA_DATA_PROFILED_FREQUENCY": spark_session.createDataFrame(
            [
                ("column-a", "old", 1, 1, old_snapshot),
                ("column-a", None, 2, 1, latest_snapshot),
                ("column-a", "current", 3, 2, latest_snapshot),
                ("column-a", "future", 4, 1, later_snapshot),
                ("unrelated-column", "other", 5, 1, latest_snapshot),
            ],
            "metadata_column_key string, value string, frequency_count long, "
            "frequency_rank integer, profiled_at timestamp",
        ),
        "METADATA_GUARDRAIL_RESULTS": spark_session.createDataFrame(
            [
                (
                    "dataset-key",
                    "orders",
                    "old-run",
                    "not_null",
                    "id",
                    "failed",
                    "error",
                    False,
                    "old failure",
                    '{"failed_count":1,"failed_percent":25.0,"total_count":4}',
                    old_snapshot,
                ),
                (
                    "dataset-key",
                    "orders",
                    "latest-run",
                    "required_when",
                    "required_value,status",
                    "failed",
                    "error",
                    False,
                    "required value missing",
                    '{"failed_count":1,"failed_percent":25.0,"total_count":4}',
                    latest_snapshot,
                ),
                (
                    "dataset-key",
                    "orders",
                    "latest-run",
                    "not_null",
                    "id",
                    "passed",
                    "error",
                    True,
                    "Rule passed.",
                    '{"failed_count":0,"failed_percent":0.0,"total_count":4}',
                    latest_snapshot,
                ),
                (
                    "other-key",
                    "orders",
                    "other-run",
                    "not_null",
                    "id",
                    "failed",
                    "error",
                    False,
                    "wrong canonical table",
                    '{"failed_count":9,"failed_percent":90.0,"total_count":10}',
                    later_snapshot,
                ),
                (
                    "unprofiled-key",
                    "customers",
                    "customer-run",
                    "not_null",
                    "customer_id",
                    "passed",
                    "error",
                    True,
                    "Rule passed.",
                    '{"failed_count":0,"failed_percent":0.0,"total_count":2}',
                    later_snapshot,
                ),
            ],
            "metadata_table_key string, table_name string, run_id string, rule_type string, column_name string, "
            "status string, severity string, can_continue boolean, reason string, actual_value_json string, _committed_at timestamp",
        ),
        "METADATA_GUARDRAIL_ROW_RESULTS": spark_session.createDataFrame(
            [
                (
                    "dataset-key",
                    "latest-run",
                    "required_when",
                    '{"id":1}',
                    '["required_value","status"]',
                    '{"required_value":null,"status":"open"}',
                    "required value was null",
                ),
                ("dataset-key", "latest-run", "not_null", '{"id":1}', '["id"]', '{"id":null}', "id was null"),
                ("dataset-key", "old-run", "not_null", '{"id":2}', '["id"]', '{"id":null}', "old failure"),
                ("other-key", "other-run", "not_null", '{"id":3}', '["id"]', '{"id":null}', "wrong canonical table"),
            ],
            "metadata_table_key string, run_id string, rule_type string, row_identity string, "
            "involved_columns_json string, failed_values_json string, failure_reason string",
        ),
    }
    read_calls = []

    def read_table(table, **_kwargs):
        read_calls.append(table)
        return tables[table]

    monkeypatch.setattr(shared, "read_lakehouse_table_core", read_table)

    state = build_catalogue_widget(
        title="Pipeline Catalogue Viewer",
        description="View data catalogues used by the current pipeline notebook",
        selection_context={"notebook_id": "technical-id", "environment_name": "dev"},
        display_context={"Notebook": "Customer <pipeline>", "Environment": "dev", "Linked datasets": 1},
        inventory_rows=[
            {
                "metadata_table_key": "dataset-key",
                "schema_fingerprint": "fingerprint",
                "layer": "raw",
                "schema_name": "sales",
                "table_name": "orders",
                "_committed_at": latest_snapshot,
            },
            {
                "metadata_table_key": "dataset-key",
                "schema_fingerprint": "previous-fingerprint",
                "layer": "raw",
                "schema_name": "sales",
                "table_name": "orders",
                "_committed_at": old_snapshot,
            },
            {
                "metadata_table_key": "unprofiled-key",
                "schema_fingerprint": "fingerprint-2",
                "layer": "z_curated",
                "schema_name": "sales",
                "table_name": "customers",
                "_committed_at": latest_snapshot,
            },
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
    assert "Customer <pipeline>" not in visible_html
    assert "<b>Environment:</b> dev" in visible_html
    assert "<b>Linked datasets:</b> 1" in visible_html
    assert "technical-id" not in visible_html
    assert "notebook_id" not in visible_html
    assert "environment_name" not in visible_html
    selection = state["get_selection"]()
    assert selection["notebook_id"] == "technical-id"
    assert selection["metadata_table_key"] == "dataset-key"
    assert selection["profiled_at"] is None
    assert selection["metadata_column_key"] is None
    assert read_calls == []
    views = state["get_views"]()
    assert read_calls == [
        "METADATA_DATA_CATALOGUE",
        "METADATA_DATA_PROFILED",
        "METADATA_DATA_PROFILED_FREQUENCY",
        "METADATA_GUARDRAIL_RESULTS",
        "METADATA_GUARDRAIL_ROW_RESULTS",
    ]
    assert state["get_selection"]()["profiled_at"] == latest_snapshot
    assert state["get_selection"]()["metadata_column_key"] == "column-a"
    assert set(views) == {"catalogue", "profile", "frequency", "guardrail_results", "guardrail_row_results"}
    assert {row.profiled_at for row in views["profile"].collect()} == {latest_snapshot}
    frequency_rows = views["frequency"].collect()
    assert {row.profiled_at for row in frequency_rows} == {latest_snapshot}
    assert {row.metadata_column_key for row in frequency_rows} == {"column-a"}
    assert {row.value for row in frequency_rows} == {None, "current"}
    guardrail_rows = views["guardrail_results"].collect()
    assert {row.run_id for row in guardrail_rows} == {"latest-run"}
    assert [row.status for row in guardrail_rows] == ["failed", "passed"]
    assert guardrail_rows[0].failed_rows == 1
    evidence_rows = views["guardrail_row_results"].collect()
    assert len(evidence_rows) == 2
    assert {row.rule_type for row in evidence_rows} == {"required_when", "not_null"}
    assert {row.row_identity for row in evidence_rows} == {'{"id":1}'}
    required = next(row for row in evidence_rows if row.rule_type == "required_when")
    assert '"required_value":null' in required.failed_values

    state["_controls"]["search"].value = "does not exist"
    assert state["_controls"]["dataset"].value is None
    state["_controls"]["search"].value = ""
    assert state["_controls"]["dataset"].value == "\x1fdataset-key"
    assert len(read_calls) == 5

    selected_details = page.children[3].children[1]
    state["_controls"]["schema_fingerprint"].value = "previous-fingerprint"
    assert "<b>Schema version:</b> previous-fingerprint" in selected_details.value
    state["_controls"]["schema_fingerprint"].value = "fingerprint"
    assert len(read_calls) == 5

    state["_controls"]["metadata_column_key"].value = "column-b"
    assert state["get_selection"]()["metadata_column_key"] == "column-b"
    assert state["get_views"]()["frequency"].count() == 0
    assert len(read_calls) == 5

    state["_controls"]["dataset"].value = "\x1funprofiled-key"
    unprofiled = state["get_views"]()
    assert len(read_calls) == 5
    assert state["get_selection"]()["profiled_at"] is None
    assert unprofiled["profile"].count() == 0
    assert unprofiled["frequency"].count() == 0
    assert unprofiled["profile"].schema == tables["METADATA_DATA_PROFILED"].schema
    assert unprofiled["frequency"].schema == tables["METADATA_DATA_PROFILED_FREQUENCY"].schema
    assert {row.run_id for row in unprofiled["guardrail_results"].collect()} == {"customer-run"}
    assert unprofiled["guardrail_row_results"].count() == 0
