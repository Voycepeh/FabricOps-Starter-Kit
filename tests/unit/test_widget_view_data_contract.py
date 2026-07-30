"""Tests for data-contract view selection helpers."""

from __future__ import annotations

import pytest
from datetime import datetime

import fabricops_kit
from fabricops_kit.widgets import widget_view_data_contract as public_widget
from fabricops_kit.widgets.widget_view_data_contract import (
    _agreement_details,
    _assembled_views,
    _base_dataset_label,
    _dataset_options,
    _normalize_metadata_ids,
    _pipeline_scope_items,
    _schema_version_options,
)
from fabricops_kit.widgets.shared import (
    get_data_contract_views,
    get_current_notebook_lineage_scope,
)

pytestmark = pytest.mark.unit


ROWS = [
    {"store_type": "lakehouse", "layer": "curated", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "one"},
    {"store_type": "lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "two"},
    {"store_type": "warehouse", "layer": "curated", "schema_name": "dbo", "table_name": "orders", "metadata_table_key": "three"},
]


def test_dataset_options_use_readable_locations_and_canonical_values():
    """One selector omits blank schemas and progressively disambiguates labels."""
    rows = [
        {**ROWS[0], "environment_name": "dev"},
        {**ROWS[0], "metadata_table_key": "four", "store_type": "warehouse", "environment_name": "dev"},
        {**ROWS[0], "metadata_table_key": "five", "environment_name": "prod"},
        {**ROWS[1], "metadata_table_key": "blank", "schema_name": "", "table_name": "customers", "environment_name": "dev"},
    ]
    options = _dataset_options(rows)
    assert _base_dataset_label(rows[-1]) == "raw / customers"
    assert {value for _label, value in options} == {"one", "four", "five", "blank"}
    labels = dict((value, label) for label, value in options)
    assert labels["four"].startswith("warehouse — curated / sales / orders")
    assert labels["one"].endswith("dev")
    assert labels["five"].endswith("prod")


def test_dataset_options_use_key_as_final_deterministic_fallback():
    """Physically indistinguishable observations never silently collapse."""
    rows = [
        {**ROWS[0], "environment_name": "dev", "metadata_table_key": "abcdefgh-one"},
        {**ROWS[0], "environment_name": "dev", "metadata_table_key": "ijklmnop-two"},
    ]
    labels = [label for label, _value in _dataset_options(rows)]
    assert any("abcdefgh" in label for label in labels)
    assert any("ijklmnop" in label for label in labels)


def test_widget_is_publicly_importable_and_old_export_is_removed():
    """Only the intentional Preview rename is exported."""
    assert fabricops_kit.widget_view_data_contract is public_widget
    assert "widget_browse_metadata_catalogue" not in fabricops_kit.__all__
    with pytest.raises(AttributeError):
        getattr(fabricops_kit, "widget_browse_metadata_catalogue")


def test_widget_returns_dataframe_views_without_rendering_them():
    """The selector leaves native DataFrame rendering to separate notebook cells."""
    import inspect
    import fabricops_kit.widgets.shared as shared

    source = inspect.getsource(public_widget)
    assert "display(frame)" not in source
    assert "render_expandable_dataframe" not in source
    for removed_name in (
        "format_full_value", "_compact_value", "export_dataframe_to_files",
        "render_expandable_dataframe",
    ):
        assert not hasattr(shared, removed_name)


def test_assembled_views_preserve_existing_keys_and_frames():
    """The viewer aliases raw trace tables without transforming Spark schemas."""
    frames = {
        "METADATA_DATA_CATALOGUE": object(), "METADATA_DATA_CONTRACT": object(),
        "METADATA_DATA_PROFILED": object(), "METADATA_GUARDRAIL_RESULTS": object(),
        "METADATA_DATA_ACCESS": object(),
    }
    views = _assembled_views({"tables": frames})
    assert list(views) == [
        "summary", "current_contract", "data_profiled", "guardrail_results", "data_access",
    ]
    assert list(views.values()) == list(frames.values())


def test_agreement_context_resolves_records_and_widget_state():
    """Agreement records and agreement-widget selections resolve the same ID."""
    assert _agreement_details({"agreement_id": " agreement-1 ", "agreement_name": "Sales"}, None) == ("agreement-1", "Sales")

    class Selected:
        value = "agreement-2"

    state = {
        "existing_record": Selected(),
        "existing_records_by_id": {"agreement-2": {"agreement_id": "agreement-2"}},
    }
    assert _agreement_details(state, None)[0] == "agreement-2"
    assert _agreement_details({"agreement_id": "state"}, " explicit ")[0] == "explicit"
    assert _agreement_details({"agreement_id": "state"}, " ")[0] == "state"


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
    assert _pipeline_scope_items(
        [("Source / Target", "history-id")], [("Current source", "current-id")],
    ) == ([('Source / Target', 'history-id')], "current_notebook_lineage")
    assert _pipeline_scope_items([], [("Current source", "current-id")]) == (
        [("Current source", "current-id")], "metadata_ids_fallback",
    )
    assert _pipeline_scope_items([], []) == ([], "empty")


def test_schema_versions_are_readable_newest_first_and_keep_full_values():
    """Timestamp labels do not replace canonical full schema fingerprints."""
    old = datetime(2026, 7, 20, 14, 5)
    new = datetime(2026, 7, 29, 21, 30)
    rows = [
        {"metadata_table_key": "one", "schema_fingerprint": "old-full-fingerprint", "_committed_at": old},
        {"metadata_table_key": "one", "schema_fingerprint": "new-full-fingerprint", "_committed_at": new},
    ]
    assert _schema_version_options(rows, "one") == [
        ("Latest — 29 Jul 2026, 9:30 PM", "new-full-fingerprint"),
        ("Previous — 20 Jul 2026, 2:05 PM", "old-full-fingerprint"),
    ]


def test_schema_versions_disambiguate_duplicate_and_missing_timestamps():
    """Ambiguous schema labels gain stable shortened fingerprints."""
    same = datetime(2026, 7, 29, 21, 30)
    rows = [
        {"metadata_table_key": "one", "schema_fingerprint": "aaaaaaaa-full", "_committed_at": same},
        {"metadata_table_key": "one", "schema_fingerprint": "bbbbbbbb-full", "_committed_at": same},
        {"metadata_table_key": "one", "schema_fingerprint": "cccccccc-full", "_committed_at": None},
    ]
    options = _schema_version_options(rows, "one")
    assert {value for _label, value in options} == {"aaaaaaaa-full", "bbbbbbbb-full", "cccccccc-full"}
    assert all(value[:8] in label for label, value in options)


def test_agreement_scope_is_exclusive():
    """Agreement governance cannot be combined with other restricted scopes."""
    with pytest.raises(ValueError, match="pipeline_scope"):
        public_widget(agreement_id="agreement-1", pipeline_scope="current_notebook")
    with pytest.raises(ValueError, match="metadata_ids"):
        public_widget(agreement={"agreement_id": "agreement-1"}, metadata_ids=["one"])


def test_agreement_scope_strictly_intersects_active_catalogue(monkeypatch, spark_session):
    """Only contract-linked logical keys observed in the active environment are selectable."""
    import importlib
    from tests.unit.test_widget_register_data_contract import _FakeWidgets

    module = importlib.import_module("fabricops_kit.widgets.widget_view_data_contract")
    _FakeWidgets.Dropdown = _FakeWidgets.Select
    now = datetime(2026, 7, 29, 21, 30)
    catalogue = spark_session.createDataFrame([
        ("linked", "fingerprint-linked", "dev", "lakehouse", "raw", "sales", "orders", now),
        ("unrelated", "fingerprint-other", "dev", "lakehouse", "raw", "sales", "other", now),
        ("prod-only", "fingerprint-prod", "prod", "lakehouse", "raw", "sales", "secret", now),
    ], "metadata_table_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, _committed_at timestamp")
    contracts = spark_session.createDataFrame([
        ("agreement-1", "linked"), ("agreement-1", "linked"),
        ("agreement-1", "prod-only"), ("agreement-2", "unrelated"),
    ], "agreement_id string, metadata_table_key string")
    monkeypatch.setattr(module, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: (object(), "dev", {}))
    monkeypatch.setattr(
        module, "read_lakehouse_table_core",
        lambda name, **_kwargs: catalogue if name == "METADATA_DATA_CATALOGUE" else contracts,
    )
    monkeypatch.setattr(
        module, "get_data_contract_views",
        lambda key, **kwargs: {"selection": {"metadata_table_key": key}, "tables": {}, "error": None},
    )
    monkeypatch.setattr("IPython.display.display", lambda *_args, **_kwargs: None)

    state = public_widget(
        agreement={"agreement_id": "agreement-1", "agreement_name": "Sales agreement"},
        metadata_id="unrelated",
    )

    assert state["selection_mode"] == "agreement"
    assert state["linked_metadata_ids"] == ["linked", "prod-only"]
    assert state["allowed_metadata_ids"] == ["linked"]
    assert state["metadata_table_key"] == "linked"
    assert state["_controls"]["dataset"].description == "Agreement dataset"
    assert state["_controls"]["dataset"].disabled is True
    assert set(state["_controls"]) == {"dataset", "schema_fingerprint"}
    assert state["schema_fingerprint"] == "fingerprint-linked"


@pytest.mark.parametrize(
    ("catalogue_environment", "expected_message"),
    [
        (None, "No datasets are linked to this agreement yet"),
        ("prod", "none resolve to registered datasets in the active environment"),
    ],
)
def test_agreement_empty_states_never_fall_back_to_discovery(
    monkeypatch, spark_session, catalogue_environment, expected_message,
):
    """Empty links and cross-environment-only links retain strict agreement state."""
    import importlib
    from tests.unit.test_widget_register_data_contract import _FakeWidgets

    module = importlib.import_module("fabricops_kit.widgets.widget_view_data_contract")
    _FakeWidgets.Dropdown = _FakeWidgets.Select
    now = datetime(2026, 7, 29)
    catalogue = spark_session.createDataFrame([
        ("linked", "fingerprint", catalogue_environment or "dev", "lakehouse", "raw", "sales", "orders", now),
    ], "metadata_table_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, _committed_at timestamp")
    contract_rows = [] if catalogue_environment is None else [("agreement-1", "linked")]
    contracts = spark_session.createDataFrame(contract_rows, "agreement_id string, metadata_table_key string")
    monkeypatch.setattr(module, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: (object(), "dev", {}))
    monkeypatch.setattr(
        module, "read_lakehouse_table_core",
        lambda name, **_kwargs: catalogue if name == "METADATA_DATA_CATALOGUE" else contracts,
    )

    state = public_widget(agreement_id=" agreement-1 ")

    assert state["selection_mode"] == "agreement"
    assert state["allowed_metadata_ids"] == []
    assert expected_message in state["error"]
    assert state["get_views"]()["selection"] is None
    if catalogue_environment == "prod":
        assert state["linked_metadata_ids"] == ["linked"]


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
    )

    assert state["metadata_table_key"] == "dataset-1"
    assert state["selection_mode"] == "restricted"
    assert state["allowed_metadata_ids"] == ["dataset-1"]
    assert "Install the widget extra" in state["error"]
    assert state["get_views"]() == {
        "selection": None, "tables": {}, "error": "Install the widget extra.",
    }
    assert "Data contract viewer unavailable" in capsys.readouterr().out


