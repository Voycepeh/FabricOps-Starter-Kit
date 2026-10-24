"""Explicit rebinding after notebook replacement."""

from fabricops_kit.pipeline.shared import administer_pipeline_registration


def rebind_pipeline(pipeline_id, *, previous_workspace_id, previous_notebook_id, config_workspace_id=None):
    """Move an existing environment binding to the caller after notebook reupload.

    Supply the exact previous workspace and notebook IDs from the registry.
    Stale expectations and a caller already owned by another pipeline fail.
    Approved releases remain immutable. Rerun Test and approve a new release
    when processing configuration or physical data destinations differ.

    Parameters
    ----------
    pipeline_id : str
        Persisted permanent Pipeline UUIDv4.
    previous_workspace_id : str
        Workspace ID of the existing environment binding being replaced.
    previous_notebook_id : str
        Notebook ID of the existing environment binding being replaced.
    config_workspace_id : str | None, optional
        Workspace hosting 00_env_config; defaults to the caller workspace.

    Returns
    -------
    str
        The unchanged Pipeline UUID, now bound to the current notebook.

    Raises
    ------
    ValueError
        If the UUID, previous binding or current notebook ownership conflicts.
    RuntimeError
        If the registry transaction cannot be confirmed; inspect and retry setup.

    Examples
    --------
    >>> PIPELINE_ID = rebind_pipeline(PIPELINE_ID,
    ...     previous_workspace_id=old_workspace_id, previous_notebook_id=old_notebook_id)

    """
    return administer_pipeline_registration(pipeline_id, previous_binding=(previous_workspace_id, previous_notebook_id),
        config_workspace_id=config_workspace_id)
