"""Optional pipeline-level observation of historical physical source contents."""

from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fabricops_kit.pipeline.shared import (
    current_pipeline_session,
    observe_full_source,
    persist_pipeline_run,
    source_drift_investigation_query,
    write_guardrail_result_row,
)


def observe_source_drift(
    observe_immediately: bool = True,
    source_observation_days: int | None = 1,
    block: bool = True,
) -> dict:
    """Compare all sources already read in this execution with accepted history.

    Call after all orchestrate_read calls and before transformation and Write.
    Full and Incremental Read both observe the complete physical source, once
    per canonical Table ID per call. Sources read later are not covered. This
    optional function works without Data Contracts and with every Write Mode.

    Parameters
    ----------
    block : bool, default=True
        Block write: stop execution after reporting all failures. False returns
        warnings and permits continuation, including when evaluation is unavailable.
    source_observation_days : int or None, default=1
        Observe every day(s): positive integer interval since the last accepted
        snapshot. None requests observation on each call. Booleans are invalid.
    observe_immediately : bool, default=True
        Observe immediately: True forces a check now; False uses the interval.
        An interval skip is reported as skipped, never passed.

    Returns
    -------
    dict
        Pipeline and execution IDs, status, can_continue, blocking policy,
        per-source counts/reasons and scoped investigation queries. Counts include
        added, modified, removed and ambiguous historical rows. Without validated
        unique keys, added/missing content is exact but modifications are unknown;
        ambiguous counts describe missing content and overlap removed counts.

    Raises
    ------
    ValueError
        If controls are invalid.
    RuntimeError
        If no pipeline is active, or blocking observation detects historical
        changes or cannot evaluate a source. All sources are attempted and
        diagnostics are persisted and printed before a blocking exception.

    Notes
    -----
    Requires Spark and configured metadata access. A full-source scan and retained
    identity/hash multiplicities cost compute and metadata storage proportional to
    distinct source content. No raw business values are persisted. Observation
    captures candidates; successful Finalize and verified required publications
    accept them. A successful nonblocking run with completed evaluation accepts its new snapshot, retaining
    warning diagnostics. Failed, blocked, partial or stale concurrent runs do not
    advance history. Dry Run never persists or accepts snapshots. Existing aggregate
    fingerprints cannot prove historical row identity: a clean successful run must
    establish the first exact snapshot. Observation does not repair source data.

    Examples
    --------
    >>> orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    >>> result = observe_source_drift(block=True, observe_immediately=True)
    >>> scheduled = observe_source_drift(observe_immediately=False, source_observation_days=1)

    """
    if type(block) is not bool or type(observe_immediately) is not bool:
        raise ValueError("block and observe_immediately must be booleans.")
    if source_observation_days is not None and (
        type(source_observation_days) is not int or source_observation_days <= 0
    ):
        raise ValueError("source_observation_days must be a positive integer or None.")
    session = current_pipeline_session()
    plan = session.plan
    started = perf_counter()
    evaluation_id = str(uuid4())
    with plan.lock:
        if plan.evidence.get("sealed"):
            raise RuntimeError("This pipeline execution is already finalized.")
        # Canonical IDs prevent repeated Reads from triggering repeated physical scans.
        source_ids = list(dict.fromkeys(source["table_id"] for source in session.sources))
        import json
        identities = json.loads(plan.participants_json)
        context = {**plan.runtime_context, "execution_plan": plan, "_spark_session": session.spark,
                   "_fabricops_suppress_io_log": True}
        plan.evidence["source_drift_coverage_invalid"] = False
        plan.evidence["source_drift_candidates"] = {}
        results = []
        for source_id in source_ids:
            identity = identities[source_id]
            try:
                result = observe_full_source(identity, context=context,
                    observe_immediately=observe_immediately, source_observation_days=source_observation_days)
            except Exception as exc:
                # Avoid connector exception strings, which can contain paths or business values.
                result = {"status": "evaluation_failed", "reason": "Source or historical evidence could not be evaluated. Check access and snapshot integrity.",
                          "error_type": type(exc).__name__, "added_count": None, "modified_count": None,
                          "removed_count": None, "ambiguous_count": None}
                plan.evidence.setdefault("source_drift_candidates", {}).pop(source_id, None)
            failed = result["status"] in {"failed", "evaluation_failed"}
            result.update(table_id=source_id, table_name=identity["table_name"],
                          source_name=".".join(str(identity[key]) for key in ("store", "schema", "table_name") if identity.get(key)),
                          pipeline_id=plan.pipeline_id,
                          run_id=plan.plan_id, evaluation_id=evaluation_id, guardrail_type="source_drift", can_continue=not (block and failed),
                          block=block, action="Block" if block else "Warn", severity="blocking" if block else "warning",
                          guardrail_rule_id="pipeline_source_drift_v1", guardrail_version=1,
                          rule_context={"rule_type": "historical_source_content"})
            if failed:
                result["investigation_query"] = source_drift_investigation_query(plan, source_id, evaluation_id=evaluation_id)
            try:
                write_guardrail_result_row(spark_session=session.spark, config=context["config"],
                    active_workspace_id=plan.workspace_id, run_id=plan.plan_id, dataset_name="",
                    table_name=identity["table_name"], store_type=identity.get("store_type") or identity.get("store_kind") or "", layer="",
                    guardrail_type="source_drift", rule_type="historical_source_content", result=result,
                    table_id=source_id, context=context)
            except Exception as exc:
                result.update(status="evaluation_failed", reason="Diagnostic persistence failed; no baseline will be accepted.",
                              error_type=type(exc).__name__, can_continue=not block)
                result["investigation_query"] = source_drift_investigation_query(plan, source_id, evaluation_id=evaluation_id)
                plan.evidence.setdefault("source_drift_candidates", {}).clear()
            results.append(result)
        any_failure = any(r["status"] in {"failed", "evaluation_failed"} for r in results)
        unavailable = any(r["status"] == "evaluation_failed" for r in results)
        skipped = not results or all(r["status"] == "skipped" for r in results)
        can_continue = not (block and any_failure)
        drift_detected = any(r.get("modified_count") or r.get("removed_count") or r.get("ambiguous_count") for r in results)
        historical_unknown = unavailable or any(r["status"] in {"skipped", "first_observation"} for r in results) or not results
        status = ("evaluation_failed" if unavailable else "failed" if block and any_failure else
                  "warning" if any_failure else "skipped" if skipped else
                  "first_observation" if all(r["status"] == "first_observation" for r in results) else
                  "partially_skipped" if any(r["status"] == "skipped" for r in results) else "passed")
        result = {"pipeline_id": plan.pipeline_id, "run_id": plan.plan_id, "evaluation_id": evaluation_id, "status": status,
                  "can_continue": can_continue, "decision": "continue" if can_continue else "blocked",
                  "historical_drift_detected": True if drift_detected else None if historical_unknown else False,
                  "block": block, "observe_immediately": observe_immediately,
                  "source_observation_days": source_observation_days, "sources": results,
                  "covered_source_ids": source_ids, "elapsed_seconds": round(perf_counter() - started, 2),
                  "reason": "No previously read sources." if not results else "All previously read sources evaluated or explicitly skipped."}
        for count in ("added_count", "modified_count", "removed_count", "ambiguous_count"):
            result[count] = None if unavailable or any(r["status"] == "skipped" for r in results) else sum(r.get(count) or 0 for r in results)
        # Persist the consolidated decision separately from bounded source samples.
        # A pipeline summary has no table/Contract identity; its payload carries
        # the actual pipeline, run, evaluation and participating source identities.
        summary_payload = {**result, "sources": [{key: value for key, value in source.items()
                           if key not in {"samples", "investigation_query", "rule_context"}} for source in results],
                           "guardrail_rule_id": "pipeline_source_drift_summary_v1", "guardrail_version": 1,
                           "guardrail_type": "source_drift", "action": "Block" if block else "Warn",
                           "severity": "blocking" if block else "warning",
                           "rule_context": {"rule_type": "pipeline_observation"}}
        try:
            write_guardrail_result_row(spark_session=session.spark, config=context["config"],
                active_workspace_id=plan.workspace_id, run_id=plan.plan_id, dataset_name="", table_name="",
                store_type="", layer="", guardrail_type="source_drift", rule_type="pipeline_observation",
                result=summary_payload, context=context)
        except Exception as exc:
            result.update(status="evaluation_failed", can_continue=not block, decision="blocked" if block else "continue",
                          reason="Consolidated result persistence failed; no baseline will be accepted.",
                          diagnostics_error_type=type(exc).__name__)
            can_continue, unavailable = not block, True
        plan.evidence.setdefault("source_drift_results", []).append(result)
        if unavailable or not can_continue:
            plan.evidence.setdefault("source_drift_candidates", {}).clear()
        print("\nFabricOps Source Drift Observation")
        print(f"Pipeline: {plan.pipeline_id}\nExecution: {plan.plan_id}")
        print(f"Observation status: {result['status'].upper()}")
        print(f"Reason: {result['reason']}")
        print("Source | Status | Added | Modified | Removed | Ambiguous")
        for row in results:
            counts = " | ".join(str(row.get(key)) if row.get(key) is not None else "unknown"
                                for key in ("added_count", "modified_count", "removed_count", "ambiguous_count"))
            print(f"{row['source_name']} | {row['status'].upper()} | {counts}")
            print(f"  {row['reason']}")
        print(f"Historical drift detected: {'Yes' if drift_detected else 'Not established or not checked' if historical_unknown else 'No'}")
        print(f"Observe immediately: {observe_immediately} | Observe every day(s): {source_observation_days}")
        print(f"Block write: {block} | Decision: {'CONTINUE' if can_continue else 'BLOCKED'} | Elapsed: {result['elapsed_seconds']:.2f}s")
        for row in results:
            if row.get("investigation_query"):
                print(f"\nInvestigation for {row['table_name']} (at most 10 hash-only samples per category):\n{row['investigation_query']}")
        if not can_continue:
            plan.evidence["failures"].append({"code": "source_drift_blocked"})
            persist_pipeline_run(plan, spark_session=session.spark, status="failed")
            error = RuntimeError("Source Drift observation blocked execution. Review the source counts and scoped investigation query; restore the source, or use block=False in a reviewed new run. Successful Finalize of a nonblocking run accepts its candidate history.")
            error.result = result
            raise error
        return result
