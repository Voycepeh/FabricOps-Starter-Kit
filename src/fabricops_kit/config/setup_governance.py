"""Public initialization for governance and independent registered-workspace IO."""
from .shared import resolve_governed_workspace, get_default_fabric_context


def setup_governance(*, target_workspace_id: str | None = None, spark_session=None):
    """Initialize registered workspace configuration without starting a pipeline.

    Governance administrators may select a registered engineering workspace from
    the Governance Workspace to author contracts and activate its pipelines.
    Otherwise the runtime workspace is authoritative. No deployment environment
    or resource override is accepted. This function does not create metadata or
    grant permissions. Independent public IO can also use an explicit context.

    Parameters
    ----------
    target_workspace_id : str, optional
        Registered target workspace; selectable only from the pinned Governance Workspace.
    spark_session : object, optional
        Fabric Spark session; otherwise the active session is used.

    Returns
    -------
    dict
        Resolved, context-local FrameworkConfig, deployment environment and runtime identity.

    """
    try:
        active = get_default_fabric_context()
    except RuntimeError:
        active = {}
    if active.get("_registry_pipeline"):
        raise RuntimeError("Finalize the current pipeline before initializing Governance or independent workspace IO.")
    return resolve_governed_workspace(target_workspace_id=target_workspace_id, spark_session=spark_session)
