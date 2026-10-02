"""Create a native Microsoft Fabric Data Agent for one governed table."""

from typing import Any, Callable, Mapping

from .shared import FabricResponse, configured_context, consumer_context, default_token_provider, http_request, provision_data_agent


def create_data_agent(
    table_id: str, target_workspace_id: str, display_name: str, *,
    description: str = "FabricOps governed single-table Data Agent",
    config: Any = None, context: Mapping[str, Any] | None = None, spark_session: Any = None,
    token_provider: Callable[[], str] = default_token_provider,
    transport: Callable[[str, str, Mapping[str, Any] | None, str], FabricResponse] = http_request,
) -> dict[str, Any]:
    """Create and configure a native Data Agent from governed Production metadata.

    Parameters
    ----------
    table_id : str
        Canonical FabricOps identity for one activated Production table.
    target_workspace_id : str
        Fabric workspace in which to create the Data Agent.
    display_name : str
        Data Agent display name.
    description : str, optional
        Data Agent item description.
    config : Any, optional
        FabricOps configuration. The configured notebook value is used when omitted.
    context : mapping, optional
        FabricOps runtime context used to resolve configuration and Spark.
    spark_session : Any, optional
        Explicit Spark session used to read metadata.
    token_provider : callable, optional
        Token provider integration boundary. Defaults to Fabric ``notebookutils``.
    transport : callable, optional
        HTTP integration boundary, primarily for isolated testing.

    Returns
    -------
    dict[str, Any]
        Created agent and datasource identities, workspace, display name, source
        ``table_id``, and the final useful configuration status.

    Raises
    ------
    ValueError
        If inputs or governed Production source metadata are invalid.
    FabricDataAgentError
        If authentication, permissions, a Fabric REST request, response validation,
        or long-running operation fails. Fabric error details are retained.

    Notes
    -----
    This Preview API requires a supported Fabric capacity, access to the Production
    Lakehouse or Warehouse, and permission to create and configure Data Agents in
    the target workspace. It creates a staging datasource, selects one table, and
    applies datasource and agent instructions. It does not publish the agent.

    Examples
    --------
    >>> result = create_data_agent(
    ...     "lakehouse||production||dbo||orders",
    ...     target_workspace_id="00000000-0000-0000-0000-000000000000",
    ...     display_name="Governed orders",
    ... )
    >>> result["status"]
    'configured'

    See Also
    --------
    build_consumer_context
    render_data_agent_instructions

    """
    if not str(target_workspace_id or "").strip() or not str(display_name or "").strip():
        raise ValueError("target_workspace_id and display_name must be non-empty strings.")
    resolved_config, resolved_spark = configured_context(config, context)
    governed = consumer_context(resolved_config, table_id, spark_session=spark_session or resolved_spark)
    return provision_data_agent(
        governed, target_workspace_id=target_workspace_id.strip(), display_name=display_name.strip(),
        description=str(description or "").strip(), token_provider=token_provider, transport=transport,
    )


__all__ = ["create_data_agent"]
