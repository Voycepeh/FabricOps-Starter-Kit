"""Public widget entrypoint for browsing metadata catalogue rows."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import read_lakehouse_table_core
from fabricops_kit.widgets.shared import render_searchable_selector, require_ipywidgets, widget_common


def widget_browse_metadata_catalogue(
    *,
    agreement: dict | None = None,
    agreement_id: str | None = None,
    contract_version: str | None = None,
    target: str = "metadata",
    schema: str | None = None,
    metadata_table: str = "METADATA_DATA_CATALOGUE",
    spark_session=None,
    context=None,
):
    """Render a searchable metadata catalogue browser.

    Parameters
    ----------
    agreement : dict, optional
        Agreement context used as a fallback for agreement and contract filters.
    agreement_id : str, optional
        Explicit agreement identifier. Takes precedence over ``agreement``.
    contract_version : str, optional
        Explicit contract version. Takes precedence over ``agreement``.
    target : str, default="metadata"
        Logical FabricStore target used to read the catalogue table.
    schema : str, optional
        Optional metadata lakehouse schema override.
    metadata_table : str, default="METADATA_DATA_CATALOGUE"
        Metadata catalogue table to read.
    spark_session : object, optional
        Spark session override.
    context : object, optional
        Active FabricOps context override.

    Returns
    -------
    dict
        Mutable widget state. The ``dataframe`` key contains the currently
        filtered Spark DataFrame and updates when selections change.

    """
    config, env, resolved_context = resolve_fabric_context(context=context)
    widgets = require_ipywidgets()
    from IPython import display as ip

    metadata_catalogue = read_lakehouse_table_core(
        metadata_table,
        target=target,
        schema=schema,
        spark_session=spark_session,
        context={"config": config, "env": env, **(resolved_context or {})},
    )
    store_targets = _configured_fabric_store_targets({"config": config, "env": env, **(resolved_context or {})})
    store_dropdown = widgets.Dropdown(
        options=store_targets,
        value=store_targets[0] if store_targets else None,
        **widget_common(widgets, "FabricStore target"),
    )
    table_selector = render_searchable_selector(
        widgets=widgets,
        label="Metadata table",
        rows=[],
        label_fn=lambda row: str(row["table_name"]),
        value_fn=lambda row: str(row["table_name"]),
        search_fields=["table_name"],
        empty_label="No catalogue tables" if not store_targets else None,
    )
    status = widgets.HTML()
    state: dict[str, Any] = {"dataframe": metadata_catalogue.limit(0), "fabric_store_target": "", "table_name": ""}

    def get_dataframe():
        """Return the currently selected filtered catalogue DataFrame."""
        return state["dataframe"]

    state["get_dataframe"] = get_dataframe

    resolved_agreement_id = str(agreement_id if agreement_id is not None else (agreement or {}).get("agreement_id", "")).strip()
    resolved_contract_version = str(
        contract_version
        if contract_version is not None
        else (agreement or {}).get("agreement_contract_version") or (agreement or {}).get("contract_version") or ""
    ).strip()

    def refresh_tables(*_: Any) -> None:
        selected_store = str(store_dropdown.value or "").strip().lower()
        names = _catalogue_table_names_for_target(metadata_catalogue, selected_store) if selected_store else []
        rows = [{"table_name": name} for name in names]
        table_selector["selector"].refresh_rows(rows, selected=names[0] if names else "")
        refresh_dataframe()

    def refresh_dataframe(*_: Any) -> None:
        selected_store = str(store_dropdown.value or "").strip().lower()
        selected_table = str(table_selector["selector"].value or "").strip()
        state["fabric_store_target"] = selected_store
        state["table_name"] = selected_table
        if not selected_store or not selected_table:
            state["dataframe"] = metadata_catalogue.limit(0)
            status.value = "No configured FabricStore targets." if not selected_store else "No catalogue tables for selected FabricStore target."
            return
        state["dataframe"] = _filter_metadata_catalogue(
            metadata_catalogue,
            fabric_store_target=selected_store,
            table_name=selected_table,
            agreement_id=resolved_agreement_id,
            contract_version=resolved_contract_version,
        )
        status.value = f"Selected {selected_store} / {selected_table}."

    store_dropdown.observe(refresh_tables, names="value")
    table_selector["selector"].observe(refresh_dataframe, names="value")
    refresh_tables()
    state["_controls"] = {"fabric_store_target": store_dropdown, "metadata_table": table_selector, "status": status}
    ip.display(widgets.VBox([widgets.HTML("<h3>Browse metadata catalogue</h3>"), store_dropdown, table_selector["container"], status]))
    return state


def _configured_fabric_store_targets(context) -> list[str]:
    """Return configured logical FabricStore keys for the active environment."""
    config, env, _resolved = resolve_fabric_context(context=context)
    paths = getattr(getattr(config, "path_config", None), "paths", None)
    if paths is None and isinstance(config, Mapping):
        paths = config.get("path_config", {}).get("paths") if isinstance(config.get("path_config"), Mapping) else config.get("paths")
    env_paths = (paths or {}).get(env, {}) if isinstance(paths, Mapping) else {}
    return sorted({str(key).strip().lower() for key in env_paths if str(key).strip()})


def _catalogue_table_names_for_target(metadata_catalogue, fabric_store_target: str) -> list[str]:
    """Return distinct catalogue table names for a logical FabricStore target."""
    from pyspark.sql import functions as F

    target = str(fabric_store_target or "").strip().lower()
    if not target:
        return []
    rows = (
        metadata_catalogue.filter(F.col("fabric_store_target") == target)
        .select("table_name")
        .distinct()
        .collect()
    )
    return sorted({str(row["table_name"]).strip() for row in rows if str(row["table_name"] or "").strip()})


def _filter_metadata_catalogue(
    metadata_catalogue,
    *,
    fabric_store_target: str,
    table_name: str,
    agreement_id: str = "",
    contract_version: str = "",
):
    """Filter catalogue rows by store, table, and optional agreement context."""
    from pyspark.sql import functions as F

    filtered = metadata_catalogue.filter(F.col("fabric_store_target") == str(fabric_store_target).strip().lower())
    filtered = filtered.filter(F.col("table_name") == str(table_name).strip())
    if str(agreement_id or "").strip() and "agreement_id" in filtered.columns:
        filtered = filtered.filter(F.col("agreement_id") == str(agreement_id).strip())
    if str(contract_version or "").strip() and "contract_version" in filtered.columns:
        filtered = filtered.filter(F.col("contract_version") == str(contract_version).strip())
    return filtered
