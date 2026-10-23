"""Governance administrator entrypoint for central workspace registration."""
from .shared import (fabric_runtime_identity, registry_bootstrap, bootstrap_context,
                     read_workspace_registry, validate_workspace_registration, commit_metadata_snapshot,
                     REGISTRY_TABLE, suspend_governed_context)


def register_workspace(registration: dict, *, expected_token: str, spark_session=None):
    """Publish one complete workspace registration using an explicit reviewed registry token.

    Run in the pinned Governance Workspace with Fabric write permission on the
    registry table. The workspace check is a usage guard; Fabric permissions are
    the security boundary. Existing entries are replaced atomically, never merged
    with notebook parameters. A changed registry requires fresh pipeline setup.

    Parameters
    ----------
    registration : dict
        Complete workspace_id, display_name, environment, status, resources,
        notebooks and settings mapping. Metadata must match the pinned locator.
    expected_token : str
        Registry token reviewed by the administrator. Stale tokens fail closed.
    spark_session : object, optional
        Fabric Spark session.

    Returns
    -------
    str
        Confirmed registry token for the new snapshot.

    """
    identity, locator = fabric_runtime_identity(), registry_bootstrap()
    if identity["workspace_id"] != locator["governance_workspace_id"]:
        raise PermissionError("Workspace registrations must be managed in the Governance Workspace.")
    registration = validate_workspace_registration(registration, locator=locator)
    token, snapshot = read_workspace_registry(locator=locator, identity=identity, spark_session=spark_session)
    if token != expected_token:
        raise ValueError("Workspace Registry changed; refresh and review before publishing.")
    snapshot["workspaces"][registration["workspace_id"]] = registration
    with suspend_governed_context():
        return commit_metadata_snapshot(REGISTRY_TABLE, snapshot, expected_token=token,
            context=bootstrap_context(locator, identity), spark_session=spark_session)
