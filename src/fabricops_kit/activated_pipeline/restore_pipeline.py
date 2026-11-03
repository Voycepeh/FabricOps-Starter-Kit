"""Explicit exact-snapshot notebook restoration."""
from __future__ import annotations


def restore_pipeline(pipeline_id: str, *, expected_active_version: int,
                     workspace_id: str | None = None, governance_confirmed: bool = False) -> dict:
    """Preserve the changed notebook and restore its exact active frozen implementation.

    Parameters
    ----------
    pipeline_id : str
        Stable logical Pipeline ID.
    expected_active_version : int
        Reviewed active version; an intervening promotion cancels restoration.
    workspace_id : str | None, optional
        Destination execution workspace, defaulting to the notebook scope.
    governance_confirmed : bool, default=False
        Explicit review confirmation; actual Fabric permissions authorize repair.

    Returns
    -------
    dict
        Existing promotion/version, preserved changed-copy URI and readiness gate.

    Raises
    ------
    ValueError
        If review is stale, ambiguous or unconfirmed.
    RuntimeError
        If archive, bindings, preservation, update or readback verification fails.

    Notes
    -----
    No approval is rewritten and no new version is created. Different code needs
    a new manual Dry Run and promotion. Imported dependencies are not restored.
    Tenant permissions remain the security boundary; saved-code checks have TOCTOU.

    Examples
    --------
    >>> result = restore_pipeline(PIPELINE_ID, expected_active_version=1,
    ...     governance_confirmed=True)

    """
    from fabricops_kit.activated_pipeline.shared import restore_promoted_notebook
    from fabricops_kit.config.shared import resolve_fabric_context
    config, workspace, runtime = resolve_fabric_context()
    target = workspace_id or workspace
    return restore_promoted_notebook(pipeline_id, workspace_id=target,
        expected_active_version=expected_active_version, governance_confirmed=governance_confirmed,
        context={**runtime, "config": config, "scope_workspace_id": target,
            "metadata_workspace_id": runtime.get("metadata_workspace_id") or workspace})
