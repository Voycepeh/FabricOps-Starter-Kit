"""Agreement-scoped catalogue selection widget."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import read_lakehouse_table_core
from fabricops_kit.widgets.shared import build_catalogue_widget, collect_catalogue_inventory
from fabricops_kit.widgets.shared import resolve_agreement_details


def widget_view_agreement_catalogue(*, agreement: dict[str, Any], spark_session=None, target: str = "metadata", schema: str | None = None, context=None):
    """Select agreement-linked catalogue metadata for native Fabric rendering.

    Parameters
    ----------
    agreement : dict
        Agreement widget state containing the current saved agreement.
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
        State mapping with ``get_selection``, ``get_views``, and ``refresh``.
        ``get_views`` returns a named mapping containing ``catalogue``,
        ``profile``, and ``frequency`` Spark DataFrames and does not render
        them.

    Raises
    ------
    ValueError
        If the agreement state has no saved agreement identity.

    Notes
    -----
    Inventory follows agreement to registered data contracts to catalogue
    datasets in the current environment. The compact parent profile defaults
    to the latest ``profiled_at`` snapshot. Normalized child frequencies are
    limited to the selected column and matched to that snapshot through both
    ``metadata_column_key`` and ``profiled_at``.

    Examples
    --------
    >>> view = widget_view_agreement_catalogue(agreement=agreement_widget, spark_session=spark)
    >>> views = view["get_views"]()
    >>> views["catalogue"], views["profile"], views["frequency"]

    """
    agreement_id, agreement_name = resolve_agreement_details(agreement)
    if not agreement_id:
        raise ValueError("A saved agreement selection is required to view its catalogue inventory.")
    config, environment_name, resolved = resolve_fabric_context(context=context)
    runtime_context = {"config": config, "env": environment_name, **resolved}
    from pyspark.sql import functions as F
    contracts = read_lakehouse_table_core("METADATA_DATA_CONTRACT", target=target, schema=schema, spark_session=spark_session, context=runtime_context)
    keys = sorted({str(row["metadata_table_key"]) for row in contracts.filter(F.col("agreement_id") == agreement_id).select("metadata_table_key").distinct().collect() if row["metadata_table_key"]})
    catalogue = read_lakehouse_table_core("METADATA_DATA_CATALOGUE", target=target, schema=schema, spark_session=spark_session, context=runtime_context)
    rows = [row for row in collect_catalogue_inventory(catalogue, environment_name) if row["metadata_table_key"] in set(keys)]
    return build_catalogue_widget(
        heading="Agreement catalogue",
        selection_context={"agreement_id": agreement_id, "environment_name": environment_name},
        display_context={"Agreement": agreement_name, "Environment": environment_name, "Linked datasets": len({row['metadata_table_key'] for row in rows})},
        inventory_rows=rows, role_options=None, target=target, schema=schema, spark_session=spark_session,
        runtime_context=runtime_context, empty_message="This agreement has no linked catalogue inventory.",
    )
