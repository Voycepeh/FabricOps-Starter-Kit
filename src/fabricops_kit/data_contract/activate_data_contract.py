"""Notebook-facing independent environment/Table ID Contract activation."""
from __future__ import annotations


def activate_data_contract(table_id: str, contract_id: str, contract_version: int, *,
                           expected_token: str, workspace_id: str | None = None, governance_confirmed: bool = False):
    """Activate one exact frozen Data Contract for the configured execution workspace.

    This action is independent of pipeline activation. It protects the Table ID
    and its physical destination from Ungoverned publication. It never unfreezes
    or copies a Contract, activates a pipeline or enables Governed execution.

    Parameters
    ----------
    table_id, contract_id : str
        Exact logical Table ID and globally frozen Contract identity.
    contract_version : int
        Exact frozen version, never a latest-version fallback.
    expected_token : str
        Current Registry control token from the reviewed snapshot. Stale review
        is rejected; refresh and review before retrying.
    workspace_id : str | None, optional
        Target execution workspace; defaults to the notebook configuration scope.
        Central Metadata routing remains separate from this activation scope.
    governance_confirmed : bool, default=False
        Explicit confirmation of the reviewed governance change. This is not
        authentication: metadata write principals must be trusted and restricted
        by tenant permissions.

    Returns
    -------
    dict
        Committed table_contract_activation record with immutable activation ID.

    Raises
    ------
    ValueError
        If confirmation, exact frozen identity, current token, destination or
        active pipeline compatibility fails, or an affected execution must drain.
    RuntimeError
        If notebook/Spark context, atomic publication or exact readback fails.
        A failed acknowledgement requires inspecting the Registry and audit
        transaction before another governance decision.

    Notes
    -----
    Call setup_notebook first. The central configured Metadata Lakehouse is used.
    The one Registry transaction retains a durable before/after audit snapshot.
    No business data, Processing State or historical Run is changed.

    Examples
    --------
    >>> activated = activate_data_contract(TABLE_ID, CONTRACT_ID, 1,
    ...     expected_token=reviewed_token, governance_confirmed=True)

    """
    from fabricops_kit.activated_pipeline.shared import set_table_contract_activation
    from fabricops_kit.config.shared import resolve_fabric_context

    config, workspace, runtime = resolve_fabric_context()
    target_workspace = workspace if workspace_id is None else str(workspace_id).strip()
    if not target_workspace:
        raise ValueError("workspace_id must be nonblank.")
    return set_table_contract_activation(table_id, contract_id, contract_version,
        expected_token=expected_token, governance_confirmed=governance_confirmed,
        context={**runtime, "config": config, "scope_workspace_id": target_workspace,
            "metadata_workspace_id": runtime.get("metadata_workspace_id") or workspace})
