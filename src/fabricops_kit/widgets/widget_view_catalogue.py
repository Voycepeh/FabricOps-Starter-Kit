"""Mode-scoped data catalogue selection widget."""

from __future__ import annotations

import html
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context, resolve_runtime_context
from fabricops_kit.io.shared import read_lakehouse_table_core
import fabricops_kit.widgets.shared as widget_shared


def _collect_catalogue_inventory(catalogue: Any, environment_name: str) -> list[dict[str, Any]]:
    """Collect one readable inventory row per normalized catalogue table."""
    from pyspark.sql import functions as F

    rows = (
        catalogue.filter(
            (F.col("environment_name") == environment_name)
            & (F.col("metadata_level") == "table")
        )
        .select(
            "table_id",
            "environment_name",
            "store_type",
            "layer",
            "schema_name",
            "table_name",
            "last_profiled_at",
        )
        .distinct()
        .collect()
    )
    return [row.asDict(recursive=True) for row in rows if str(row["table_id"] or "").strip()]


def _resolve_pipeline_catalogue_scope(
    *,
    environment_name: str,
    target: str,
    schema: str | None,
    spark_session: Any,
    context: Any,
    runtime_context: dict[str, Any],
) -> tuple[set[str], list[tuple[str, str]], dict[str, Any], dict[str, Any]]:
    """Resolve notebook-lineage table IDs and pipeline-role choices."""
    runtime = resolve_runtime_context(context=context)
    notebook_id = str(runtime.get("notebook_id") or "").strip()
    notebook_name = str(runtime.get("notebook_name") or notebook_id).strip()
    workspace_id = str(runtime.get("workspace_id") or "").strip()
    if not notebook_id:
        raise ValueError(
            "Unable to resolve the current notebook_id from the active FabricOps context or Fabric runtime context."
        )
    from pyspark.sql import functions as F

    lineage = read_lakehouse_table_core(
        "METADATA_DATA_LINEAGE",
        target=target,
        schema=schema,
        spark_session=spark_session,
        context=runtime_context,
    )
    predicate = (F.col("_notebook_id") == notebook_id) & (F.col("environment_name") == environment_name)
    if workspace_id:
        predicate &= F.col("_workspace_id") == workspace_id
    pairs = sorted(
        {
            (str(row["pipeline_role"] or "").strip().title(), str(row["table_id"] or "").strip())
            for row in lineage.filter(predicate).select("pipeline_role", "table_id").distinct().collect()
            if row["table_id"] and row["pipeline_role"]
        }
    )
    return (
        {table_id for _role, table_id in pairs},
        pairs,
        {"notebook_id": notebook_id, "notebook_name": notebook_name, "environment_name": environment_name},
        {"Notebook": notebook_name, "Environment": environment_name, "Linked datasets": len(pairs)},
    )


def _resolve_agreement_catalogue_scope(
    *,
    agreement: dict[str, Any] | None,
    environment_name: str,
    target: str,
    schema: str | None,
    spark_session: Any,
    runtime_context: dict[str, Any],
) -> tuple[set[str], None, dict[str, Any], dict[str, Any]]:
    """Resolve the selected agreement's registered table IDs."""
    agreement_id, agreement_name = widget_shared.resolve_agreement_details(agreement or {})
    if not agreement_id:
        raise ValueError("A saved agreement selection is required to view its catalogue inventory.")
    from pyspark.sql import functions as F

    contracts = read_lakehouse_table_core(
        "METADATA_DATA_CONTRACT",
        target=target,
        schema=schema,
        spark_session=spark_session,
        context=runtime_context,
    )
    table_ids = {
        str(row["metadata_table_key"])
        for row in contracts.filter(F.col("agreement_id") == agreement_id)
        .select("metadata_table_key")
        .distinct()
        .collect()
        if row["metadata_table_key"]
    }
    return (
        table_ids,
        None,
        {"agreement_id": agreement_id, "environment_name": environment_name},
        {"Agreement": agreement_name, "Environment": environment_name, "Linked datasets": len(table_ids)},
    )