def test_metadata_trace_returns_canonical_raw_filtered_tables(monkeypatch, spark_session):
    """The trace helper filters raw canonical tables without joins or renames."""
    old = datetime(2026, 1, 1)
    new = datetime(2026, 2, 1)

    def frame(rows, schema):
        return spark_session.createDataFrame(rows, schema)

    tables = {
        "METADATA_DATA_STEWARD": frame(
            [("provider", "Provider", old), ("recipient", "Recipient", new), ("other", "Other", new)],
            "steward_id string, marker string, _committed_at timestamp",
        ),
        "METADATA_DATA_AGREEMENT": frame(
            [("agreement-1", "provider", "recipient", "old agreement", old),
             ("agreement-1", "provider", "recipient", "new agreement", new),
             ("agreement-2", "other", "other", "other agreement", new)],
            "agreement_id string, provider_steward_id string, recipient_steward_id string, marker string, _committed_at timestamp",
        ),
        "METADATA_DATA_CONTRACT": frame(
            [("agreement-1", "dataset", "snapshot-old", old),
             ("agreement-1", "dataset", "snapshot-new", new),
             ("agreement-2", "dataset", "snapshot-second-agreement", new),
             ("agreement-2", "other", "snapshot-other", new)],
            "agreement_id string, metadata_table_key string, _activity_id string, _committed_at timestamp",
        ),
    }
    environment_tables = {
        "METADATA_DATA_CATALOGUE", "METADATA_DATA_PROFILED", "METADATA_DATA_LINEAGE",
        "METADATA_GUARDRAIL", "METADATA_GUARDRAIL_RESULTS",
    }
    for table_name in (
        "METADATA_DATA_CATALOGUE", "METADATA_DATA_PROFILED", "METADATA_DATA_LINEAGE",
        "METADATA_DATA_ACCESS", "METADATA_ENRICHMENT", "METADATA_GUARDRAIL",
        "METADATA_GUARDRAIL_RESULTS",
    ):
        if table_name in environment_tables:
            tables[table_name] = frame(
                [("dataset", "dev", "old", old), ("dataset", "dev", "new", new),
                 ("dataset", "prod", "other environment", new), ("other", "dev", "other dataset", new)],
                "metadata_table_key string, environment_name string, marker string, _committed_at timestamp",
            )
        else:
            tables[table_name] = frame(
                [("dataset", "old", old), ("dataset", "new", new), ("other", "other dataset", new)],
                "metadata_table_key string, marker string, _committed_at timestamp",
            )
    monkeypatch.setattr(
        "fabricops_kit.widgets.shared.read_lakehouse_table_core",
        lambda name, **_kwargs: tables[name],
    )

    views = get_data_contract_views(
        "dataset", agreement_id="agreement-1", environment_name="dev",
        spark_session=spark_session,
    )

    assert list(views) == ["selection", "tables", "error"]
    assert set(views["tables"]) == set(tables)
    assert views["error"] is None
    assert views["selection"] == {
        "environment_name": "dev", "metadata_table_key": "dataset",
        "agreement_id": "agreement-1", "provider_steward_id": "provider",
        "recipient_steward_id": "recipient",
    }
    assert [row.steward_id for row in views["tables"]["METADATA_DATA_STEWARD"].collect()] == [
        "recipient", "provider",
    ]
    assert [row.marker for row in views["tables"]["METADATA_DATA_AGREEMENT"].collect()] == [
        "new agreement", "old agreement",
    ]
    assert [row._activity_id for row in views["tables"]["METADATA_DATA_CONTRACT"].collect()] == [
        "snapshot-new", "snapshot-old",
    ]
    for table_name in tables:
        assert views["tables"][table_name].columns == tables[table_name].columns
        assert all(row._committed_at in {old, new} for row in views["tables"][table_name].collect())
    for table_name in environment_tables:
        assert [row.marker for row in views["tables"][table_name].collect()] == ["new", "old"]
    assert [row.marker for row in views["tables"]["METADATA_ENRICHMENT"].collect()] == ["new", "old"]

    unscoped = get_data_contract_views("dataset", environment_name="dev", spark_session=spark_session)
    assert unscoped["selection"]["agreement_id"] is None
    assert {row.agreement_id for row in unscoped["tables"]["METADATA_DATA_AGREEMENT"].collect()} == {
        "agreement-1", "agreement-2",
    }
    assert {row.steward_id for row in unscoped["tables"]["METADATA_DATA_STEWARD"].collect()} == {
        "provider", "recipient", "other",
    }
    assert {row._activity_id for row in unscoped["tables"]["METADATA_DATA_CONTRACT"].collect()} == {
        "snapshot-old", "snapshot-new", "snapshot-second-agreement",
    }

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


