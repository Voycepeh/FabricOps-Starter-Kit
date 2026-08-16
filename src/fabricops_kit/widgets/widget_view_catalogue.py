"""Mode-scoped data catalogue selection widget."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context, resolve_runtime_context
from fabricops_kit.io.shared import read_lakehouse_table_core
from fabricops_kit.widgets.shared import (
    build_catalogue_widget,
    collect_catalogue_inventory,
    resolve_agreement_details,
)


def _resolve_pipeline_catalogue_scope(
    *,
    environment_name: str,
    target: str,
    schema: str | None,
    spark_session: Any,
    context: Any,
    runtime_context: dict[str, Any],
) -> tuple[set[str], list[tuple[str, str]], dict[str, Any], dict[str, Any]]:
    """Resolve notebook-lineage dataset keys and role choices."""
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
    predicate = (F.col("notebook_id") == notebook_id) & (F.col("environment_name") == environment_name)
    if workspace_id:
        predicate &= F.col("workspace_id") == workspace_id
    pairs = sorted(
        {
            (str(row["profile_role"] or "").strip().title(), str(row["metadata_table_key"] or "").strip())
            for row in lineage.filter(predicate).select("profile_role", "metadata_table_key").distinct().collect()
            if row["metadata_table_key"] and row["profile_role"]
        }
    )
    return (
        {key for _role, key in pairs},
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
    """Resolve the selected agreement's registered dataset keys."""
    agreement_id, agreement_name = resolve_agreement_details(agreement or {})
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
    keys = {
        str(row["metadata_table_key"])
        for row in contracts.filter(F.col("agreement_id") == agreement_id)
        .select("metadata_table_key")
        .distinct()
        .collect()
        if row["metadata_table_key"]
    }
    return (
        keys,
        None,
        {"agreement_id": agreement_id, "environment_name": environment_name},
        {"Agreement": agreement_name, "Environment": environment_name, "Linked datasets": len(keys)},
    )


def _resolve_explore_catalogue_scope(
    *,
    inventory_rows: list[dict[str, Any]],
    environment_name: str,
) -> tuple[set[str], None, dict[str, Any], dict[str, Any]]:
    """Resolve every catalogued dataset in the current environment."""
    keys = {str(row["metadata_table_key"]) for row in inventory_rows}
    return (
        keys,
        None,
        {"environment_name": environment_name},
        {
            "Environment": environment_name,
            "Datasets": len(keys),
        },
    )


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
        ``guardrail_results``, and ``guardrail_row_results`` Spark DataFrames,
        all scoped to the selected ``metadata_table_key``.

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
    All modes then use one shared selector and evidence-loading path.

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
    inventory_rows = collect_catalogue_inventory(catalogue, environment_name)
    if mode == "explore":
        scope = _resolve_explore_catalogue_scope(
            inventory_rows=inventory_rows,
            environment_name=environment_name,
        )
    allowed_keys, role_options, selection_context, display_context = scope
    rows = [row for row in inventory_rows if row["metadata_table_key"] in allowed_keys]
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
    return build_catalogue_widget(
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