def _resolve_explore_catalogue_scope(
    *, inventory_rows: list[dict[str, Any]], environment_name: str
) -> tuple[set[str], None, dict[str, Any], dict[str, Any]]:
    """Resolve every catalogued table in the current environment."""
    table_ids = {str(row["table_id"]) for row in inventory_rows}
    return (
        table_ids,
        None,
        {"environment_name": environment_name},
        {"Environment": environment_name, "Datasets": len(table_ids)},
    )


def _reader_dataset_label(row: dict[str, Any], role: str | None = None) -> str:
    """Return a readable dataset label backed by normalized table identity."""
    labelled = dict(row)
    labelled["metadata_table_key"] = str(row.get("table_id") or "")
    return widget_shared.dataset_label(labelled, role)


def _select_reader_columns(frame: Any, preferred: list[str]) -> Any:
    """Select reader-facing columns while keeping technical IDs at the end."""
    return frame.select(*[name for name in preferred if name in frame.columns])


def _prepare_selected_guardrail_views(results, row_results, *, metadata_table_key: str) -> dict[str, Any]:
    """Prepare the selected dataset's latest persisted guardrail execution."""
    from pyspark.sql import functions as F

    scoped = results.filter(
        (F.col("metadata_table_key") == metadata_table_key)
        & F.col("run_id").isNotNull()
        & (F.trim(F.col("run_id")) != "")
    )
    latest = (
        scoped.select("run_id", "_committed_at")
        .distinct()
        .orderBy(F.col("_committed_at").desc_nulls_last(), F.col("run_id").desc())
        .limit(1)
        .collect()
    )
    selected_run_id = str(latest[0]["run_id"]) if latest else None
    selected_results = (
        scoped.filter(F.col("run_id") == selected_run_id)
        if selected_run_id is not None
        else scoped.limit(0)
    )
    actual = F.col("actual_value_json")
    guardrail_results = selected_results.select(
        "rule_type",
        F.col("column_name").alias("columns"),
        "status",
        "severity",
        F.get_json_object(actual, "$.failed_count").cast("long").alias("failed_rows"),
        F.get_json_object(actual, "$.failed_percent").cast("double").alias("failed_percent"),
        F.get_json_object(actual, "$.total_count").cast("long").alias("total_count"),
        "reason",
        "can_continue",
        "run_id",
    ).orderBy(
        F.when(F.lower(F.col("status")) == "failed", 0)
        .when(F.lower(F.col("status")) == "warning", 1)
        .otherwise(2),
        F.col("rule_type"),
        F.col("columns"),
    )
    selected_row_results = (
        row_results.filter(
            (F.col("metadata_table_key") == metadata_table_key)
            & (F.col("run_id") == selected_run_id)
        )
        if selected_run_id is not None
        else row_results.limit(0)
    )
    guardrail_row_results = selected_row_results.select(
        "rule_type",
        "row_identity",
        F.col("involved_columns_json").alias("involved_columns"),
        F.col("failed_values_json").alias("failed_values"),
        "failure_reason",
        "run_id",
    ).orderBy("row_identity", "rule_type", "failure_reason")
    return {
        "guardrail_results": guardrail_results,
        "guardrail_row_results": guardrail_row_results,
    }