def test_widget_returns_non_breaking_state_when_lineage_context_is_unavailable(monkeypatch, capsys):
    """Optional pipeline inspection does not stop notebooks outside Fabric runtime context."""
    import importlib

    module = importlib.import_module("fabricops_kit.widgets.widget_view_data_contract")
    monkeypatch.setattr(module, "require_ipywidgets", lambda: object())
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda **_kwargs: (object(), "dev", {}),
    )
    monkeypatch.setattr(
        module,
        "get_current_notebook_lineage_scope",
        lambda **_kwargs: (_ for _ in ()).throw(ValueError("missing runtime IDs")),
    )

    state = public_widget(pipeline_scope="current_notebook")

    assert state["pipeline_scope_source"] == "unavailable"
    assert state["allowed_metadata_ids"] == []
    assert "Current-notebook lineage could not be resolved" in state["error"]
    assert state["get_views"]()["error"] == state["error"]
    assert state["get_views"]()["selection"] is None
    assert state["get_views"]()["tables"] == {}
    assert "Ensure 00_env_config has run" in capsys.readouterr().out


def test_widget_returns_non_breaking_state_when_notebook_has_no_lineage(monkeypatch, capsys):
    """A pipeline notebook without lineage receives an explicit empty error state."""
    import importlib

    module = importlib.import_module("fabricops_kit.widgets.widget_view_data_contract")
    monkeypatch.setattr(module, "require_ipywidgets", lambda: object())
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda **_kwargs: (
            object(),
            "dev",
            {"workspace_id": "workspace-1", "notebook_id": "notebook-1"},
        ),
    )
    monkeypatch.setattr(module, "get_current_notebook_lineage_scope", lambda **_kwargs: [])
    monkeypatch.setattr(
        module,
        "read_lakehouse_table_core",
        lambda *_args, **_kwargs: pytest.fail("catalogue must not be read without lineage"),
    )

    state = public_widget(pipeline_scope="current_notebook")

    assert state["pipeline_scope_source"] == "empty"
    assert state["allowed_metadata_ids"] == []
    assert state["selection_mode"] == "pipeline"
    assert "No lineage records were found for this notebook" in state["error"]
    assert state["get_views"]()["error"] == state["error"]
    assert state["get_views"]()["selection"] is None
    assert state["get_views"]()["tables"] == {}
    assert "Run the profiling and lineage-writing sections first" in capsys.readouterr().out
