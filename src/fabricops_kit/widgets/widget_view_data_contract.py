"""Public widget entrypoint for viewing a registered dataset contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import read_lakehouse_table_core
from fabricops_kit.widgets.shared import (
    get_data_contract_views,
    get_current_notebook_lineage_scope,
    require_ipywidgets,
    widget_common,
)


def _catalogue_locations(catalogue, environment: str) -> list[dict[str, Any]]:
    """Collect distinct canonical dataset locations for one environment."""
    from pyspark.sql import functions as F

    fields = [
        "environment_name",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "metadata_table_key",
    ]
    return [row.asDict(recursive=True) for row in catalogue.filter(F.col("environment_name") == environment).select(*fields).distinct().collect()]


def _options(rows: list[dict[str, Any]], field: str, selections: dict[str, Any]) -> list[Any]:
    """Return values for a hierarchy level constrained by earlier selections."""
    values = {
        row.get(field)
        for row in rows
        if all(row.get(key) == value for key, value in selections.items() if value is not None)
    }
    return sorted(values, key=lambda value: str(value or ""))


def _agreement_id_from_context(agreement: dict[str, Any] | None) -> str:
    """Resolve an agreement ID from a record or agreement-widget state."""
    if not agreement:
        return ""
    direct = str(agreement.get("agreement_id") or "").strip()
    if direct:
        return direct
    selected = agreement.get("existing_record")
    selected_value = str(getattr(selected, "value", "") or "").strip()
    selected_row = (agreement.get("existing_records_by_id") or {}).get(selected_value, {})
    return str(selected_row.get("agreement_id") or "").strip()


def _normalize_metadata_ids(metadata_ids: Mapping[str, str] | Sequence[str] | None) -> list[tuple[str, str]]:
    """Return ordered, non-empty display labels and canonical metadata IDs."""
    if metadata_ids is None:
        return []
    if isinstance(metadata_ids, Mapping):
        items = metadata_ids.items()
    elif isinstance(metadata_ids, Sequence) and not isinstance(metadata_ids, (str, bytes)):
        items = ((f"Dataset {index}", value) for index, value in enumerate(metadata_ids, start=1))
    else:
        raise TypeError("metadata_ids must be a mapping, a non-string sequence, or None")
    normalized: list[tuple[str, str]] = []
    seen: set[str] = set()
    for label, value in items:
        metadata_key = str(value or "").strip()
        if not metadata_key or metadata_key in seen:
            continue
        normalized.append((str(label or metadata_key).strip() or metadata_key, metadata_key))
        seen.add(metadata_key)
    return normalized


def _pipeline_scope_items(
    lineage_items: list[tuple[str, str]],
    fallback_items: list[tuple[str, str]],
) -> tuple[list[tuple[str, str]], str]:
    """Prefer historical lineage scope, then caller-supplied restricted IDs."""
    if lineage_items:
        return lineage_items, "current_notebook_lineage"
    if fallback_items:
        return fallback_items, "metadata_ids_fallback"
    return [], "empty"


def widget_view_data_contract(
    *,
    agreement: dict[str, Any] | None = None,
    metadata_id: str | None = None,
    metadata_ids: Mapping[str, str] | Sequence[str] | None = None,
    pipeline_scope: str | None = None,
    target: str = "metadata",
    schema: str | None = None,
    spark_session=None,
    context=None,
):
    """Render the canonical metadata trace for one registered dataset.

    Parameters
    ----------
    agreement : dict, optional
        Agreement record or agreement-widget state. Linked data contracts are
        offered first when canonical contract links already exist, and the
        resolved agreement ID constrains contract, agreement, and steward traces.
    metadata_id : str, optional
        Canonical ``metadata_table_key`` to select initially.
    metadata_ids : mapping or sequence of str, optional
        Canonical dataset identities allowed in restricted mode. Mapping keys
        become readable role labels, such as ``Source`` and ``Target``. When
        ``pipeline_scope`` is also supplied, these IDs are used only if the
        current notebook has no matching lineage history.
    pipeline_scope : {"current_notebook"}, optional
        Restrict discovery to historical metadata IDs recorded in Data Lineage
        for the active environment, workspace, and notebook.
    target : str, default="metadata"
        Configured FabricStore target containing FabricOps metadata tables.
    schema : str, optional
        Metadata lakehouse schema override.
    spark_session : object, optional
        Spark session override.
    context : object, optional
        Active FabricOps context override.

    Returns
    -------
    dict
        Mutable state containing the selected dataset and a ``get_views``
        callable. The callable returns all ten raw, filtered canonical metadata
        tables without rendering them.

    Notes
    -----
    The environment is fixed to the active FabricOps context. Dataset identity
    is the stable ``metadata_table_key``. All metadata history for that identity
    is retained within the supplied agreement scope. Without an agreement scope,
    every agreement linked to the dataset and all of their stewards are returned.
    The selected environment is applied only to canonical tables that contain
    ``environment_name``. After changing a widget selection, rerun the notebook
    cell that displays ``get_views()`` results.

    Examples
    --------
    >>> state = widget_view_data_contract()
    >>> views = state["get_views"]()
    >>> table_name = "METADATA_DATA_CONTRACT"
    >>> views["tables"][table_name].show()

    """
    if pipeline_scope not in {None, "current_notebook"}:
        raise ValueError("pipeline_scope must be 'current_notebook' or None")
    restricted_items = _normalize_metadata_ids(metadata_ids)
    restricted_mode = metadata_ids is not None or pipeline_scope is not None
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError as exc:
        message = str(exc)
        print(f"Data contract viewer unavailable: {message}")
        empty_state: dict[str, Any] = {
            "error": message,
            "metadata_table_key": metadata_id,
            "selection_mode": "restricted" if restricted_mode else ("direct" if metadata_id else "discovery"),
            "allowed_metadata_ids": [metadata_key for _label, metadata_key in restricted_items],
        }
        empty_state["get_views"] = lambda: {"selection": None, "tables": {}, "error": message}
        return empty_state

    config, env, resolved = resolve_fabric_context(context=context)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    pipeline_scope_source = "explicit_metadata_ids" if restricted_items else "none"
    if pipeline_scope == "current_notebook":
        try:
            lineage_items = get_current_notebook_lineage_scope(
                target=target, schema=schema, spark_session=spark_session, context=runtime_context,
            )
        except ValueError as exc:
            message = (
                "Current-notebook lineage could not be resolved. Ensure 00_env_config has run "
                "and this notebook has written lineage metadata. "
                f"{exc}"
            )
            print(message)
            unavailable_state: dict[str, Any] = {
                "error": message,
                "metadata_table_key": metadata_id,
                "selection_mode": "restricted",
                "allowed_metadata_ids": [],
                "pipeline_scope_source": "unavailable",
            }
            unavailable_state["get_views"] = lambda: {"selection": None, "tables": {}, "error": message}
            return unavailable_state
        restricted_items, pipeline_scope_source = _pipeline_scope_items(lineage_items, restricted_items)
        if pipeline_scope_source == "empty":
            message = (
                "No lineage records were found for this notebook. "
                "Run the profiling and lineage-writing sections first."
            )
            print(message)
            empty_lineage_state: dict[str, Any] = {
                "error": message,
                "metadata_table_key": metadata_id,
                "selection_mode": "restricted",
                "allowed_metadata_ids": [],
                "pipeline_scope_source": "empty",
            }
            empty_lineage_state["get_views"] = lambda: {"selection": None, "tables": {}, "error": message}
            return empty_lineage_state
    catalogue = read_lakehouse_table_core(
        "METADATA_DATA_CATALOGUE", target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    rows = _catalogue_locations(catalogue, env)
    restricted_labels = {metadata_key: label for label, metadata_key in restricted_items}
    if restricted_mode:
        allowed = set(restricted_labels)
        rows = [row for row in rows if row.get("metadata_table_key") in allowed]
    agreement_id = _agreement_id_from_context(agreement)
    linked_metadata_ids: list[str] = []
    if agreement_id:
        from pyspark.sql import functions as F

        contracts = read_lakehouse_table_core(
            "METADATA_DATA_CONTRACT", target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        linked_metadata_ids = sorted({
            str(row["metadata_table_key"])
            for row in contracts.filter(F.col("agreement_id") == agreement_id)
            .select("metadata_table_key").distinct().collect()
            if row["metadata_table_key"]
        })
        linked = set(linked_metadata_ids)
        rows.sort(key=lambda row: (row.get("metadata_table_key") not in linked, str(row.get("table_name") or "")))
    from IPython import display as ip

    hierarchy = ([
        ("metadata_table_key", "Pipeline dataset"),
    ] if restricted_mode else [
        ("store_type", "FabricStore type"), ("layer", "Layer"),
        ("schema_name", "Schema"), ("table_name", "Table"),
        ("metadata_table_key", "Metadata ID"),
    ])
    controls = {field: widgets.Dropdown(options=[], **widget_common(widgets, label)) for field, label in hierarchy}
    controls_box = widgets.VBox([])
    state: dict[str, Any] = {
        "environment_name": env, "store_type": None, "layer": None,
        "schema_name": None, "table_name": None, "metadata_table_key": None,
        "agreement_id": agreement_id,
        "linked_metadata_ids": linked_metadata_ids,
        "selection_mode": "restricted" if restricted_mode else ("direct" if metadata_id else "discovery"),
        "allowed_metadata_ids": [metadata_key for _label, metadata_key in restricted_items],
        "pipeline_scope_source": pipeline_scope_source,
    }

    def get_views():
        """Return the current selection and ten raw metadata DataFrames."""
        if state.get("error"):
            return {"selection": None, "tables": {}, "error": state["error"]}
        return state.get("views", {"selection": None, "tables": {}, "error": "No dataset is selected."})

    state["get_views"] = get_views
    def refresh_from(start: int = 0) -> None:
        selections: dict[str, Any] = {}
        restricted_default = restricted_items[0][1] if restricted_items else None
        preferred_metadata_id = (metadata_id or restricted_default or (linked_metadata_ids[0] if linked_metadata_ids else None)) if start == 0 else None
        preferred_row = next((row for row in rows if row.get("metadata_table_key") == preferred_metadata_id), {})
        for index, (field, _label) in enumerate(hierarchy):
            if index < start:
                selections[field] = controls[field].value
                continue
            choices = (
                [metadata_key for _label, metadata_key in restricted_items if any(row.get("metadata_table_key") == metadata_key for row in rows)]
                if restricted_mode and field == "metadata_table_key"
                else _options(rows, field, selections)
            )
            current = controls[field].value
            requested = preferred_row.get(field)
            controls[field].options = [
                (
                    f"{restricted_labels[value]} — {next((row.get('table_name') for row in rows if row.get('metadata_table_key') == value), value)}"
                    if field == "metadata_table_key" and value in restricted_labels
                    else (str(value) if value not in {None, ""} else "(default schema)"),
                    value,
                )
                for value in choices
            ]
            controls[field].value = requested if requested in choices else (current if current in choices else (choices[0] if choices else None))
            selections[field] = controls[field].value
        controls_box.children = tuple(control for control in controls.values() if len(control.options) > 1)
        refresh_views()

    def refresh_views(*_: Any) -> None:
        for field, _label in hierarchy:
            state[field] = controls[field].value
        metadata_id = state["metadata_table_key"]
        if not metadata_id:
            state["views"] = {"selection": None, "tables": {}, "error": "No dataset is selected."}
            return
        selected_location = next((row for row in rows if row.get("metadata_table_key") == metadata_id), {})
        for field in ("environment_name", "store_type", "layer", "schema_name", "table_name"):
            state[field] = selected_location.get(field)
        views = get_data_contract_views(
            metadata_id, agreement_id=agreement_id or None,
            environment_name=state["environment_name"], target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        state["views"] = views
        state["agreement_id"] = views["selection"]["agreement_id"]

    for index, (field, _label) in enumerate(hierarchy):
        controls[field].observe(lambda change, i=index: refresh_from(i + 1) if change.get("name") == "value" else None, names="value")
    refresh_from()
    state["_controls"] = controls
    ip.display(widgets.VBox([widgets.HTML("<h2>View metadata trace</h2>"), controls_box]))
    return state