def _build_catalogue_widget(
    *,
    title: str,
    description: str,
    selection_context: dict[str, Any],
    display_context: dict[str, Any],
    inventory_rows: list[dict[str, Any]],
    role_options: list[tuple[str | None, str]] | None,
    target: str,
    schema: str | None,
    spark_session: Any,
    runtime_context: dict[str, Any],
    empty_message: str,
) -> dict[str, Any]:
    """Build the normalized catalogue reader and human-facing Spark views."""
    widgets = widget_shared.require_ipywidgets()
    rows_by_table_id = {str(row["table_id"]): row for row in inventory_rows}
    roles = role_options or [(None, table_id) for table_id in sorted(rows_by_table_id)]
    options: list[tuple[str, str]] = []
    option_context: dict[str, tuple[str | None, str]] = {}
    for role, table_id in roles:
        row = rows_by_table_id.get(table_id)
        if row is None:
            continue
        value = f"{role or ''}\x1f{table_id}"
        options.append((_reader_dataset_label(row, role), value))
        option_context[value] = (role, table_id)
    options.sort(key=lambda item: (item[0].casefold(), item[1]))
    initial_table_id = next(iter(rows_by_table_id), "")
    initial_value = next((value for _label, value in options if value.endswith(f"\x1f{initial_table_id}")), None)

    search = widgets.Text(value="", placeholder="Search catalogues", **widget_shared.widget_common(widgets, "Search"))
    dataset = widgets.Dropdown(options=options, value=initial_value, **widget_shared.widget_common(widgets, "Dataset"))
    profile_column = widgets.Dropdown(options=[], **widget_shared.widget_common(widgets, "Profile column"))
    for control in (search, dataset, profile_column):
        control.layout = widgets.Layout(width="100%", height="auto", overflow="visible")

    selection_details = widgets.HTML(value="")
    status = widget_shared.status_message(widgets)
    controls = {"search": search, "dataset": dataset, "profile_id": profile_column}
    state: dict[str, Any] = {
        "get_selection": None,
        "get_views": None,
        "refresh": None,
        "_controls": controls,
        "error": None,
    }
    source_frames: dict[str, Any] = {}
    current_frames: dict[str, Any] = {}
    selected_profile_snapshot_id: str | None = None
    selected_profiled_at: Any = None
    last_dataset_value = str(dataset.value or "")
    filtering_options = False

    def get_selection() -> dict[str, Any]:
        role, table_id = option_context.get(str(dataset.value or ""), (None, ""))
        row = rows_by_table_id.get(table_id, {})
        return {
            **selection_context,
            "table_id": table_id or None,
            "metadata_table_key": table_id or None,
            "dataset_label": _reader_dataset_label(row, role) if row else None,
            "profile_snapshot_id": selected_profile_snapshot_id,
            "profiled_at": selected_profiled_at,
            "profile_id": profile_column.value,
            "pipeline_role": role,
            "store_type": row.get("store_type"),
            "layer": row.get("layer"),
            "schema_name": row.get("schema_name"),
            "table_name": row.get("table_name"),
        }

    def refresh_loaded_views() -> None:
        nonlocal selected_profile_snapshot_id, selected_profiled_at
        from pyspark.sql import functions as F

        _role, table_id = option_context.get(str(dataset.value or ""), (None, ""))
        catalogue_raw = source_frames["catalogue"].filter(F.col("table_id") == table_id)
        profile_for_table = source_frames["profile"].filter(F.col("table_id") == table_id)
        latest = (
            profile_for_table.filter(F.col("profiled_at").isNotNull())
            .select("profile_snapshot_id", "profiled_at")
            .distinct()
            .orderBy(F.col("profiled_at").desc(), F.col("profile_snapshot_id").desc())
            .limit(1)
            .collect()
        )
        selected_profile_snapshot_id = str(latest[0]["profile_snapshot_id"]) if latest else None
        selected_profiled_at = latest[0]["profiled_at"] if latest else None
        catalogue_columns = catalogue_raw.filter(F.col("metadata_level") == "column").select(
            "table_id", "column_id", "column_name"
        )

        if selected_profile_snapshot_id is None:
            profile_snapshot = profile_for_table.limit(0)
            profile_reader = profile_snapshot.withColumn("column_name", F.lit(None).cast("string"))
            frequency_snapshot = source_frames["frequency"].limit(0).withColumn(
                "column_name", F.lit(None).cast("string")
            )
            column_options: list[tuple[str, str]] = []
            frequency_profile_ids: set[str] = set()
        else:
            profile_snapshot = profile_for_table.filter(
                F.col("profile_snapshot_id") == selected_profile_snapshot_id
            )
            profile_reader = profile_snapshot.join(catalogue_columns, on=["table_id", "column_id"], how="left")
            column_options = sorted(
                (
                    (str(row["column_name"] or row["profile_id"]), str(row["profile_id"]))
                    for row in profile_reader.select("profile_id", "column_name").distinct().collect()
                ),
                key=lambda option: (option[0].casefold(), option[1]),
            )
            frequency_snapshot = (
                source_frames["frequency"]
                .filter(F.col("profile_snapshot_id") == selected_profile_snapshot_id)
                .join(
                    profile_snapshot.select("profile_id", "profile_snapshot_id", "table_id", "column_id"),
                    on=["profile_id", "profile_snapshot_id"],
                    how="inner",
                )
                .join(catalogue_columns, on=["table_id", "column_id"], how="left")
            )
            frequency_profile_ids = {
                str(row["profile_id"])
                for row in frequency_snapshot.select("profile_id").distinct().collect()
            }

        previous_profile_id = str(profile_column.value or "")
        profile_column.options = column_options
        profile_ids = [value for _label, value in column_options]
        preferred_profile_id = next((value for value in profile_ids if value in frequency_profile_ids), None)
        profile_column.value = (
            previous_profile_id
            if previous_profile_id in profile_ids
            else preferred_profile_id or (profile_ids[0] if profile_ids else None)
        )
        selected_profile_id = profile_column.value
        selected_frequency = (
            frequency_snapshot.filter(F.col("profile_id") == selected_profile_id)
            if selected_profile_id
            else frequency_snapshot.limit(0)
        )
        current_frames.update(
            {
                "catalogue": catalogue_raw,
                "profile": profile_reader,
                "frequency_snapshot": frequency_snapshot,
                "frequency": selected_frequency,
            }
        )
        state.update(get_selection())
        state["error"] = None if table_id else empty_message
        selection = get_selection()
        labels_by_profile_id = {value: label for label, value in profile_column.options}
        selection_details.value = (
            f"<b>Dataset:</b> {html.escape(str(selection['dataset_label'] or ''))}<br>"
            f"<b>Profile snapshot:</b> {html.escape(str(selection['profiled_at'] or ''))}<br>"
            f"<b>Profile column:</b> {html.escape(str(labels_by_profile_id.get(selection['profile_id'], '') or ''))}"
            if table_id
            else ""
        )
        status.value = (
            "No profile snapshot is available for this dataset."
            if table_id and selected_profile_snapshot_id is None
            else "Selection ready. Run get_views() in the next cell to load native Spark DataFrames."
            if table_id
            else empty_message
        )

    def get_views() -> dict[str, Any]:
        selection = get_selection()
        table_id = selection["table_id"]
        if not table_id:
            raise ValueError(empty_message)
        if not source_frames:
            for name, table_name in (
                ("catalogue", "METADATA_DATA_CATALOGUE"),
                ("profile", "METADATA_DATA_PROFILED"),
                ("frequency", "METADATA_DATA_PROFILED_FREQUENCY"),
                ("guardrail_results", "METADATA_GUARDRAIL_RESULTS"),
                ("guardrail_row_results", "METADATA_GUARDRAIL_ROW_RESULTS"),
            ):
                source_frames[name] = read_lakehouse_table_core(
                    table_name,
                    target=target,
                    schema=schema,
                    spark_session=spark_session,
                    context=runtime_context,
                )
            refresh_loaded_views()

        catalogue = _select_reader_columns(
            current_frames["catalogue"],
            [
                "metadata_level",
                "table_name",
                "column_name",
                "store_type",
                "layer",
                "schema_name",
                "first_profiled_at",
                "last_profiled_at",
                "is_active",
                "table_id",
                "column_id",
            ],
        )
        profile = _select_reader_columns(
            current_frames["profile"],
            [
                "column_name",
                "data_type",
                "row_count",
                "non_null_count",
                "null_count",
                "null_percent",
                "distinct_count",
                "distinct_percent",
                "mean_value",
                "stddev_value",
                "min_value",
                "percentile_25_value",
                "median_value",
                "percentile_75_value",
                "max_value",
                "profiled_at",
                "profile_id",
                "profile_snapshot_id",
                "column_id",
                "table_id",
            ],
        )
        frequency = _select_reader_columns(
            current_frames["frequency"],
            [
                "column_name",
                "value",
                "frequency_count",
                "frequency_percent",
                "frequency_rank",
                "profiled_row_count",
                "profiled_non_null_count",
                "profiled_at",
                "frequency_id",
                "profile_id",
                "profile_snapshot_id",
            ],
        )
        views = {
            "catalogue": catalogue.orderBy("metadata_level", "column_name"),
            "profile": profile.orderBy("column_name"),
            "frequency": frequency.orderBy("frequency_rank", "value"),
        }
        views.update(
            _prepare_selected_guardrail_views(
                source_frames["guardrail_results"],
                source_frames["guardrail_row_results"],
                metadata_table_key=table_id,
            )
        )
        return views

    def refresh(*_args: Any) -> None:
        nonlocal selected_profile_snapshot_id, selected_profiled_at
        _role, table_id = option_context.get(str(dataset.value or ""), (None, ""))
        if source_frames:
            refresh_loaded_views()
            return
        selected_profile_snapshot_id = None
        selected_profiled_at = None
        profile_column.options = []
        state.update(get_selection())
        state["error"] = None if table_id else empty_message
        selection = get_selection()
        selection_details.value = (
            f"<b>Dataset:</b> {html.escape(str(selection['dataset_label'] or ''))}<br>"
            "<b>Profile snapshot:</b> Load views to resolve<br>"
            "<b>Profile column:</b> Load views to resolve"
            if table_id
            else ""
        )
        status.value = (
            "Selection ready. Run get_views() in the next cell to load native Spark DataFrames."
            if table_id
            else empty_message
        )

    def refresh_frequency(*_args: Any) -> None:
        from pyspark.sql import functions as F

        frequency = current_frames.get("frequency_snapshot")
        if frequency is None:
            return
        profile_id = profile_column.value
        current_frames["frequency"] = (
            frequency.filter(F.col("profile_id") == profile_id)
            if profile_id
            else frequency.limit(0)
        )
        state.update(get_selection())

    def select_dataset(change: dict[str, Any]) -> None:
        nonlocal last_dataset_value
        selected = str(change.get("new") or "")
        if selected:
            last_dataset_value = selected
        if not filtering_options:
            refresh()

    def filter_options(*_args: Any) -> None:
        nonlocal filtering_options, last_dataset_value
        query = str(search.value or "").strip().casefold()
        filtered = [option for option in options if query in option[0].casefold()]
        filtered_values = [value for _label, value in filtered]
        filtering_options = True
        try:
            dataset.options = filtered
            dataset.value = (
                last_dataset_value
                if last_dataset_value in filtered_values
                else filtered_values[0]
                if filtered_values
                else None
            )
        finally:
            filtering_options = False
        if dataset.value:
            last_dataset_value = str(dataset.value)
        refresh()

    state.update({"get_selection": get_selection, "get_views": get_views, "refresh": refresh})
    refresh()
    dataset.observe(lambda change: select_dataset(change) if change.get("name") == "value" else None, names="value")
    profile_column.observe(
        lambda change: refresh_frequency() if change.get("name") == "value" else None,
        names="value",
    )
    search.observe(lambda change: filter_options() if change.get("name") == "value" else None, names="value")

    context_html = "<br>".join(
        f"<b>{html.escape(str(name))}:</b> {html.escape(str(value))}"
        for name, value in display_context.items()
        if value not in (None, "")
    )
    from IPython import display as ip

    context_section = widget_shared.form_section(widgets, title="Context", children=[widgets.HTML(value=context_html)])
    selection_section = widget_shared.form_section(
        widgets,
        title="Catalogue selection",
        children=[widget_shared.form_grid(widgets, [search, dataset, profile_column])],
    )
    selected_section = widget_shared.form_section(
        widgets,
        title="Selected catalogue",
        children=[selection_details, status],
    )
    ip.display(
        widget_shared.form_page(
            widgets,
            title=title,
            description=description,
            children=[context_section, selection_section, selected_section],
        )
    )
    return state


