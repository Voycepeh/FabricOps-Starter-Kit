"""Read-only persisted metadata explorer widget."""

from __future__ import annotations

import html
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table
import fabricops_kit.widgets.shared as widget_shared


_SCOPES = ("Table", "Data Agreement", "Data Steward", "Pipeline Notebook")


def _read_explorer_frames(*, names, store, schema, spark_session, runtime_context):
    """Read requested canonical metadata tables through configured metadata routing."""
    return {
        key: read_lakehouse_table(
            table_name, store=store, schema=schema,
            spark_session=spark_session, context=runtime_context,
        )
        for key, table_name in names.items()
    }


def _scope_options(scope: str, *, environment_name: str, frames: dict[str, Any]):
    """Collect a small, readable selector inventory for one explorer scope."""
    from pyspark.sql import functions as F

    contracts = frames["contracts"].filter(F.col("environment_name") == environment_name)
    if scope == "Table":
        rows = frames["catalogue"].filter(
            (F.col("environment_name") == environment_name)
            & (F.col("metadata_level") == "table") & F.col("is_active")
        ).select("table_id", "store_type", "layer", "schema_name", "table_name").distinct().collect()
        return sorted((widget_shared.dataset_label(row.asDict(recursive=True)), str(row["table_id"])) for row in rows)
    if scope == "Data Agreement":
        rows = frames["agreements"].join(
            contracts.select("agreement_id", "agreement_version").distinct(),
            ["agreement_id", "agreement_version"], "inner",
        ).select("agreement_id", "agreement_name").distinct().collect()
        return sorted((f"{row['agreement_name']} ({row['agreement_id']})", str(row["agreement_id"])) for row in rows)
    if scope == "Data Steward":
        agreement_stewards = frames["agreements"].join(
            contracts.select("agreement_id", "agreement_version").distinct(),
            ["agreement_id", "agreement_version"], "inner",
        ).select(F.col("provider_steward_id").alias("steward_id")).unionByName(
            frames["agreements"].join(
                contracts.select("agreement_id", "agreement_version").distinct(),
                ["agreement_id", "agreement_version"], "inner",
            ).select(F.col("recipient_steward_id").alias("steward_id"))
        ).distinct()
        rows = frames["stewards"].join(agreement_stewards, "steward_id", "inner").select(
            "steward_id", "steward_name"
        ).distinct().collect()
        return sorted((f"{row['steward_name']} ({row['steward_id']})", str(row["steward_id"])) for row in rows)
    rows = frames["lineage"].filter(F.col("environment_name") == environment_name).select(
        "_notebook_id", "_notebook_name"
    ).distinct().collect()
    return sorted((str(row["_notebook_name"] or row["_notebook_id"]), str(row["_notebook_id"] or row["_notebook_name"])) for row in rows)


