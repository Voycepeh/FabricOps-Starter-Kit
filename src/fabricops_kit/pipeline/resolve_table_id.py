"""Public owner for deterministic physical table identity resolution."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import resolve_physical_table_identity


def resolve_table_id(*, store: str, schema: str | None = None, table_name: str) -> str:
    """Return the canonical table identity for configured physical coordinates.

    Parameters
    ----------
    store : str
        Configured FabricStore key.
    schema : str, optional
        Physical schema, or ``None`` when the configured store does not use one.
    table_name : str
        Physical table name.

    Returns
    -------
    str
        Deterministic canonical ``table_id``. The physical table and Catalogue
        record do not need to exist yet.

    Raises
    ------
    ValueError
        If the store, schema, table name, or configured store is invalid.

    Examples
    --------
    >>> table_id = resolve_table_id(
    ...     store="unified", schema="dbo", table_name="curated_orders"
    ... )

    See Also
    --------
    pipeline_write, pipeline_read

    """
    config, env, _context = resolve_fabric_context()
    identity = resolve_physical_table_identity(
        config, env, store=store, schema=schema, table_name=table_name
    )
    return str(identity["table_id"])
