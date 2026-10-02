"""Build deterministic context for a governed Production table."""

from typing import Any, Mapping

from .shared import configured_context, consumer_context


def build_consumer_context(
    table_id: str, *, config: Any = None, context: Mapping[str, Any] | None = None,
    spark_session: Any = None,
) -> dict[str, Any]:
    """Build deterministic consumer context for one governed Production table.

    Parameters
    ----------
    table_id : str
        Canonical FabricOps table identity.
    config : Any, optional
        FabricOps configuration. The configured notebook value is used when omitted.
    context : mapping, optional
        FabricOps runtime context used to resolve configuration and Spark.
    spark_session : Any, optional
        Explicit Spark session used to read metadata.

    Returns
    -------
    dict[str, Any]
        Stable, JSON-safe table, contract, source, column, and rule context. Profile
        samples, credentials, access tokens, and raw sensitive values are excluded.

    Raises
    ------
    ValueError
        If the table is missing, is not a Production asset, has no active Data
        Contract, or its configured source is unsupported or incomplete.
    RuntimeError
        If authoritative metadata records conflict.

    Notes
    -----
    This Preview function reads ``METADATA_DATA_CATALOGUE`` and the active frozen
    ``METADATA_DATA_CONTRACT`` in the configured Metadata Lakehouse. It does not
    call AI or persist a second copy of the governed metadata.

    Examples
    --------
    >>> context = build_consumer_context("lakehouse||production||dbo||orders")
    >>> context["environment"]
    'prod'

    See Also
    --------
    create_data_agent
    render_data_agent_instructions

    """
    resolved_config, resolved_spark = configured_context(config, context)
    return consumer_context(resolved_config, table_id, spark_session=spark_session or resolved_spark)


__all__ = ["build_consumer_context"]
