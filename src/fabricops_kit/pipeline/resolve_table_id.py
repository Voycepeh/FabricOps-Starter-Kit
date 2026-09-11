"""Public owner for deterministic physical table identity resolution."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import resolve_physical_table_identity


def resolve_table_id(*, target: str, schema: str | None = None, table_name: str) -> str:
    """Return the canonical table identity for configured physical coordinates.

    Parameters
    ----------
    target : str
        Configured FabricStore target key.
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
        If the target, schema, table name, or configured store is invalid.

    Examples
    --------
    >>> table_id = resolve_table_id(
    ...     target="unified", schema="dbo", table_name="curated_orders"
    ... )

    See Also
    --------
    write_pipeline_prep, read_pipeline_prep

    """
    config, env, _context = resolve_fabric_context()
    identity = resolve_physical_table_identity(
        config, env, target=target, schema=schema, table_name=table_name
    )
    return str(identity["table_id"])
