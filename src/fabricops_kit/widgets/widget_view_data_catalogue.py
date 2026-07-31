"""General data catalogue selection widget."""

from __future__ import annotations

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import read_lakehouse_table_core
from fabricops_kit.widgets.shared import build_catalogue_widget, collect_catalogue_inventory


def widget_view_data_catalogue(*, spark_session=None, target: str = "metadata", schema: str | None = None, context=None):
    """Select any catalogued dataset for native Fabric rendering.

    Parameters
    ----------
    spark_session : object, optional
        Spark session override.
    target : str, default="metadata"
        Configured metadata FabricStore target.
    schema : str, optional
        Metadata lakehouse schema override.
    context : object, optional
        Active FabricOps context override.

    Returns
    -------
    dict
        Common catalogue state mapping. ``get_views`` returns exactly the
        selected catalogue and profile Spark DataFrames without rendering.

    Notes
    -----
    Inventory is built only from the current environment's data catalogue.

    Examples
    --------
    >>> view = widget_view_data_catalogue(spark_session=spark)
    >>> catalogue_df, profile_df = view["get_views"]()

    """
    config, environment_name, resolved = resolve_fabric_context(context=context)
    runtime_context = {"config": config, "env": environment_name, **resolved}
    catalogue = read_lakehouse_table_core("METADATA_DATA_CATALOGUE", target=target, schema=schema, spark_session=spark_session, context=runtime_context)
    rows = collect_catalogue_inventory(catalogue, environment_name)
    return build_catalogue_widget(
        heading="Data catalogue", context_values={"environment_name": environment_name, "Environment": environment_name, "Dataset count": len({row['metadata_table_key'] for row in rows})},
        inventory_rows=rows, role_options=None, target=target, schema=schema, spark_session=spark_session,
        runtime_context=runtime_context, empty_message="The data catalogue has no datasets in the current environment.",
    )