def widget_view_catalogue(
    *,
    mode: str,
    agreement: dict[str, Any] | None = None,
    spark_session=None,
    target: str = "metadata",
    schema: str | None = None,
    context=None,
):
    """Select catalogue evidence using an explicit workflow scope.

    Parameters
    ----------
    mode : {"pipeline", "agreement", "explore"}
        Explicit dataset-scope strategy. No mode is inferred from other inputs.
    agreement : dict, optional
        Agreement widget state containing the current saved agreement. Required
        only for ``mode="agreement"``.
    spark_session : object, optional
        Spark session override.
    target : str, default="metadata"
        Configured metadata FabricStore target.
    schema : str, optional
        Metadata lakehouse schema override.
    context : object, optional
        Explicit FabricOps context used for environment and runtime identity.

    Returns
    -------
    dict
        Common state with ``get_selection``, ``get_views``, and ``refresh``.
        ``get_views`` returns exactly ``catalogue``, ``profile``, ``frequency``,
        ``guardrail_results``, and ``guardrail_row_results`` Spark DataFrames.
        Catalogue and profile views expose readable asset/column fields first;
        frequency rows are enriched with ``column_name`` through the normalized
        ``profile_id`` relationship.

    Raises
    ------
    ValueError
        If ``mode`` is unsupported, pipeline notebook identity cannot be
        resolved, or agreement mode has no saved agreement selection.

    Notes
    -----
    Microsoft Fabric is the execution runtime. Pipeline mode derives its scope
    from current-notebook lineage, agreement mode derives it from registered
    contracts, and explore mode includes the current environment inventory.
    The widget reads the normalized catalogue/profile/frequency tables without
    changing their persisted schemas.

    Examples
    --------
    >>> view = widget_view_catalogue(mode="explore", spark_session=spark)
    >>> sorted(view["get_views"]())
    ['catalogue', 'frequency', 'guardrail_results', 'guardrail_row_results', 'profile']

    See Also
    --------
    widget_render_data_agreement

    """
    supported_modes = {"pipeline", "agreement", "explore"}
    if mode not in supported_modes:
        raise ValueError(f"mode must be one of {sorted(supported_modes)}; got {mode!r}.")

    config, environment_name, resolved = resolve_fabric_context(context=context)
    runtime_context = {"config": config, "env": environment_name, **resolved}
    if mode == "pipeline":
        scope = _resolve_pipeline_catalogue_scope(
            environment_name=environment_name,
            target=target,
            schema=schema,
            spark_session=spark_session,
            context=context,
            runtime_context=runtime_context,
        )
    elif mode == "agreement":
        scope = _resolve_agreement_catalogue_scope(
            agreement=agreement,
            environment_name=environment_name,
            target=target,
            schema=schema,
            spark_session=spark_session,
            runtime_context=runtime_context,
        )

    catalogue = read_lakehouse_table_core(
        "METADATA_DATA_CATALOGUE",
        target=target,
        schema=schema,
        spark_session=spark_session,
        context=runtime_context,
    )
    inventory_rows = _collect_catalogue_inventory(catalogue, environment_name)
    if mode == "explore":
        scope = _resolve_explore_catalogue_scope(
            inventory_rows=inventory_rows,
            environment_name=environment_name,
        )
    allowed_table_ids, role_options, selection_context, display_context = scope
    rows = [row for row in inventory_rows if row["table_id"] in allowed_table_ids]
    if mode == "agreement":
        display_context["Linked datasets"] = len({row["table_id"] for row in rows})

    presentation = {
        "pipeline": (
            "Pipeline Catalogue Viewer",
            "View data catalogues used by the current pipeline notebook",
            "No lineage catalogue inventory was found for this notebook.",
        ),
        "agreement": (
            "Agreement Catalogue Viewer",
            "View data catalogues linked to the selected data agreement",
            "This agreement has no linked catalogue inventory.",
        ),
        "explore": (
            "Data Catalogue Viewer",
            "Browse data catalogues available in the current environment",
            "The data catalogue has no datasets in the current environment.",
        ),
    }
    title, description, empty_message = presentation[mode]
    return _build_catalogue_widget(
        title=title,
        description=description,
        selection_context=selection_context,
        display_context=display_context,
        inventory_rows=rows,
        role_options=role_options,
        target=target,
        schema=schema,
        spark_session=spark_session,
        runtime_context=runtime_context,
        empty_message=empty_message,
    )
