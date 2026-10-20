"""Public creation of explicit, environment-neutral pipeline run authority."""

from __future__ import annotations

import json
from types import MappingProxyType
from uuid import uuid4

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    PipelineExecutionPlan,
    contract_guardrail_rows,
    resolve_active_data_contract,
    resolve_catalogue_table_identity,
    resolve_data_contract_version,
    resolve_physical_table_identity,
)


def create_pipeline_execution_plan(*, execution_mode, sources, targets, selections, context=None, spark_session=None):
    """Freeze one explicit Testing/Live decision and contract selection for a run.

    Parameters
    ----------
    execution_mode : {"testing", "live"}
        Required for interactive and scheduled execution, independent of environment.
    sources : list of dict
        Actual source participants with store/schema/table_name or a registered
        canonical table_id. No historical Lineage is needed.
    targets : list of dict
        Actual target participants with store/schema/table_name or a registered table_id.
    selections : dict
        Exactly one choice per participating table_id: either
        ``{"no_contract": True}`` or exact ``contract_id`` and ``contract_version``.
        Live requires the active frozen version when one exists and never accepts
        an inactive candidate. No Contract cannot bypass an active version.
    context : dict, optional
        Configured Fabric routing and runtime notebook identity.
    spark_session : object, optional
        Spark session for metadata reads.

    Returns
    -------
    PipelineExecutionPlan
        Immutable mode, identities, and canonical frozen payload snapshots, with
        an isolated in-memory Guardrail journal shared by all Read/Write calls.
        Create a new plan after changing selections; pass the same plan explicitly
        to every orchestrator in the run. This function performs metadata reads only.

    Raises
    ------
    ValueError
        If mode, identities or explicit selections are invalid, or Live would
        bypass an active contract. Corrupt payloads are errors, never No Contract.
    RuntimeError
        If metadata contains ambiguous active versions or duplicate version rows.

    Examples
    --------
    >>> plan = create_pipeline_execution_plan(
    ...     execution_mode="testing", sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS,
    ...     selections={source_id: {"no_contract": True}, target_id: {"no_contract": True}},
    ... )
    >>> source = orchestrate_read(execution_plan=plan, store="Bronze", schema="demo", table_name="orders")

    """
    if execution_mode not in {"testing", "live"}:
        raise ValueError("execution_mode must explicitly be 'testing' or 'live'.")
    from fabricops_kit.data_contract.shared import validate_contract_definitions

    config, env, runtime = resolve_fabric_context(context=context)
    notebook_id = str(runtime.get("notebook_id") or "").strip()
    if not notebook_id:
        raise ValueError("An explicit notebook_id is required for pipeline execution.")
    identities = {}
    for role, participants in (("source", sources), ("target", targets)):
        for participant in participants:
            if "store" in participant:
                identity = resolve_physical_table_identity(config, env, **{
                    key: participant[key] for key in ("store", "schema", "table_name")
                })
                if participant.get("table_id") not in (None, identity["table_id"]):
                    raise ValueError("Configured participant does not match its canonical table_id.")
            else:
                identity = resolve_catalogue_table_identity(
                    config, env, participant["table_id"], context=runtime, spark_session=spark_session,
                )
            identity = {**identity, "store_type": identity.get("store_type") or identity.get("store_kind")}
            table_id = identity["table_id"]
            roles = list(identities.get(table_id, {}).get("roles", []))
            if role in roles:
                raise ValueError(f"Duplicate {role} participant {table_id!r}.")
            identities[table_id] = {**identity, "roles": [*roles, role]}
    if not identities or set(selections) != set(identities):
        raise ValueError("Supply an explicit contract or No Contract choice for every participating table only.")
    contracts = {}
    for table_id, choice in selections.items():
        if not isinstance(choice, dict):
            raise ValueError("Every contract selection must be an explicit mapping.")
        active = resolve_active_data_contract(config, env, table_id, spark_session=spark_session, required=False)
        if choice == {"no_contract": True}:
            if active is not None:
                raise ValueError(f"No Contract cannot bypass the active contract for {table_id!r}.")
            contracts[table_id] = None
            continue
        if set(choice) != {"contract_id", "contract_version"}:
            raise ValueError("Select exact contract_id/contract_version or explicit no_contract=True.")
        selected = resolve_data_contract_version(
            config, env, table_id, choice["contract_id"], choice["contract_version"],
            spark_session=spark_session, context=runtime,
        )
        validate_contract_definitions(selected["contract_payload"])
        contract_guardrail_rows(selected, environment_name=env, table_id=table_id)
        if execution_mode == "live" and (active is None or any(
            selected[key] != active[key] for key in ("contract_id", "contract_version")
        )):
            raise ValueError(f"Live requires the active frozen contract for {table_id!r}; candidates require Testing.")
        contracts[table_id] = selected
    plan_id = str(uuid4())
    run_context = {**runtime, "config": config, "env": env}
    if execution_mode == "testing":
        run_context["activity_id"] = plan_id
    return PipelineExecutionPlan(
        execution_mode, env, notebook_id, plan_id,
        json.dumps(identities, default=str, sort_keys=True),
        json.dumps(selections, sort_keys=True), json.dumps(contracts, default=str, sort_keys=True),
        MappingProxyType(run_context),
    )
