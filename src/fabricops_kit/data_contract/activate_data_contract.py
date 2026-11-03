"""Activate exact frozen Contracts independently of Pipeline Promotion."""
from __future__ import annotations


def activate_data_contract(table_id: str, contract_id: str, contract_version: int, *,
                           expected_activation_id: str | None, activation_id: str,
                           workspace_id: str | None = None, governance_confirmed: bool = False):
    """Activate a frozen Contract in its physical table workspace.

    Parameters
    ----------
    table_id, contract_id : str
        Exact logical Table ID and globally frozen Contract identity.
    contract_version : int
        Exact frozen positive version; never a latest-version fallback.
    expected_activation_id : str | None
        Previously reviewed activation ID; None asserts no existing activation.
    activation_id : str
        Unique operation ID retained for safe retry after a lost acknowledgement.
    workspace_id : str | None, optional
        Physical table workspace, defaulting to the current execution scope.
        Metadata continues to use the configured central Metadata Lakehouse.
    governance_confirmed : bool, default=False
        Review confirmation. Actual metadata storage permissions authorize writes;
        this flag grants no permissions.

    Returns
    -------
    dict
        Committed METADATA_DATA_CONTRACT_ACTIVATION row, including revision.

    Raises
    ------
    ValueError
        If the exact frozen Contract, physical binding, operation ID or expected
        activation is invalid, or another Table ID aliases the physical table.
    RuntimeError
        If a writer holds the publication claim, Fabric/Spark is unavailable or
        transactional readback fails. Reconcile interrupted writers before retry.

    Notes
    -----
    Call setup_notebook first. Frozen definitions are immutable and global;
    activations are per physical workspace/Table ID. Existing admitted runs keep
    captured Contracts; the next run resolves the new version. Normal setup never
    drops development metadata. No business target or Processing State is changed.

    Examples
    --------
    >>> result = activate_data_contract(TABLE_ID, CONTRACT_ID, 1,
    ...     expected_activation_id=None, activation_id=OPERATION_ID,
    ...     governance_confirmed=True)

    """
    from fabricops_kit.activated_pipeline.shared import set_table_contract_activation
    from fabricops_kit.config.shared import resolve_fabric_context
    config, workspace, runtime = resolve_fabric_context()
    target = workspace if workspace_id is None else str(workspace_id).strip()
    if not target:
        raise ValueError("workspace_id must be nonblank.")
    return set_table_contract_activation(table_id, contract_id, contract_version,
        expected_activation_id=expected_activation_id, activation_id=activation_id,
        governance_confirmed=governance_confirmed,
        context={**runtime, "config": config, "scope_workspace_id": target,
            "metadata_workspace_id": runtime.get("metadata_workspace_id") or workspace})