def widget_metadata_explorer(
    *,
    spark_session=None,
    store: str = "metadata",
    schema: str | None = None,
    context=None,
):
    """Explore persisted FabricOps metadata through deliberately shaped views.

    Parameters
    ----------
    spark_session : object, optional
        Spark session override.
    store : str, default="metadata"
        Configured metadata FabricStore key.
    schema : str, optional
        Metadata lakehouse schema override.
    context : object, optional
        Explicit FabricOps context. Its current environment is used for every
        selector and returned view.

    Returns
    -------
    dict
        Widget state with ``get_selection``, ``get_views``, and ``refresh``.
        ``get_views`` returns native Spark DataFrames named ``assets``,
        ``columns``, ``governance``, ``execution``, ``frequency``, and
        ``access``. Each preserves its documented metadata grain.

    Raises
    ------
    ValueError
        If no entity is selected or an unsupported scope is requested.

    Notes
    -----
    This read-only Microsoft Fabric widget routes all reads through the
    metadata store configured by ``00_env_config``. It deliberately uses only
    the current resolved environment because FabricOps does not provide a
    cross-environment metadata-store routing contract.

    Examples
    --------
    >>> explorer = widget_metadata_explorer(store="metadata", spark_session=spark)
    >>> views = explorer["get_views"]()
    >>> sorted(views)
    ['access', 'assets', 'columns', 'execution', 'frequency', 'governance']

    See Also
    --------
    widget_view_catalogue

    """
    from IPython import display as ip

    config, environment_name, resolved = resolve_fabric_context(context=context)
    runtime_context = {"config": config, "env": environment_name, **resolved}
    selector_frames = _read_explorer_frames(
        names={
            "catalogue": "METADATA_DATA_CATALOGUE", "contracts": "METADATA_DATA_CONTRACT",
            "agreements": "METADATA_DATA_AGREEMENT", "stewards": "METADATA_DATA_STEWARD",
            "lineage": "METADATA_DATA_LINEAGE",
        }, store=store, schema=schema, spark_session=spark_session, runtime_context=runtime_context,
    )
    widgets = widget_shared.require_ipywidgets()
    scope = widgets.Dropdown(options=list(_SCOPES), value="Table", **widget_shared.widget_common(widgets, "Explore by"))
    search = widgets.Text(value="", placeholder="Search metadata scope", **widget_shared.widget_common(widgets, "Search"))
    entity = widgets.Dropdown(options=[], **widget_shared.widget_common(widgets, "Selection"))
    summary = widgets.HTML(value="")
    status = widget_shared.status_message(widgets)
    all_options: list[tuple[str, str]] = []
    state: dict[str, Any] = {"get_selection": None, "get_views": None, "refresh": None,
                             "_controls": {"scope": scope, "search": search, "entity": entity}}

    def get_selection():
        selected_id = str(entity.value or "")
        table_ids = widget_shared.metadata_scope_table_ids(
            scope.value, selected_id, environment_name=environment_name, frames=selector_frames,
        ) if selected_id else []
        return {"environment_name": environment_name, "scope": scope.value,
                "selected_id": selected_id or None, "table_ids": table_ids}

    def get_views():
        selection = get_selection()
        if not selection["selected_id"]:
            raise ValueError("Select an entity before loading metadata views.")
        frames = dict(selector_frames)
        frames.update(_read_explorer_frames(
            names={
                "profiles": "METADATA_DATA_PROFILED", "frequency": "METADATA_DATA_PROFILED_FREQUENCY",
                "enrichments": "METADATA_ENRICHMENT", "guardrails": "METADATA_GUARDRAIL",
                "guardrail_results": "METADATA_GUARDRAIL_RESULTS",
                "observations": "METADATA_SOURCE_OBSERVATION", "access": "METADATA_DATA_ACCESS",
            }, store=store, schema=schema, spark_session=spark_session, runtime_context=runtime_context,
        ))
        return widget_shared.metadata_explorer_views(
            selection["table_ids"], environment_name=environment_name, frames=frames,
        )

    def filter_options(*_args):
        query = str(search.value or "").casefold().strip()
        filtered = [option for option in all_options if query in option[0].casefold()]
        entity.options = filtered
        entity.value = filtered[0][1] if filtered else None
        refresh_summary()

    def refresh_scope(*_args):
        nonlocal all_options
        all_options = _scope_options(scope.value, environment_name=environment_name, frames=selector_frames)
        filter_options()

    def refresh_summary(*_args):
        selection = get_selection()
        selected_label = next((label for label, value in entity.options if value == entity.value), "None")
        summary.value = (
            f"<b>Environment:</b> {html.escape(environment_name)}<br>"
            f"<b>Selected {html.escape(scope.value)}:</b> {html.escape(selected_label)}<br>"
            f"<b>Matched governed tables:</b> {len(selection['table_ids'])}"
        )
        status.value = "Selection ready. Call get_views() to load only the Spark DataFrames you need."

    state.update({"get_selection": get_selection, "get_views": get_views, "refresh": refresh_scope})
    scope.observe(refresh_scope, names="value")
    search.observe(filter_options, names="value")
    entity.observe(refresh_summary, names="value")
    refresh_scope()
    controls = widget_shared.form_section(
        widgets, title="Metadata scope",
        children=[widget_shared.form_grid(widgets, [scope, search, entity])],
    )
    selected = widget_shared.form_section(widgets, title="Selected scope", children=[summary, status])
    ip.display(widget_shared.form_page(
        widgets, title="Metadata Explorer",
        description="Inspect persisted FabricOps metadata without changing governance or pipeline state.",
        children=[controls, selected],
    ))
    return state
