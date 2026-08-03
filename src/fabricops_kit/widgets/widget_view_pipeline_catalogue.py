"""Pipeline-scoped catalogue selection widget."""

from __future__ import annotations

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import read_lakehouse_table_core
from fabricops_kit.widgets.shared import build_catalogue_widget, collect_catalogue_inventory


def widget_view_pipeline_catalogue(*, spark_session=None, target: str = "metadata", schema: str | None = None, context=None):
    """Select notebook-lineage catalogue metadata for native Fabric rendering.

    Parameters
    ----------
    spark_session : object, optional
        Spark session override.
    target : str, default="metadata"
        Configured metadata FabricStore target.
    schema : str, optional
        Metadata lakehouse schema override.
    context : object, optional
        Active FabricOps context used to resolve stable notebook identity.

    Returns
    -------
    dict
        Common catalogue state mapping. ``get_views`` returns a named mapping
        containing the selected ``catalogue``, compact ``profile``, and
        normalized ``frequency`` Spark DataFrames without rendering.

    Raises
    ------
    ValueError
        If stable notebook identity is unavailable.

    Notes
    -----
    The compact profile defaults to the latest ``profiled_at`` snapshot.
    Frequencies are limited to the selected profile column and matched through
    both ``metadata_column_key`` and ``profiled_at`` so historical snapshots
    cannot be mixed.

    Examples
    --------
    >>> view = widget_view_pipeline_catalogue(spark_session=spark)
    >>> views = view["get_views"]()
    >>> views["catalogue"], views["profile"], views["frequency"]

    """
    config, environment_name, resolved = resolve_fabric_context(context=context)
    runtime = resolved.get("runtime_metadata") or {}
    notebook_id = str(resolved.get("notebook_id") or runtime.get("notebook_id") or "").strip()
    notebook_name = str(resolved.get("notebook_name") or runtime.get("notebook_name") or notebook_id).strip()
    workspace_id = str(resolved.get("workspace_id") or runtime.get("workspace_id") or "").strip()
    if not notebook_id:
        raise ValueError("Current notebook_id is required to resolve pipeline catalogue inventory.")
    runtime_context = {"config": config, "env": environment_name, **resolved}
    from pyspark.sql import functions as F
    lineage = read_lakehouse_table_core("METADATA_DATA_LINEAGE", target=target, schema=schema, spark_session=spark_session, context=runtime_context)
    predicate = (F.col("notebook_id") == notebook_id) & (F.col("environment_name") == environment_name)
    if workspace_id:
        predicate = predicate & (F.col("workspace_id") == workspace_id)
    pairs = sorted({
        (str(row["profile_role"] or "").strip().title(), str(row["metadata_table_key"] or "").strip())
        for row in lineage.filter(predicate).select("profile_role", "metadata_table_key").distinct().collect()
        if row["metadata_table_key"] and row["profile_role"]
    })
    catalogue = read_lakehouse_table_core("METADATA_DATA_CATALOGUE", target=target, schema=schema, spark_session=spark_session, context=runtime_context)
    allowed = {key for _role, key in pairs}
    rows = [row for row in collect_catalogue_inventory(catalogue, environment_name) if row["metadata_table_key"] in allowed]
    return build_catalogue_widget(
        heading="Pipeline catalogue",
        selection_context={"notebook_id": notebook_id, "notebook_name": notebook_name, "environment_name": environment_name},
        display_context={"Notebook": notebook_name, "Environment": environment_name, "Linked datasets": len(pairs)},
        inventory_rows=rows, role_options=pairs, target=target, schema=schema, spark_session=spark_session,
        runtime_context=runtime_context, empty_message="No lineage catalogue inventory was found for this notebook.",
    )
