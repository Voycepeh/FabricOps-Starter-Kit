"""Explicit allocation of a permanent pipeline identity."""

from fabricops_kit.pipeline.shared import administer_pipeline_registration


def create_pipeline(*, config_workspace_id=None):
    """Generate and register a UUIDv4 for an independent, unregistered notebook.

    Call in an independent notebook copy and save the returned UUID as
    PIPELINE_ID. An already registered notebook fails rather than changing identity.
    This administrative write grants no activation or Live permission.

    Parameters
    ----------
    config_workspace_id : str | None, optional
        Workspace hosting 00_env_config; defaults to the caller workspace.

    Returns
    -------
    str
        Permanent UUIDv4 registered to the caller notebook in its environment.

    Raises
    ------
    ValueError
        If the caller is already registered or Fabric notebook identity is missing.
    RuntimeError
        If registration cannot be confirmed; rerun setup_pipeline to recover it.

    Examples
    --------
    >>> PIPELINE_ID = create_pipeline()
    >>> pipeline = setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode="Test")

    """
    return administer_pipeline_registration(config_workspace_id=config_workspace_id)
