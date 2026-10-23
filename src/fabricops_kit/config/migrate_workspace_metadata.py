"""Explicit, stopped-workload migration of existing shared metadata."""
from copy import deepcopy

from .shared import (fabric_runtime_identity, registry_bootstrap, read_workspace_registry, bootstrap_context,
                     validate_workspace_registration, activation_scope, suspend_governed_context)


def migrate_workspace_metadata(*, legacy_environment: str, workspace_id: str, expected_token: str,
                               workloads_stopped: bool = False, spark_session=None):
    """Assign one legacy environment to exactly one inactive registered workspace.

    Administrators must stop and verify all Fabric jobs first. The registry must
    contain no active workspaces during migration. Delta updates are idempotent
    per table; rerun after an interrupted migration while registrations remain
    inactive. Contract payloads, IDs, versions, manifests and historical outcomes
    remain unchanged. Original environment labels are retained in an additive
    audit column. No legacy approval can be inherited by a second workspace.

    Parameters
    ----------
    legacy_environment : str
        Exact previous environment key, without inference or defaults.
    workspace_id : str
        Inactive registered workspace receiving this environment's metadata.
    expected_token : str
        Reviewed activation/reservation token from read_activation_state.
    workloads_stopped : bool
        Explicit administrator confirmation that native Fabric executions stopped.
    spark_session : object, optional
        Fabric Spark session with administrator metadata write permissions.

    Returns
    -------
    str
        Confirmed activation/reservation token after migration.

    """
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F
    from fabricops_kit.io.shared import get_spark_session, resolve_configured_lakehouse_table
    from fabricops_kit.config.metadata_schemas import WORKSPACE_SCOPED_METADATA_TABLES, metadata_table_physical_schema
    from fabricops_kit.activated_pipeline.shared import read_activation_state, commit_activation_state
    identity, locator = fabric_runtime_identity(), registry_bootstrap()
    if identity["workspace_id"] != locator["governance_workspace_id"] or workloads_stopped is not True:
        raise PermissionError("Governance administrators must confirm all native Fabric workloads stopped.")
    if "@" in legacy_environment:
        raise ValueError("Migrate only unscoped legacy environments, never an existing workspace activation scope.")
    if not legacy_environment.strip():
        raise ValueError("An exact legacy environment is required.")
    _registry_token, registry = read_workspace_registry(locator=locator, identity=identity, spark_session=spark_session)
    if any(row["status"] == "active" for row in registry["workspaces"].values()):
        raise ValueError("Disable all workspace registrations before migrating shared metadata.")
    registration = validate_workspace_registration(registry["workspaces"][workspace_id], locator=locator)
    if registration["workspace_id"] != workspace_id:
        raise ValueError("Workspace Registry key does not match its authoritative workspace ID.")
    bootstrap = bootstrap_context(locator, identity)
    with suspend_governed_context():
        token, state = read_activation_state(context=bootstrap, spark_session=spark_session)
        if token != expected_token or any(current["runs"] for current in state["environments"].values()):
            raise ValueError("Activation changed or run reservations remain; verify stopped workloads before migration.")
        current = state["environments"].setdefault(legacy_environment, {"revision": "initial", "pipelines": {},
            "history": {}, "tables": {}, "runs": {}})
        scope = activation_scope(registration["environment"], {"_registry_workspace_id": workspace_id})
        if current and current.get("migrated_to") not in {None, scope}:
            raise ValueError("This legacy environment was already assigned to another workspace.")
        target = state["environments"].get(scope)
        if target and not (current and current.get("migrated_to") == scope):
            raise ValueError("Target workspace already has activation history; migrate into an empty scope.")
        routes = {(r["workspace_id"], r["item_id"], r["kind"]) for r in registration["resources"].values()}
        if current:
            for item in current["tables"].values():
                destination = item["destination"]
                if (destination["workspace_id"], destination["item_id"], destination["kind"]) not in routes:
                    raise ValueError("Legacy approval physical bindings do not match the registered resource mappings.")
        if not current.get("migrated_to"):
            destinations = [item["destination"] for item in current["tables"].values() if item.get("writer")]
            for other_scope, other in state["environments"].items():
                if other_scope != legacy_environment and any(item.get("writer") and item["destination"] in destinations
                                                             for item in other["tables"].values()):
                    raise ValueError("Legacy writer ownership conflicts across scopes; reconcile Governance decisions before migration.")
        spark = get_spark_session(spark_session)
        for table in WORKSPACE_SCOPED_METADATA_TABLES:
            _store, _name, _schema, path = resolve_configured_lakehouse_table(
                "Metadata", table, metadata_table_physical_schema(bootstrap["config"], table), context=bootstrap)
            delta = DeltaTable.forPath(spark, path)
            delta.update(condition=F.col("execution_workspace_id").isNull() & (F.col("environment_name") == legacy_environment),
                         set={"execution_workspace_id": F.lit(workspace_id),
                              "_legacy_environment_name": F.col("environment_name"),
                              "environment_name": F.lit(registration["environment"])})
        if current and not current.get("migrated_to"):
            state["environments"][scope] = deepcopy(current)
            current.update(pipelines={}, tables={}, migrated_to=scope)
        return commit_activation_state(state, expected_token=token, context=bootstrap, spark_session=spark)
