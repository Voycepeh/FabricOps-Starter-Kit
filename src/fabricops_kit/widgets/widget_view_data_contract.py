"""Public widget entrypoint for viewing a registered dataset contract."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime
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
    """Collect canonical dataset/schema observations for one environment."""
    from pyspark.sql import functions as F

    fields = [
        "environment_name", "store_type", "layer", "schema_name", "table_name",
        "metadata_table_key", "schema_fingerprint", "_committed_at",
    ]
    return [
        row.asDict(recursive=True)
        for row in catalogue.filter(F.col("environment_name") == environment)
        .select(*fields).distinct().collect()
    ]


def _agreement_details(
    agreement: dict[str, Any] | None,
    agreement_id: str | None,
) -> tuple[str, str]:
    """Resolve the explicit-or-state agreement identity and readable label."""
    state = agreement or {}
    explicit = str(agreement_id or "").strip()
    direct = str(state.get("agreement_id") or "").strip()
    selected = state.get("existing_record")
    selected_value = str(getattr(selected, "value", "") or "").strip()
    selected_row = (state.get("existing_records_by_id") or {}).get(selected_value, {})
    resolved = explicit or direct or str(selected_row.get("agreement_id") or "").strip()
    label = str(
        state.get("agreement_name")
        or state.get("name")
        or selected_row.get("agreement_name")
        or selected_row.get("name")
        or ""
    ).strip()
    return resolved, label


def _normalize_metadata_ids(metadata_ids: Mapping[str, str] | Sequence[str] | None) -> list[tuple[str, str]]:
    """Return deterministic roles and canonical metadata IDs, combining duplicate roles."""
    if metadata_ids is None:
        return []
    combine_roles = isinstance(metadata_ids, Mapping)
    if combine_roles:
        items = metadata_ids.items()
    elif isinstance(metadata_ids, Sequence) and not isinstance(metadata_ids, (str, bytes)):
        items = ((f"Dataset {index}", value) for index, value in enumerate(metadata_ids, start=1))
    else:
        raise TypeError("metadata_ids must be a mapping, a non-string sequence, or None")
    roles: dict[str, list[str]] = {}
    for label, value in items:
        key = str(value or "").strip()
        if not key:
            continue
        if key in roles and not combine_roles:
            continue
        role = str(label or key).strip() or key
        if role not in roles.setdefault(key, []):
            roles[key].append(role)
    return [(" / ".join(labels), key) for key, labels in roles.items()]


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


def _base_dataset_label(row: Mapping[str, Any]) -> str:
    """Format a readable physical dataset location, omitting blank segments."""
    return " / ".join(
        str(row.get(field) or "").strip()
        for field in ("layer", "schema_name", "table_name")
        if str(row.get(field) or "").strip()
    )


def _dataset_options(
    rows: list[dict[str, Any]], roles: Mapping[str, str] | None = None,
) -> list[tuple[str, str]]:
    """Build unique readable labels whose values remain canonical logical keys."""
    by_key: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: (
        str(item.get("metadata_table_key") or ""),
        str(item.get("_committed_at") or ""),
    ), reverse=True):
        key = str(row.get("metadata_table_key") or "")
        if key:
            by_key[key] = row
    entries = [(key, row, _base_dataset_label(row)) for key, row in by_key.items()]
    base_counts = Counter(base for _key, _row, base in entries)
    labels: list[tuple[str, str]] = []
    provisional: list[tuple[str, str, dict[str, Any]]] = []
    for key, row, base in entries:
        label = base
        if base_counts[base] > 1:
            label = f"{str(row.get('store_type') or '').strip()} — {base}"
        provisional.append((key, label, row))
    first_counts = Counter(label for _key, label, _row in provisional)
    second: list[tuple[str, str]] = []
    for key, label, row in provisional:
        if first_counts[label] > 1:
            label = f"{label} — {str(row.get('environment_name') or '').strip()}"
        second.append((key, label))
    second_counts = Counter(label for _key, label in second)
    for key, label in second:
        if second_counts[label] > 1:
            label = f"{label} — {key[:8]}"
        role = (roles or {}).get(key)
        labels.append((f"{role} — {label}" if role else label, key))
    return sorted(labels, key=lambda item: (item[0].casefold(), item[1]))


def _format_timestamp(value: Any) -> str:
    """Format a timestamp deterministically without depending on process locale."""
    if not isinstance(value, datetime):
        return "Timestamp unavailable"
    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    hour = value.hour % 12 or 12
    period = "AM" if value.hour < 12 else "PM"
    return f"{value.day} {months[value.month - 1]} {value.year}, {hour}:{value.minute:02d} {period}"


def _schema_version_options(rows: list[dict[str, Any]], metadata_key: str) -> list[tuple[str, str]]:
    """Return newest-first readable schema labels backed by full fingerprints."""
    versions: dict[str, Any] = {}
    for row in rows:
        if str(row.get("metadata_table_key") or "") != metadata_key:
            continue
        fingerprint = str(row.get("schema_fingerprint") or "").strip()
        committed = row.get("_committed_at")
        if fingerprint and (fingerprint not in versions or str(committed or "") > str(versions[fingerprint] or "")):
            versions[fingerprint] = committed
    ordered = sorted(
        versions.items(), key=lambda item: (isinstance(item[1], datetime), item[1] or datetime.min, item[0]), reverse=True,
    )
    timestamp_counts = Counter(_format_timestamp(timestamp) for _fingerprint, timestamp in ordered)
    options = []
    for index, (fingerprint, timestamp) in enumerate(ordered):
        prefix = "Latest" if index == 0 else "Previous"
        formatted = _format_timestamp(timestamp)
        suffix = f" — {fingerprint[:8]}" if timestamp_counts[formatted] > 1 or not isinstance(timestamp, datetime) else ""
        options.append((f"{prefix} — {formatted}{suffix}", fingerprint))
    return options


def _empty_state(**values: Any) -> dict[str, Any]:
    """Return the stable, non-breaking viewer state for an unavailable scope."""
    message = str(values.pop("error"))
    state: dict[str, Any] = {
        "environment_name": values.pop("environment_name", None),
        "store_type": None, "layer": None, "schema_name": None, "table_name": None,
        "metadata_table_key": values.pop("metadata_table_key", None),
        "schema_fingerprint": values.pop("schema_fingerprint", None),
        "agreement_id": values.pop("agreement_id", ""),
        "linked_metadata_ids": values.pop("linked_metadata_ids", []),
        "allowed_metadata_ids": values.pop("allowed_metadata_ids", []),
        "pipeline_scope_source": values.pop("pipeline_scope_source", "none"),
        "_controls": {}, "error": message, **values,
    }
    state["get_views"] = lambda: {"selection": None, "tables": {}, "error": message}
    return state


def _assembled_views(trace: Mapping[str, Any]) -> dict[str, Any]:
    """Expose the established five review views without altering their frames."""
    tables = trace.get("tables") or {}
    return {
        "summary": tables.get("METADATA_DATA_CATALOGUE"),
        "current_contract": tables.get("METADATA_DATA_CONTRACT"),
        "data_profiled": tables.get("METADATA_DATA_PROFILED"),
        "guardrail_results": tables.get("METADATA_GUARDRAIL_RESULTS"),
        "data_access": tables.get("METADATA_DATA_ACCESS"),
    }


def widget_view_data_contract(
    *,
    agreement: dict[str, Any] | None = None,
    agreement_id: str | None = None,
    metadata_id: str | None = None,
    metadata_ids: Mapping[str, str] | Sequence[str] | None = None,
    pipeline_scope: str | None = None,
    schema_version: str | None = None,
    target: str = "metadata",
    schema: str | None = None,
    spark_session=None,
    context=None,
):
    """Review one dataset through a readable, scope-aware Data Contract viewer.

    Parameters
    ----------
    agreement : dict, optional
        Agreement record or agreement-widget state. This activates strict
        agreement scope and may also supply a readable agreement label.
    agreement_id : str, optional
        Direct agreement identity. A non-empty trimmed value takes precedence
        over the identity in ``agreement``.
    metadata_id : str, optional
        Canonical ``metadata_table_key`` to select initially within the allowed
        scope. It never broadens that scope.
    metadata_ids : mapping or sequence of str, optional
        Logical dataset identities for restricted selection, or fallback scope
        when current-notebook lineage is empty. Mapping keys are role labels.
    pipeline_scope : {"current_notebook"}, optional
        Restrict selection to lineage for the active environment and current
        workspace and notebook.
    schema_version : str, optional
        Full schema fingerprint to select initially when it exists for the
        selected dataset.
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
        Mutable state with selection mode, selected physical context, full
        schema fingerprint, linked and allowed logical IDs, controls, and
        ``get_views``. Existing view keys are ``summary``, ``current_contract``,
        ``data_profiled``, ``guardrail_results``, and ``data_access``.

    Raises
    ------
    ValueError
        If agreement scope is combined with pipeline or standalone restricted
        scope, or if ``pipeline_scope`` is unsupported.

    Notes
    -----
    The single dataset selector has ``agreement``, ``pipeline``, ``restricted``,
    ``direct``, and ``discovery`` modes. Agreement scope follows only
    ``agreement_id -> METADATA_DATA_CONTRACT -> metadata_table_key`` and then
    intersects those links with catalogue evidence in the active environment;
    unrelated or cross-environment datasets are never offered. Agreement and
    other restricted scopes are mutually exclusive. Empty agreement links and
    links absent from the active environment return explicit non-breaking empty
    states rather than discovery.

    Schema versions are newest first and have readable, locale-independent
    timestamps while retaining the full fingerprint as their value. Under the
    current schema contract, that fingerprint represents ordered column names
    and data types. Large Spark DataFrames are returned by ``get_views`` rather
    than rendered inside the widget.

    Examples
    --------
    >>> pipeline_view = widget_view_data_contract(
    ...     pipeline_scope="current_notebook", target="metadata",
    ...     schema=METADATA_SCHEMA, spark_session=spark,
    ... )
    >>> governance_view = widget_view_data_contract(
    ...     agreement=agreement_state, target="metadata",
    ...     schema=METADATA_SCHEMA, spark_session=spark,
    ... )
    >>> direct_view = widget_view_data_contract(
    ...     metadata_id="logical-table-key", target="metadata",
    ...     schema=METADATA_SCHEMA, spark_session=spark,
    ... )

    """
    agreement_scope = agreement is not None or agreement_id is not None
    if agreement_scope and pipeline_scope is not None:
        raise ValueError("Agreement scope cannot be combined with pipeline_scope.")
    if agreement_scope and metadata_ids is not None:
        raise ValueError("Agreement scope cannot be combined with standalone metadata_ids.")
    if pipeline_scope not in {None, "current_notebook"}:
        raise ValueError("pipeline_scope must be 'current_notebook' or None")
    resolved_agreement_id, agreement_label = _agreement_details(agreement, agreement_id)
    restricted_items = _normalize_metadata_ids(metadata_ids)
    if agreement_scope:
        selection_mode = "agreement"
    elif pipeline_scope == "current_notebook":
        selection_mode = "pipeline"
    elif metadata_ids is not None:
        selection_mode = "restricted"
    elif metadata_id is not None:
        selection_mode = "direct"
    else:
        selection_mode = "discovery"

    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError as exc:
        message = str(exc)
        print(f"Data contract viewer unavailable: {message}")
        return _empty_state(
            error=message, metadata_table_key=metadata_id, schema_fingerprint=schema_version,
            agreement_id=resolved_agreement_id, selection_mode=selection_mode,
            allowed_metadata_ids=[key for _label, key in restricted_items],
        )

    config, env, resolved = resolve_fabric_context(context=context)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    pipeline_scope_source = "none"
    if selection_mode == "pipeline":
        try:
            lineage_items = get_current_notebook_lineage_scope(
                target=target, schema=schema, spark_session=spark_session, context=runtime_context,
            )
        except ValueError as exc:
            message = (
                "Current-notebook lineage could not be resolved. Ensure 00_env_config has run "
                f"and workspace and notebook identities are available. {exc}"
            )
            print(message)
            return _empty_state(
                error=message, environment_name=env, metadata_table_key=metadata_id,
                schema_fingerprint=schema_version, agreement_id=resolved_agreement_id,
                selection_mode=selection_mode, pipeline_scope_source="unavailable",
            )
        restricted_items, pipeline_scope_source = _pipeline_scope_items(lineage_items, restricted_items)
        if pipeline_scope_source == "empty":
            message = "No lineage records were found for this notebook. Run the profiling and lineage-writing sections first."
            print(message)
            return _empty_state(
                error=message, environment_name=env, metadata_table_key=metadata_id,
                schema_fingerprint=schema_version, agreement_id=resolved_agreement_id,
                selection_mode=selection_mode, pipeline_scope_source="empty",
            )

    catalogue = read_lakehouse_table_core(
        "METADATA_DATA_CATALOGUE", target=target, schema=schema,
        spark_session=spark_session, context=runtime_context,
    )
    rows = _catalogue_locations(catalogue, env)
    linked_metadata_ids: list[str] = []
    if selection_mode == "agreement":
        from pyspark.sql import functions as F

        contracts = read_lakehouse_table_core(
            "METADATA_DATA_CONTRACT", target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        linked_metadata_ids = sorted({
            str(row["metadata_table_key"]).strip()
            for row in contracts.filter(F.col("agreement_id") == resolved_agreement_id)
            .select("metadata_table_key").distinct().collect()
            if str(row["metadata_table_key"] or "").strip()
        })
        if not linked_metadata_ids:
            message = (
                "No datasets are linked to this agreement yet. "
                "Create or register a Data Contract before reviewing dataset metadata."
            )
            print(message)
            return _empty_state(
                error=message, environment_name=env, metadata_table_key=metadata_id,
                schema_fingerprint=schema_version, agreement_id=resolved_agreement_id,
                linked_metadata_ids=[], selection_mode=selection_mode,
            )
        linked = set(linked_metadata_ids)
        rows = [row for row in rows if str(row.get("metadata_table_key") or "") in linked]
    elif selection_mode in {"pipeline", "restricted"}:
        restricted = {key for _label, key in restricted_items}
        rows = [row for row in rows if str(row.get("metadata_table_key") or "") in restricted]

    allowed_metadata_ids = sorted({str(row.get("metadata_table_key") or "") for row in rows if row.get("metadata_table_key")})
    if selection_mode == "agreement" and not allowed_metadata_ids:
        message = "This agreement has linked Data Contracts, but none resolve to registered datasets in the active environment."
        print(message)
        return _empty_state(
            error=message, environment_name=env, metadata_table_key=metadata_id,
            schema_fingerprint=schema_version, agreement_id=resolved_agreement_id,
            linked_metadata_ids=linked_metadata_ids, selection_mode=selection_mode,
        )
    if selection_mode in {"pipeline", "restricted"}:
        allowed_metadata_ids = [key for _label, key in restricted_items if key in set(allowed_metadata_ids)]

    role_by_key = {key: label for label, key in restricted_items}
    descriptions = {
        "agreement": "Agreement dataset", "pipeline": "Pipeline dataset",
        "restricted": "Restricted dataset", "direct": "Dataset", "discovery": "Dataset",
    }
    dataset = widgets.Dropdown(
        options=_dataset_options(rows, role_by_key),
        disabled=len(allowed_metadata_ids) == 1,
        **widget_common(widgets, descriptions[selection_mode]),
    )
    preferred = str(metadata_id or "").strip()
    if preferred in allowed_metadata_ids:
        dataset.value = preferred
    schema_control = widgets.Dropdown(options=[], **widget_common(widgets, "Schema Version"))
    context_control = widgets.HTML(value="")
    controls = {"dataset": dataset, "schema_fingerprint": schema_control}
    state: dict[str, Any] = {
        "environment_name": env, "store_type": None, "layer": None,
        "schema_name": None, "table_name": None, "metadata_table_key": None,
        "schema_fingerprint": None, "agreement_id": resolved_agreement_id,
        "linked_metadata_ids": linked_metadata_ids, "selection_mode": selection_mode,
        "allowed_metadata_ids": allowed_metadata_ids,
        "pipeline_scope_source": pipeline_scope_source, "_controls": controls,
    }

    def get_views():
        """Return existing assembled views for the current logical dataset."""
        return state.get("views", {"selection": None, "tables": {}, "error": "No dataset is selected."})

    state["get_views"] = get_views

    def refresh_views(*_: Any) -> None:
        key = str(dataset.value or "")
        state["metadata_table_key"] = key or None
        location = next((row for row in rows if str(row.get("metadata_table_key") or "") == key), {})
        for field in ("environment_name", "store_type", "layer", "schema_name", "table_name"):
            state[field] = location.get(field)
        version_options = _schema_version_options(rows, key)
        current_version = str(schema_control.value or "")
        schema_control.options = version_options
        version_values = [value for _label, value in version_options]
        requested_version = str(schema_version or "")
        schema_control.value = (
            requested_version if requested_version in version_values
            else current_version if current_version in version_values
            else version_values[0] if version_values else None
        )
        state["schema_fingerprint"] = schema_control.value
        agreement_context = f"<br><b>Agreement:</b> {agreement_label}" if selection_mode == "agreement" and agreement_label else ""
        context_control.value = (
            f"<b>Environment:</b> {state['environment_name'] or ''}<br>"
            f"<b>FabricStore:</b> {state['store_type'] or ''}<br>"
            f"<b>Location:</b> {_base_dataset_label(location)}{agreement_context}"
        )
        if not key:
            state["views"] = {"selection": None, "tables": {}, "error": "No dataset is selected."}
            return
        trace = get_data_contract_views(
            key, agreement_id=resolved_agreement_id or None,
            environment_name=state["environment_name"], target=target, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        state["views"] = _assembled_views(trace)

    dataset.observe(lambda change: refresh_views() if change.get("name") == "value" else None, names="value")
    schema_control.observe(
        lambda change: state.update(schema_fingerprint=change.get("new")) if change.get("name") == "value" else None,
        names="value",
    )
    refresh_views()
    from IPython import display as ip

    ip.display(widgets.VBox([
        widgets.HTML("<h2>View metadata trace</h2>"), dataset, context_control, schema_control,
    ]))
    return state
