"""Public widget entrypoint for viewing a registered dataset contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import read_lakehouse_table_core
from fabricops_kit.widgets.shared import (
    get_data_contract_views,
    render_expandable_dataframe,
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


def widget_view_data_contract(
    *,
    agreement: dict[str, Any] | None = None,
    metadata_id: str | None = None,
    metadata_ids: Mapping[str, str] | Sequence[str] | None = None,
    schema_version: str | None = None,
    target: str = "metadata",
    schema: str | None = None,
    spark_session=None,
    context=None,
):
    """Render the governed metadata surfaces for one registered dataset.

    Parameters
    ----------
    agreement : dict, optional
        Agreement record or agreement-widget state. Linked data contracts are
        offered first when canonical contract links already exist.
    metadata_id : str, optional
        Canonical ``metadata_table_key`` to select initially.
    metadata_ids : mapping or sequence of str, optional
        Canonical dataset identities allowed in restricted mode. Mapping keys
        become readable role labels, such as ``Source`` and ``Target``.
    schema_version : str, optional
        Canonical ``schema_fingerprint`` to select initially.
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
        Mutable state containing canonical selections, the displayed Spark
        DataFrames, expandable preview controls, and a ``get_views`` callable.

    Notes
    -----
    The environment is fixed to the active FabricOps context. Dataset identity
    is the stable ``metadata_table_key``; schema history is selected with the
    canonical ``schema_fingerprint``. Each displayed view collects at most 200
    preview rows. Its CSV, JSON, and Parquet actions write the complete filtered
    Spark DataFrame to a unique ``Files/fabricops_exports`` location under the
    configured metadata target; export paths are reported in the widget.

    Examples
    --------
    >>> state = widget_view_data_contract()
    >>> views = state["get_views"]()
    >>> views["current_contract"].show()

    """
    restricted_items = _normalize_metadata_ids(metadata_ids)
    restricted_mode = metadata_ids is not None
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError as exc:
        message = str(exc)
        print(f"Data contract viewer unavailable: {message}")
        empty_state: dict[str, Any] = {
            "error": message,
            "metadata_table_key": metadata_id,
            "schema_fingerprint": schema_version,
            "selection_mode": "restricted" if restricted_mode else ("direct" if metadata_id else "discovery"),
            "allowed_metadata_ids": [metadata_key for _label, metadata_key in restricted_items],
        }
        empty_state["get_views"] = lambda: {key: value for key, value in empty_state.items() if key != "get_views"}
        return empty_state

    config, env, resolved = resolve_fabric_context(context=context)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
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
    version = widgets.Dropdown(options=[], **widget_common(widgets, "Schema version"))
    controls_box = widgets.VBox([])
    output = widgets.Output()
    state: dict[str, Any] = {
        "environment_name": env, "store_type": None, "layer": None,
        "schema_name": None, "table_name": None, "metadata_table_key": None,
        "schema_fingerprint": None, "agreement_id": agreement_id,
        "linked_metadata_ids": linked_metadata_ids,
        "selection_mode": "restricted" if restricted_mode else ("direct" if metadata_id else "discovery"),
        "allowed_metadata_ids": [metadata_key for _label, metadata_key in restricted_items],
    }

    def get_views():
        """Return current selections and assembled DataFrames."""
        return {key: value for key, value in state.items() if key not in {"get_views", "_controls"}}

    state["get_views"] = get_views
    initial_schema_pending = True

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
        nonlocal initial_schema_pending
        for field, _label in hierarchy:
            state[field] = controls[field].value
        metadata_id = state["metadata_table_key"]
        if not metadata_id:
            with output:
                output.clear_output(wait=True)
                ip.display(widgets.HTML("<i>No pipeline metadata IDs are configured for this restricted view.</i>"))
            return
        selected_location = next((row for row in rows if row.get("metadata_table_key") == metadata_id), {})
        for field in ("environment_name", "store_type", "layer", "schema_name", "table_name"):
            state[field] = selected_location.get(field)
        from pyspark.sql import functions as F

        versions = [row["schema_fingerprint"] for row in (
            catalogue.filter(F.col("metadata_table_key") == metadata_id)
            .groupBy("schema_fingerprint").agg(F.max("_committed_at").alias("latest_at"))
            .orderBy(F.col("latest_at").desc_nulls_last()).collect()
        )]
        requested_schema = schema_version if initial_schema_pending else None
        selected = requested_schema if requested_schema in versions else (version.value if version.value in versions else (versions[0] if versions else None))
        version.options = [((f"{value} (latest)" if index == 0 else str(value)), value) for index, value in enumerate(versions)]
        version.value = selected
        state["schema_fingerprint"] = selected
        initial_schema_pending = False
        views = get_data_contract_views(
            metadata_id, schema_fingerprint=selected, target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        state.update(views)
        with output:
            output.clear_output(wait=True)
            viewers = {}
            export_identity = str(metadata_id)
            schema_identity = str(selected or "latest")
            for title, key, filename, preview_columns, expanded_columns in [
                ("Dataset summary", "summary", f"dataset-summary_{export_identity}_{schema_identity}", None, None),
                ("Current data contract", "current_contract", f"data-contract_{export_identity}_{schema_identity}", ["column_name", "data_type", "enrichment_business_meaning", "enrichment_classification", "guardrail_rule_type", "guardrail_severity"], None),
                ("Data Profiled", "data_profiled", f"data-profiled_{export_identity}", ["profiled_at", "schema_fingerprint", "column_name", "row_count", "null_percent", "distinct_percent"], ["frequency_json"]),
                ("Guardrail Results", "guardrail_results", f"guardrail-results_{export_identity}", ["_committed_at", "column_name", "rule_type", "status", "can_continue", "severity"], ["reason", "expected_value_json", "actual_value_json", "result_payload_json"]),
                ("Data Access", "data_access", f"data-access_{export_identity}", ["user_principal", "permission", "access_scope", "approval_status", "approved_at", "expires_at"], None),
            ]:
                viewer = render_expandable_dataframe(
                    state[key], title=title, max_rows=200,
                    preview_columns=preview_columns, expanded_columns=expanded_columns,
                    download_filename=filename, download_target=target, context=runtime_context,
                )
                viewers[key] = viewer
                ip.display(viewer["container"])
            state["viewers"] = viewers

    for index, (field, _label) in enumerate(hierarchy):
        controls[field].observe(lambda change, i=index: refresh_from(i + 1) if change.get("name") == "value" else None, names="value")
    version.observe(lambda change: refresh_views() if change.get("name") == "value" and change.get("new") else None, names="value")
    refresh_from()
    state["_controls"] = {**controls, "schema_fingerprint": version, "output": output}
    ip.display(widgets.VBox([widgets.HTML("<h2>View data contract</h2>"), controls_box, version, output]))
    return state
