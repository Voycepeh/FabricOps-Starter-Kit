"""Shared pipeline implementation helpers."""

from __future__ import annotations

from fabricops_kit.io.shared import retry_delta_metadata

import hashlib
import json
import ast
import re
import time
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from functools import reduce
from threading import RLock
from dataclasses import dataclass, field as dataclass_field
from uuid import uuid4
from typing import Any, Mapping

PIPELINE_MODE_NAMES = {
    "dry_run": "Dry Run",
    "ungoverned": "Ungoverned",
    "governed": "Governed",
}

@dataclass(frozen=True)
class PipelineExecutionPlan:
    """Immutable run authority with an isolated in-memory diagnostic journal."""

    execution_mode: str
    workspace_id: str
    notebook_id: str
    plan_id: str
    participants_json: str
    selections_json: str
    contracts_json: str
    runtime_context: Any = dataclass_field(repr=False, compare=False)
    pipeline_id: str = ""
    pipeline_version: int | None = None
    promotion_id: str = ""
    governed_notebook_id: str = ""
    activated_operations_json: str = "[]"
    lock: Any = dataclass_field(default_factory=RLock, repr=False, compare=False)
    evidence: dict = dataclass_field(default_factory=dict, repr=False, compare=False)
    results: list = dataclass_field(default_factory=list, repr=False, compare=False)
    simulations: list = dataclass_field(default_factory=list, repr=False, compare=False)

    def __post_init__(self):
        """Reject unsupported execution authority at construction."""
        if not self.evidence:
            operations = {f"{role}:{identity.get('logical_id') or identity['store'] + '/' + identity['table_name']}":
                          {"status": "not_started", "stages": []}
                          for identity in json.loads(self.participants_json).values() for role in identity["roles"]}
            self.evidence.update(started_at=datetime.now(UTC), operations=operations, failures=[], sealed=False, persistence_failed=False)
        if self.execution_mode not in PIPELINE_MODE_NAMES:
            raise ValueError("Execution mode must be dry_run, ungoverned or governed.")

    @property
    def permits_persistence(self):
        """Whether this run permits durable mutations."""
        return self.execution_mode in {"ungoverned", "governed"}

    @property
    def run_result(self):
        """Return the persisted whole-run outcome after the execution boundary exits."""
        if not self.evidence.get("sealed"):
            raise RuntimeError("The whole-run boundary has not completed.")
        return dict(self.evidence["final_result"])

    def __enter__(self):
        """Open the explicit whole-run boundary, including project transformations."""
        with self.lock:
            if self.evidence.get("sealed") or self.evidence.get("boundary_open"):
                raise RuntimeError("Run boundary is already open or closed; create a new plan.")
            if self.evidence.get("failures") or any(
                operation["status"] != "not_started" for operation in self.evidence["operations"].values()
            ):
                raise RuntimeError("Open the whole-run boundary before executing any operation; create a new plan.")
            self.evidence["boundary_open"] = True
        return self

    def __exit__(self, exc_type, exc, traceback):
        """Automatically record completion only when the entire boundary exits."""
        self.evidence["boundary_completed"] = exc_type is None
        finalize_pipeline_run(self, failed=exc_type is not None,
                              spark_session=self.runtime_context.get("_pipeline_spark"))
        return False


def persistence_permitted(context):
    """Apply the single execution-level policy at a durable mutation boundary."""
    plan = (context or {}).get("execution_plan")
    if getattr(plan, "execution_mode", None) in {"governed"}:
        from fabricops_kit.activated_pipeline.shared import verify_governed_plan
        verify_governed_plan(plan)
    return plan is None or plan.permits_persistence


def source_observation_run_id(context):
    """Reuse the pipeline attempt identity without replacing Fabric activity audit."""
    return getattr((context or {}).get("execution_plan"), "plan_id", None)


def execution_result(context, table_id, *, stages=()):
    """Describe execution authority and publication limits without Spark actions."""
    plan = context["execution_plan"]
    contract = context["_pipeline_contracts"].get(table_id)
    return {
        "execution_mode": plan.execution_mode, "execution_plan_id": plan.plan_id,
        "execution_workspace_id": plan.workspace_id,
        "guardrail_outcomes": [dict(row) for row in plan.results if (row.get("source_id") or row.get("table_id")) == table_id],
        "simulation_outcomes": list(plan.simulations),
        "selected_contract": ({"contract_id": contract["contract_id"],
                               "contract_version": contract["contract_version"]} if contract else None),
        "applicable_guardrails": sorted(pipeline_guardrail_types(context, table_id)),
        "persistence_status": "completed" if plan.permits_persistence else "disabled",
        "persistence_policy": "allow_commits" if plan.permits_persistence else "read_only",
        "publication_status": "not_requested" if plan.permits_persistence else "not_published",
        "checks_not_exercised": [] if plan.permits_persistence else [
            "Fabric publication permissions", "target transaction and concurrency behavior",
            "cross-store metadata finalization"] + [
                f"{stage['stage']}: {stage.get('reason', 'not fully evaluated')}" for stage in stages
                if stage.get("evaluation_status") == "not_fully_evaluated"],
    }


def _orchestration_status(result: Any) -> str:
    """Normalize a capability result into an orchestration stage status."""
    if isinstance(result, (list, tuple)):
        statuses = [_orchestration_status(item) for item in result]
        if "blocked" in statuses:
            return "blocked"
        if "warning" in statuses:
            return "warning"
        if statuses and all(status == "skipped" for status in statuses):
            return "skipped"
        return "passed"
    if isinstance(result, dict):
        status = str(result.get("status", "")).strip().lower().replace("-", "_").replace(" ", "_")
        if result.get("can_continue") is False:
            return "blocked"
        if status in {"skip", "skipped", "not_applicable", "not_due", "disabled"}:
            return "skipped"
        if status in {"warn", "warning"}:
            return "warning"
        if status in {"block", "blocked", "fail", "failed", "failure", "error"}:
            return "blocked"
        if status in {"pass", "passed", "success", "succeeded", "completed"}:
            return "passed"
        if status:
            return "warning"
    return "passed"


def _run_orchestration_stage(*, operation: str, name: str, index: int, total: int, stage: str, function, verbose: bool, allow_blocked: bool = False):
    """Run one visible stage while retaining its original exception as the cause."""
    started = time.perf_counter()
    if verbose:
        print(f"[{index:,}/{total:,}] {stage} ... running")
    try:
        try:
            result = function()
        except ValueError as exc:
            if not allow_blocked or stage not in {"Freshness", "Schema", "Grain", "Data Quality"}:
                raise
            result = {"status": "blocked", "can_continue": False, "checks": [],
                      "evaluation_status": "not_fully_evaluated", "reason": str(exc)}
        if verbose and stage == "Data Quality" and isinstance(result, dict) and result.get("summary"):
            summary = result["summary"]
            print(f"  DQ applicable rows: {summary.get('DQ_PASSED_ROW_PERCENT', 0):,.2f}% pass, "
                  f"{summary.get('DQ_FAILED_ROW_PERCENT', 0):,.2f}% with violations; "
                  f"{summary.get('DQ_NOT_APPLICABLE_ROW_COUNT', 0):,} not applicable. Tolerances determine continuation.")
        status = _orchestration_status(result)
        if stage in {"Schema", "Grain", "Data Quality", "Sensitive Data", "Source Drift", "Freshness"}:
            items = result if isinstance(result, list) else [result]
            normalized = []
            for item in items:
                unavailable = (
                    not isinstance(item, dict) or str(item.get("status") or "").lower() not in {
                        "passed", "pass", "success", "succeeded", "baseline_created", "warning", "warn",
                        "failed", "fail", "failure", "error", "blocked", "block", "skip", "skipped", "not_applicable"
                    }
                    or (str(item["status"]).lower() in {"skip", "skipped", "not_applicable"}
                        and not (stage == "Freshness" and item.get("rule_type") == "skip"))
                    or item.get("evaluation_status") == "not_fully_evaluated"
                )
                normalized.append({**(item if isinstance(item, dict) else {}),
                                   "status": "blocked", "can_continue": False,
                                   "evaluation_status": "not_fully_evaluated",
                                   "reason": "A configured Guardrail did not execute."} if unavailable else item)
            result = normalized if isinstance(result, list) else normalized[0]
            if not normalized:
                result = {"status": "blocked", "can_continue": False,
                          "evaluation_status": "not_fully_evaluated",
                          "reason": "A configured Guardrail did not execute."}
            status = _orchestration_status(result)
        if status == "blocked" and not allow_blocked:
            blocked_items = result if isinstance(result, list) else [result]
            reason = next((item.get("reason") for item in blocked_items
                           if isinstance(item, dict) and item.get("reason")), None)
            detail = f" Reason: {reason}" if reason else ""
            raise RuntimeError(f"Stage returned blocking status.{detail}")
    except Exception as exc:
        duration = max(0.01, round(time.perf_counter() - started, 2))
        root = exc
        seen = set()
        while id(root) not in seen:
            seen.add(id(root))
            next_error = root.__cause__ or (root.__context__ if not root.__suppress_context__ else None)
            if next_error is None:
                break
            root = next_error
        reason = f"{type(root).__name__}: {root}"
        location = ""
        if root.__traceback__ is not None:
            import traceback

            origin = traceback.extract_tb(root.__traceback__)[-1]
            location = f" ({origin.filename.rsplit('/', 1)[-1]}:{origin.lineno} in {origin.name})"
        if verbose:
            print(f"[{index:,}/{total:,}] {stage} ... ✗ Failed ({duration:,.2f}s)")
            print(f"  Root cause → {reason}{location}")
            print(f"{operation} {name!r} stopped at {stage}. Later stages did not run.")
        failure = RuntimeError(f"{operation} {name!r} failed during {stage}. Root cause: {reason}{location}")
        for field_name in ("published", "table_id", "write_metrics", "failed_stage", "persistence_status"):
            if hasattr(exc, field_name):
                setattr(failure, field_name, getattr(exc, field_name))
        raise failure from exc
    duration = max(0.01, round(time.perf_counter() - started, 2))
    if verbose:
        outcomes = {
            "skipped": ("○", "Skipped / not applicable"),
            "warning": ("⚠", "Warning"),
            "passed": ("✓", "Passed"),
            "blocked": ("✗", "Blocked (diagnostic)"),
        }
        marker, label = outcomes[status]
        print(f"[{index:,}/{total:,}] {stage} ... {marker} {label} ({duration:,.2f}s)")
    record = {"name": name, "stage": stage, "status": status, "duration_seconds": duration}
    details = result if isinstance(result, list) else [result]
    incomplete = next((item for item in details if isinstance(item, dict) and item.get("evaluation_status")), None)
    if incomplete:
        record.update(evaluation_status=incomplete["evaluation_status"], reason=incomplete.get("reason"))
    return result, record


from fabricops_kit.config.shared import (
    get_default_fabric_context,
    get_current_audit_timestamp,
    is_table_not_found_error,
    metadata_timestamp_sort_key,
    normalize_audit_datetime,
    resolve_fabric_context,
)
from fabricops_kit.io import read_lakehouse_table, read_warehouse_query, write_lakehouse_table
from ..io.shared import (
    get_spark_session,
    resolve_configured_lakehouse_table,
    resolve_lakehouse_table_location,
    resolve_warehouse_table_location,
)
from ..config.audit import _audit_timestamp_value, build_runtime_audit_fields
from ..config.shared import build_column_id, build_table_id, get_store
from ..config.metadata_schemas import (
    coerce_metadata_row_types,
    encode_metadata_row,
    decode_metadata_row,
    decode_metadata_dataframe,
    metadata_table_physical_schema,
    metadata_table_schema_registry,
)


_DEFAULT_PROFILE_EXCLUDE_COLUMNS = {
    "_pipeline_run_id",
    "_pipeline_name",
    "_pipeline_workspace_id",
    "_source_table",
    "_record_loaded_timestamp",
    "_notebook_name",
    "_loaded_by",
    "_dq_check_status",
    "_dq_failed_rules",
    "_source_system",
    "_source_extract_timestamp",
    "_watermark_value",
    "_sample_bucket",
    "_row_ingest_id",
    "_business_key_hash",
    "_row_hash",
    "pipeline_ts",
    "ingested_at_utc",
    "notebook_name",
    "loaded_by",
    "p_bucket",
    "sample_bucket",
    "row_ingest_id",
    "ingest_run_id",
    "pipeline_run_id",
    "loaded_at",
    "run_ingest_id",
    "_fabricops_run_id",
    "_fabricops_pipeline_name",
    "_fabricops_created_at",
    "_dq_check_status",
    "_dq_failed_rules",
}
_DEFAULT_PROFILE_EXCLUDE_PREFIXES = ("_fabricops_", "_dq_")
_TARGET_AUDIT_COLUMNS = (
    "_committed_at",
    "_committed_by",
    "_activity_id",
    "_workspace_id",
    "_notebook_id",
    "_notebook_name",
)
_SCD2_LIFECYCLE_COLUMNS = ("_effective_from", "_effective_to", "_is_current")
_TARGET_TECHNICAL_COLUMNS = {
    *_DEFAULT_PROFILE_EXCLUDE_COLUMNS,
    *_TARGET_AUDIT_COLUMNS,
    *_SCD2_LIFECYCLE_COLUMNS,
}


_LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
_PROCESSING_STATE_TABLE = "METADATA_PROCESSING_STATE"
_CURRENT_FRESHNESS_EVIDENCE: dict[tuple[str, str, str], dict[str, Any]] = {}
_PENDING_SOURCE_OBSERVATIONS: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
_INCREMENTAL_SOURCE_SCOPES: dict[tuple[str, str, str, str], dict[str, Any]] = {}
_ACTIVE_PUBLICATION_SOURCES: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
_CURRENT_TABLE_IDENTITIES: dict[str, dict[str, str | None]] = {}


def display_table_identity(
    table_id: str,
    *,
    config: Any | None = None,
    active_workspace_id: str | None = None,
    spark_session=None,
    context=None,
) -> str:
    """Return a readable table label without forcing Catalogue registration."""
    raw_value = str(table_id or "").strip()
    if not raw_value:
        return raw_value
    identity = _CURRENT_TABLE_IDENTITIES.get(raw_value)
    if identity is None and config is not None and active_workspace_id is not None:
        try:
            identity = resolve_catalogue_table_identity(
                config,
                active_workspace_id,
                raw_value,
                spark_session=spark_session,
                context=context,
            )
        except Exception:
            identity = None
    if identity is None:
        return raw_value
    parts = (identity.get("store"), identity.get("schema"), identity.get("table_name"))
    label = ".".join(str(part).strip() for part in parts if str(part or "").strip())
    return label or raw_value


def print_guardrail_result(
    name: str,
    result: Mapping[str, Any],
    *,
    verbose: bool,
    table_id: str | None = None,
    source_table_id: str | None = None,
    target_table_id: str | None = None,
    config: Any | None = None,
    active_workspace_id: str | None = None,
    spark_session=None,
    context=None,
) -> None:
    """Print one concise, normalized public Guardrail outcome."""
    if not verbose:
        return

    def _display_label(value: str | None) -> str | None:
        if not value:
            return None
        return display_table_identity(
            value,
            config=config,
            active_workspace_id=active_workspace_id,
            spark_session=spark_session,
            context=context,
        )
    raw_status = str(result.get("status") or "skipped").strip().lower()
    status = {
        "passed": "PASS",
        "pass": "PASS",
        "warning": "WARN",
        "warn": "WARN",
        "failed": "BLOCK" if not result.get("can_continue", False) else "WARN",
        "block": "BLOCK",
        "blocked": "BLOCK",
        "skipped": "SKIPPED",
    }.get(raw_status, raw_status.upper())
    print(f"FabricOps Check → {name}")
    if table_id:
        print(f"  Table  {_display_label(table_id)}")
    if source_table_id:
        print(f"  Source {_display_label(source_table_id)}")
    if target_table_id:
        print(f"  Target {_display_label(target_table_id)}")
    print(f"  Result {status}")


def validate_freshness_parameters(parameters):
    """Validate an explicit evidence method, scope, and positive age threshold."""
    if not isinstance(parameters, dict):
        raise ValueError("Freshness parameters must be an object.")
    method = parameters.get("evidence_method")
    if method != "metadata":
        raise ValueError("Freshness requires metadata-only evidence; use Data Quality for timestamp-column checks.")
    age = parameters.get("maximum_age")
    if type(age) not in {int, float} or not math.isfinite(age) or age <= 0:
        raise ValueError("Freshness maximum_age must be finite and positive.")
    if parameters.get("maximum_age_unit") not in {"minutes", "hours", "days"}:
        raise ValueError("Freshness maximum_age_unit must be minutes, hours, or days.")
    scope = parameters.get("evaluation_scope")
    if scope != "full_dataset":
        raise ValueError("Metadata Freshness describes the full physical source.")
    if "freshness_column" in parameters:
        raise ValueError("Freshness cannot use a timestamp column; author a Data Quality rule instead.")
    return dict(parameters)


def _freshness_timestamp(value):
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time())
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("Timestamp is absent or invalid.")
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def collect_freshness_evidence(parameters, *, dataframe=None, source=None, spark_session=None):
    """Observe only the selected current source and explicit scope.

    Delta history supplies physical-table modification metadata. Files use every
    resolved member's modification time;
    directories are recursively expanded, wildcards resolve before evaluation,
    and hidden Spark control files are excluded. The oldest member governs the
    collection so one recent file cannot hide stale members. No business-event
    time is inferred from filesystem timestamps.
    """
    params = validate_freshness_parameters(parameters)
    source = dict(source or {})
    evidence = {"evidence_method": params["evidence_method"], "evaluation_scope": params["evaluation_scope"],
                "observed_at": datetime.now(UTC).isoformat(), "source": source,
                "outcome": "unavailable", "latest_value": None}
    try:
        if source.get("source_type") == "file":
            selection_options = {"pathGlobFilter", "modifiedBefore", "modifiedAfter", "recursiveFileLookup", "ignoreMissingFiles", "ignoreCorruptFiles"}
            if selection_options.intersection(source.get("reader_options") or {}):
                return {**evidence, "reason": "Reader selection options require reader-resolved file membership; metadata evidence is unavailable."}
            path = source.get("resolved_path")
            if not path:
                return {**evidence, "reason": "Resolved file source is unavailable."}
            jvm = spark_session._jvm
            root = jvm.org.apache.hadoop.fs.Path(path)
            fs = root.getFileSystem(spark_session._jsc.hadoopConfiguration())
            pending = list(fs.globStatus(root) or [])
            members = {}
            while pending:
                entry = pending.pop()
                name = entry.getPath().getName()
                if name.startswith(("_", ".")):
                    continue
                if entry.isDirectory():
                    pending.extend(fs.listStatus(entry.getPath()))
                else:
                    members[str(entry.getPath())] = int(entry.getModificationTime())
            if not members:
                return {**evidence, "reason": "File selector resolved no data files."}
            records = sorted(members.items())
            latest = datetime.fromtimestamp(min(members.values()) / 1000, UTC)
            evidence.update(file_count=len(members), members=records,
                members_sha256=hashlib.sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest(),
                aggregation="oldest_member_modification", scan_required=False)
        elif source.get("store_type") in {"lakehouse", "warehouse"}:
            from delta.tables import DeltaTable
            path = source.get("resolved_path")
            if not path:
                return {**evidence, "reason": "Physical table path is unavailable."}
            from pyspark.sql import functions as F
            history = DeltaTable.forPath(spark_session, path).history()
            required_history_fields = {"operation", "version", "timestamp"}
            if not required_history_fields.issubset(set(history.columns)):
                return {**evidence, "reason": "Delta transaction history lacks required operation, version, or timestamp metadata."}
            updates = history.filter(F.col("operation").isin("WRITE", "MERGE", "UPDATE", "DELETE", "STREAMING UPDATE", "CREATE TABLE AS SELECT", "CREATE OR REPLACE TABLE AS SELECT", "RESTORE"))
            row = updates.orderBy(F.col("version").desc()).first()
            if row is None:
                return {**evidence, "reason": "Reliable data update history is unavailable."}
            latest = row["timestamp"]
            evidence.update(table_version=int(row["version"]), operation=row["operation"], scan_required=False)
        else:
            return {**evidence, "reason": "Reliable physical-table update metadata is unsupported for this source."}
        evidence.update(outcome="available", latest_value=_freshness_timestamp(latest).isoformat())
    except (ValueError, TypeError, OverflowError):
        evidence.update(outcome="invalid", reason="Freshness timestamp evidence is invalid.")
    except Exception as exc:
        evidence.update(outcome="unavailable", reason="Source evidence could not be read.", error_type=type(exc).__name__)
    return evidence


def evaluate_freshness_evidence(evidence, parameters, *, action, reference_time=None):
    """Return an auditable Warn/Block outcome without switching evidence methods."""
    params = validate_freshness_parameters(parameters)
    if action not in {"Warn", "Block"}:
        raise ValueError("Freshness action must be Warn or Block.")
    now = _freshness_timestamp(reference_time) if reference_time else datetime.now(UTC)
    age = params["maximum_age"] * {"minutes": 60, "hours": 3600, "days": 86400}[params["maximum_age_unit"]]
    minimum = now - timedelta(seconds=age)
    outcome = evidence.get("outcome", "unavailable")
    reason = evidence.get("reason", "")
    if any(evidence.get(key) != params[key] for key in ("evidence_method", "evaluation_scope")):
        outcome, reason = "invalid", "Evidence method or scope differs from the frozen rule."
    if outcome == "available" and evidence.get("aggregation") == "oldest_member_modification":
        try:
            members = evidence.get("members")
            if not members:
                raise ValueError("Resolved file membership is missing.")
            if any(datetime.fromtimestamp(stamp / 1000, UTC) > now for _path, stamp in members):
                outcome, reason = "invalid", "A resolved file modification timestamp is in the future."
        except (ValueError, TypeError, OverflowError, OSError):
            outcome, reason = "invalid", "Resolved file modification timestamps are invalid."
    passed = False
    if outcome == "available":
        try:
            latest = _freshness_timestamp(evidence.get("latest_value"))
            if latest > now:
                outcome, reason = "invalid", "Source timestamp is in the future."
            else:
                passed = latest >= minimum
                reason = "Source is fresh." if passed else "Source is older than the configured maximum age."
        except (ValueError, TypeError, OverflowError):
            outcome, reason = "invalid", "Source timestamp is invalid."
    return {"guardrail_type": "freshness", "rule_type": "freshness", "action": action,
        "status": "passed" if passed else "warning" if action == "Warn" else "failed",
        "can_continue": passed or action == "Warn", "evidence_outcome": outcome,
        "reason": reason, "expected": {**params, "required_min_value": minimum.isoformat()},
        "actual": dict(evidence), "checks": [{"check": "freshness", "passed": passed, "evidence_outcome": outcome}]}


def get_current_freshness_evidence(
    *, workspace_id: str, activity_id: str, table_id: str
) -> dict[str, Any]:
    """Return current-run freshness evidence for one governed table."""
    key = (workspace_id, activity_id, table_id)
    if key not in _CURRENT_FRESHNESS_EVIDENCE:
        raise ValueError(
            f"No current freshness evidence exists for {table_id!r}; call orchestrate_read() first."
        )
    return _CURRENT_FRESHNESS_EVIDENCE[key]


def lineage_id(*, activity_id: str, table_id: str, pipeline_role: str) -> str:
    """Return the deterministic identity for pipeline participation."""
    values = {
        "activity_id": str(activity_id or "").strip(),
        "table_id": str(table_id or "").strip(),
        "pipeline_role": str(pipeline_role or "").strip().lower(),
    }
    if not values["activity_id"] or not values["table_id"]:
        raise ValueError("activity_id and table_id must be non-empty strings.")
    if values["pipeline_role"] not in {"source", "target"}:
        raise ValueError("pipeline_role must be source or target.")
    return hashlib.sha256(
        json.dumps(values, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def persist_lineage_participation(
    *,
    table_id: str,
    pipeline_role: str,
    activity_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> str:
    """Upsert one canonical source or target participant for an activity."""
    if not persistence_permitted(context):
        raise RuntimeError("Dry Run cannot commit Lineage.")
    config, active_workspace_id, resolved_context = resolve_fabric_context(context=context)
    audit = build_pipeline_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=resolved_context)
    effective_activity_id = str(activity_id or audit["_activity_id"]).strip()
    audit["_activity_id"] = effective_activity_id
    identifier = lineage_id(
        activity_id=effective_activity_id,
        table_id=table_id,
        pipeline_role=pipeline_role,
    )
    record = coerce_metadata_row_types(
        _LINEAGE_TABLE,
        {
            "lineage_id": identifier,
            "table_id": str(table_id).strip(),
            "table_name": _CURRENT_TABLE_IDENTITIES.get(str(table_id), {}).get("table_name") or resolve_catalogue_table_identity(config, active_workspace_id, table_id, context=resolved_context).get("table_name"),
            "workspace_id": active_workspace_id,
            "pipeline_role": str(pipeline_role).strip().lower(),
            **audit,
        },
    )
    from ..config.metadata_schemas import metadata_table_schema_registry
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - Fabric/Delta runtime dependency
        raise RuntimeError("Delta Lake merge support is required for idempotent METADATA_DATA_LINEAGE writes.") from exc
    spark = get_spark_session(context=resolved_context)
    frame = spark.createDataFrame([record], schema=metadata_table_schema_registry()[_LINEAGE_TABLE])
    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        "Metadata",
        _LINEAGE_TABLE,
        metadata_table_physical_schema(config, _LINEAGE_TABLE),
        context=resolved_context,
    )
    (
        retry_delta_metadata(lambda: DeltaTable.forPath(spark, path)
        .alias("target")
        .merge(
            frame.alias("source"),
            "target.workspace_id = source.workspace_id AND target.lineage_id = source.lineage_id",
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute())
    )
    return identifier


def resolve_physical_table_identity(
    config: Any,
    active_workspace_id: str,
    *,
    store: Any,
    schema: Any,
    table_name: Any,
) -> dict[str, str | None]:
    """Resolve one configured table to its canonical physical identity."""
    if not isinstance(store, str) or not store.strip():
        raise ValueError("store must be a non-empty string.")
    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name must be a non-empty string.")
    store_key = store.strip()
    configured_store = get_store(config, active_workspace_id, store_key)
    # The execution workspace selects the logical store mapping. The configured
    # FabricStore owns the physical workspace/item location and may be remote.
    store_kind = str(getattr(configured_store, "kind", "")).strip().lower()
    if store_kind == "lakehouse":
        if getattr(configured_store, "schema_enabled", False) and schema is None and not getattr(configured_store, "schema", None):
            raise ValueError(
                f"schema is required for schema-enabled Lakehouse store '{store_key}'; "
                "pass schema or configure a default schema."
            )
        normalized_table, normalized_schema, _path = resolve_lakehouse_table_location(
            configured_store, table_name, schema
        )
        if getattr(configured_store, "schema_enabled", False) and normalized_schema is None:
            raise ValueError(
                f"schema is required for schema-enabled Lakehouse store '{store_key}'; "
                "pass schema or configure a default schema."
            )
    elif store_kind == "warehouse":
        configured_schema = schema if schema is not None else getattr(configured_store, "schema", None)
        if configured_schema is None or not str(configured_schema).strip():
            raise ValueError(
                f"schema is required for Warehouse store '{store_key}'; "
                "pass schema or configure a default schema."
            )
        normalized_schema, normalized_table, _object_name = resolve_warehouse_table_location(
            configured_store, configured_schema, table_name, warehouse_name=configured_store.key
        )
    else:
        raise ValueError(
            f"Store '{store_key}' has unsupported kind {store_kind or '<blank>'!r}; "
            "supported kinds are: lakehouse, warehouse."
        )
    identity = {
        "table_id": build_table_id(store_kind, store_key, normalized_schema, normalized_table),
        "store": store_key,
        "schema": normalized_schema,
        "table_name": normalized_table,
        "store_kind": store_kind,
    }
    _CURRENT_TABLE_IDENTITIES[str(identity["table_id"])] = identity
    return identity


def resolve_profiled_columns(df, exclude_columns: list[str] | set[str] | None = None) -> list[str]:
    """Return non-technical column names from a Spark DataFrame."""
    excluded = set(_DEFAULT_PROFILE_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(exclude_columns)
    return [
        name
        for name, _dtype in df.dtypes
        if name not in excluded and not any(str(name).startswith(prefix) for prefix in _DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]


FREQUENCY_PROFILE_COLUMNS = [
    "COLUMN_NAME",
    "DATA_TYPE",
    "VALUE",
    "FREQUENCY_COUNT",
    "FREQUENCY_PERCENT",
    "FREQUENCY_RANK",
    "PROFILED_ROW_COUNT",
    "PROFILED_NON_NULL_COUNT",
]


def build_frequency_distribution_dataframe(df, *, columns=None, top_n: int | None = None):
    """Return exact value-frequency rows for selected Spark DataFrame columns."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    from pyspark.sql.types import ArrayType, BinaryType, MapType, StructType
    from pyspark.sql.window import Window

    if top_n is not None and top_n <= 0:
        raise ValueError("top_n must be greater than zero when supplied.")

    fields = {field.name: field for field in df.schema.fields}
    if columns is None:
        selected_columns = [
            name
            for name in resolve_profiled_columns(df)
            if not isinstance(fields[name].dataType, ArrayType | MapType | StructType | BinaryType)
        ]
    else:
        selected_columns = list(columns)
        missing = [name for name in selected_columns if name not in fields]
        if missing:
            raise ValueError(f"Requested columns do not exist: {', '.join(missing)}")

    if not selected_columns:
        schema = T.StructType(
            [
                T.StructField("COLUMN_NAME", T.StringType(), False),
                T.StructField("DATA_TYPE", T.StringType(), False),
                T.StructField("VALUE", T.StringType(), True),
                T.StructField("FREQUENCY_COUNT", T.LongType(), False),
                T.StructField("FREQUENCY_PERCENT", T.DoubleType(), True),
                T.StructField("FREQUENCY_RANK", T.IntegerType(), False),
                T.StructField("PROFILED_ROW_COUNT", T.LongType(), False),
                T.StructField("PROFILED_NON_NULL_COUNT", T.LongType(), False),
            ]
        )
        return df.sparkSession.createDataFrame([], schema)

    def column(name: str):
        return F.col(f"`{name.replace('`', '``')}`")

    metric_exprs = [F.count(F.lit(1)).cast("long").alias("PROFILED_ROW_COUNT")]
    for column_name in selected_columns:
        metric_exprs.append(
            F.count(column(column_name)).cast("long").alias(f"__{column_name}__PROFILED_NON_NULL_COUNT")
        )
    metrics_df = df.agg(*metric_exprs)
    row_count = F.col("PROFILED_ROW_COUNT")
    branches = []
    rank_window = Window.orderBy(F.col("FREQUENCY_COUNT").desc(), F.col("VALUE").asc_nulls_first())
    for column_name in selected_columns:
        value = column(column_name).cast("string")
        grouped = (
            df.groupBy(value.alias("VALUE"))
            .agg(F.count(F.lit(1)).cast("long").alias("FREQUENCY_COUNT"))
            .crossJoin(metrics_df)
            .withColumn(
                "FREQUENCY_PERCENT",
                F.when(row_count == 0, F.lit(0.0)).otherwise(
                    F.round((F.col("FREQUENCY_COUNT").cast("double") / row_count.cast("double")) * 100, 3)
                ),
            )
            .withColumn("FREQUENCY_RANK", F.row_number().over(rank_window))
        )
        if top_n is not None:
            grouped = grouped.where(F.col("FREQUENCY_RANK") <= F.lit(top_n))
        branches.append(
            grouped.select(
                F.lit(column_name).alias("COLUMN_NAME"),
                F.lit(fields[column_name].dataType.simpleString()).alias("DATA_TYPE"),
                F.col("VALUE"),
                F.col("FREQUENCY_COUNT"),
                F.col("FREQUENCY_PERCENT"),
                F.col("FREQUENCY_RANK"),
                F.col("PROFILED_ROW_COUNT"),
                F.col(f"__{column_name}__PROFILED_NON_NULL_COUNT").alias("PROFILED_NON_NULL_COUNT"),
            ).select(*FREQUENCY_PROFILE_COLUMNS)
        )

    return reduce(lambda left, right: left.unionByName(right), branches).select(*FREQUENCY_PROFILE_COLUMNS)


PROFILE_DATAFRAME_COLUMNS = [
    "COLUMN_NAME",
    "DATA_TYPE",
    "ROW_COUNT",
    "NON_NULL_COUNT",
    "NULL_COUNT",
    "NULL_PERCENT",
    "DISTINCT_COUNT",
    "DISTINCT_PERCENT",
    "MEAN",
    "STDDEV",
    "MIN_VALUE",
    "PERCENTILE_25",
    "MEDIAN",
    "PERCENTILE_75",
    "MAX_VALUE",
]


def _profile_column_expr(name: str):
    """Return a safely quoted Spark column expression."""
    from pyspark.sql import functions as F

    return F.col(f"`{name.replace('`', '``')}`")


def _profile_percent_expr(numerator, denominator):
    """Return a rounded percentage expression protected against zero rows."""
    from pyspark.sql import functions as F

    return F.when(denominator == 0, F.lit(0.0)).otherwise(F.round((numerator.cast("double") / denominator.cast("double")) * F.lit(100.0), 3))


def build_profile_dataframe(df, *, exclude_columns=None):
    """Return structural and statistical profile rows for a Spark DataFrame."""
    from pyspark.sql import functions as F
    from pyspark.sql.types import DateType, NumericType, StringType, TimestampNTZType, TimestampType

    eligible_columns = resolve_profiled_columns(df, exclude_columns=exclude_columns)
    if not eligible_columns:
        raise ValueError("No eligible non-technical columns found for metadata profiling.")

    fields = {field.name: field for field in df.schema.fields}
    agg_exprs = [F.count(F.lit(1)).cast("long").alias("__ROW_COUNT")]

    for column_name in eligible_columns:
        col = _profile_column_expr(column_name)
        data_type = fields[column_name].dataType
        prefix = f"__{column_name}__"
        agg_exprs.extend([
            F.count(col).cast("long").alias(f"{prefix}NON_NULL_COUNT"),
            F.sum(col.isNull().cast("long")).cast("long").alias(f"{prefix}NULL_COUNT"),
            F.count_distinct(col).cast("long").alias(f"{prefix}DISTINCT_COUNT"),
        ])
        if isinstance(data_type, NumericType):
            agg_exprs.extend([
                F.avg(col).cast("double").alias(f"{prefix}MEAN"),
                F.stddev_samp(col).cast("double").alias(f"{prefix}STDDEV"),
                F.min(col).cast("string").alias(f"{prefix}MIN_VALUE"),
                F.percentile(col, [0.25, 0.5, 0.75]).alias(f"{prefix}PERCENTILES"),
                F.max(col).cast("string").alias(f"{prefix}MAX_VALUE"),
            ])
        elif isinstance(data_type, DateType | TimestampType | TimestampNTZType | StringType):
            agg_exprs.extend([
                F.min(col).cast("string").alias(f"{prefix}MIN_VALUE"),
                F.max(col).cast("string").alias(f"{prefix}MAX_VALUE"),
            ])

    agg_df = df.agg(*agg_exprs)
    row_count = F.col("__ROW_COUNT")
    rows = []
    for column_name in eligible_columns:
        data_type = fields[column_name].dataType
        prefix = f"__{column_name}__"
        non_null_count = F.coalesce(F.col(f"{prefix}NON_NULL_COUNT"), F.lit(0)).cast("long")
        null_count = F.coalesce(F.col(f"{prefix}NULL_COUNT"), F.lit(0)).cast("long")
        distinct_count = F.coalesce(F.col(f"{prefix}DISTINCT_COUNT"), F.lit(0)).cast("long")
        percentile = F.col(f"{prefix}PERCENTILES") if isinstance(data_type, NumericType) else None
        supports_min_max = isinstance(data_type, NumericType | DateType | TimestampType | TimestampNTZType | StringType)
        rows.append(agg_df.select(
            F.lit(column_name).alias("COLUMN_NAME"),
            F.lit(data_type.simpleString()).alias("DATA_TYPE"),
            row_count.cast("long").alias("ROW_COUNT"),
            non_null_count.alias("NON_NULL_COUNT"),
            null_count.alias("NULL_COUNT"),
            _profile_percent_expr(null_count, row_count).alias("NULL_PERCENT"),
            distinct_count.alias("DISTINCT_COUNT"),
            _profile_percent_expr(distinct_count, row_count).alias("DISTINCT_PERCENT"),
            (F.col(f"{prefix}MEAN") if isinstance(data_type, NumericType) else F.lit(None).cast("double")).alias("MEAN"),
            (F.col(f"{prefix}STDDEV") if isinstance(data_type, NumericType) else F.lit(None).cast("double")).alias("STDDEV"),
            (F.col(f"{prefix}MIN_VALUE") if supports_min_max else F.lit(None).cast("string")).alias("MIN_VALUE"),
            (percentile.getItem(0).cast("double") if percentile is not None else F.lit(None).cast("double")).alias("PERCENTILE_25"),
            (percentile.getItem(1).cast("double") if percentile is not None else F.lit(None).cast("double")).alias("MEDIAN"),
            (percentile.getItem(2).cast("double") if percentile is not None else F.lit(None).cast("double")).alias("PERCENTILE_75"),
            (F.col(f"{prefix}MAX_VALUE") if supports_min_max else F.lit(None).cast("string")).alias("MAX_VALUE"),
        ))

    out = rows[0]
    for row in rows[1:]:
        out = out.unionByName(row)
    return out.select(*PROFILE_DATAFRAME_COLUMNS)

PROFILED_TABLE = "METADATA_DATA_PROFILED"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
DATA_CONTRACT_TABLE = "METADATA_DATA_CONTRACT"




# ---------------------------------------------------------------------------
# Public API layer
# ---------------------------------------------------------------------------








def _result_status(result: Mapping[str, Any] | None) -> str:
    """Return a normalized guardrail result status."""
    return str(
        (result or {}).get("status")
        or (result or {}).get("freshness_status")
        or (result or {}).get("stability_status")
        or "not_run"
    ).lower()



def _result_reason(result: Mapping[str, Any] | None) -> str:
    """Return the clearest human-readable reason from a result."""
    if not result:
        return ""
    return str(
        result.get("reason")
        or result.get("message")
        or result.get("freshness_message")
        or result.get("stability_message")
        or ""
    )
def observation_rows(dataframe: Any) -> list[dict[str, Any]]:
    """Return canonical observation rows as dictionaries."""
    values = dataframe.collect() if hasattr(dataframe, "collect") else dataframe
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in values or []]


def _latest_source_target_observation(
    history: Any,
    *,
    source_table_id: str,
    target_table_id: str,
    workspace_id: str,
) -> list[dict[str, Any]]:
    """Return the latest committed baseline for one source-to-target relationship."""
    candidates = [
        row
        for row in _processing_state_rows(history)
        if str(row.get("source_table_id") or "") == source_table_id
        and str(row.get("target_table_id") or "") == target_table_id
        and str(row.get("workspace_id") or "") == workspace_id
        and row.get("record_type") == "incremental_checkpoint"
        and row.get("status") == "committed"
    ]
    latest_at = max((metadata_timestamp_sort_key(row.get("_committed_at")) for row in candidates), default=None)
    return [row for row in candidates if metadata_timestamp_sort_key(row.get("_committed_at")) == latest_at]


def _progress_key(value: Any, *, timestamp: bool = False) -> tuple[int, Any]:
    """Return a stable ordering key for numeric, temporal, or textual progress."""
    text = str(value)
    try:
        return (0, Decimal(text))
    except InvalidOperation:
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            if timestamp:
                raise ValueError(
                    f"Committed timestamp watermark {text!r} is ambiguous. "
                    "Existing progress is preserved; the timestamp boundary cannot be interpreted safely."
                )
            return (2, text)
        if parsed.tzinfo is None:
            if timestamp:
                raise ValueError(
                    f"Committed timestamp watermark {text!r} has no timezone. "
                    "Existing progress is preserved; the timestamp boundary cannot be interpreted safely."
                )
            return (1, text)
        return (1, parsed.astimezone(UTC))


def _looks_like_naive_timestamp(value: Any) -> bool:
    """Recognize timestamp-shaped strings without assigning them a timezone."""
    text = str(value or "")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return False
    return parsed.tzinfo is None and ("T" in text or (len(text) >= 19 and text[10] == " "))


def _watermark_timestamp(value: Any) -> str:
    """Serialize Spark-collected TimestampType values as unambiguous UTC ISO text."""
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            instant = value.astimezone(UTC)
        else:
            # PySpark collects TimestampType in the Python process's local zone,
            # independently of spark.sql.session.timeZone.
            instant = value.astimezone(UTC)
        return instant.isoformat(timespec="microseconds").replace("+00:00", "Z")
    text = str(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"Timestamp watermark {text!r} is timezone-naive or invalid; "
            "set an explicit timezone before retrying."
        ) from exc
    if parsed.tzinfo is None:
        raise ValueError(
            f"Timestamp watermark {text!r} is timezone-naive; its instant cannot be inferred."
        )
    return parsed.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _compact_value(value: Any, *, timestamp: bool = False, timestamp_ntz: bool = False) -> str | None:
    if value is None:
        return None
    if timestamp_ntz:
        return value.isoformat(timespec="microseconds") if isinstance(value, datetime) else str(value)
    if timestamp or isinstance(value, datetime):
        return _watermark_timestamp(value)
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _publication_value(column, datatype):
    """Canonicalize nested maps without collecting business rows to the driver."""
    from pyspark.sql import functions as F
    from pyspark.sql.types import ArrayType, MapType, StructType

    if isinstance(datatype, MapType):
        return F.array_sort(F.transform(F.map_entries(column), lambda entry: F.struct(
            _publication_value(entry["key"], datatype.keyType).alias("key"),
            _publication_value(entry["value"], datatype.valueType).alias("value"),
        )))
    if isinstance(datatype, ArrayType):
        return F.transform(column, lambda item: _publication_value(item, datatype.elementType))
    if isinstance(datatype, StructType):
        return F.when(column.isNull(), F.lit(None)).otherwise(F.struct(*[
            _publication_value(column[field.name], field.dataType).alias(field.name) for field in sorted(datatype.fields, key=lambda item: item.name)
        ]))
    return column


def row_hash_expression(dataframe, *, values=None):
    """Build a canonical typed hash expression, optionally for resulting SCD values.

    This internal expression ignores any supplied hash. Only FabricOps-owned audit,
    SCD lifecycle and reserved DQ/FabricOps fields are excluded; source Job IDs,
    ingestion timestamps and similarly named business values remain significant.
    """
    from pyspark.sql import functions as F
    from pyspark.sql.types import ArrayType, MapType, StructType

    def descriptor(datatype):
        if isinstance(datatype, StructType):
            return {"struct": [(item.name, descriptor(item.dataType))
                               for item in sorted(datatype.fields, key=lambda item: item.name)]}
        if isinstance(datatype, ArrayType):
            return {"array": descriptor(datatype.elementType)}
        if isinstance(datatype, MapType):
            return {"map": [descriptor(datatype.keyType), descriptor(datatype.valueType)]}
        return datatype.simpleString()

    values = values or {}
    names = sorted(name for name in dataframe.columns
                   if name not in {*_TARGET_AUDIT_COLUMNS, *_SCD2_LIFECYCLE_COLUMNS, "_row_hash"}
                   and not name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES))
    if not names or len(dataframe.columns) != len(set(dataframe.columns)):
        raise ValueError("A managed write requires unique named incoming data columns.")
    schema = json.dumps({"version": 1, "columns": [(name, descriptor(dataframe.schema[name].dataType))
                                                for name in names]}, separators=(",", ":"), ensure_ascii=True)
    values = F.struct(*[_publication_value(values.get(name, F.col("`" + name.replace("`", "``") + "`")),
                                         dataframe.schema[name].dataType).alias(name) for name in names])
    encoded = F.to_json(values, options={"ignoreNullFields": "false", "timeZone": "UTC",
                                        "timestampFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX",
                                        "timestampNTZFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"})
    return F.sha2(F.concat(F.lit(schema + "\n"), encoded), 256)


def add_row_hash(dataframe):
    """Recalculate the mandatory hash of final incoming data without a Spark action."""
    return dataframe.withColumn("_row_hash", row_hash_expression(dataframe))


def validate_target_row_hash(identity, *, context, cache_hashes=False):
    """Fail explicitly on legacy targets; overwrite is the complete replacement boundary."""
    from fabricops_kit.io import read_warehouse_table

    try:
        if identity.get("store_type") == "lakehouse":
            target = read_lakehouse_table(identity["table_name"], store=identity["store"],
                                          schema=identity.get("schema"), context=context)
        else:
            target = read_warehouse_table(identity["schema"], identity["table_name"],
                                          store=identity["store"], context=context)
    except Exception as exc:
        if is_table_not_found_error(exc):
            return
        raise
    if "_row_hash" not in target.columns:
        raise ValueError("Existing target has no _row_hash. Non-overwrite publication requires valid hashes "
                         "for every existing row; the target has been preserved.")
    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType
    if not isinstance(target.schema["_row_hash"].dataType, StringType):
        raise ValueError("Existing target _row_hash must use the canonical SHA256 string type; reconcile before publication.")
    hashes = target.select("_row_hash")
    if cache_hashes:
        from pyspark import StorageLevel
        hashes.persist(StorageLevel.MEMORY_AND_DISK)
    try:
        if hashes.where(F.col("_row_hash").isNull() | ~F.col("_row_hash").rlike("^[0-9a-f]{64}$")).limit(1).count():
            raise ValueError("Existing target has missing or invalid historical _row_hash values; reconcile before publication.")
    except BaseException:
        if cache_hashes:
            hashes.unpersist()
        raise
    return hashes


def filter_unpublished_rows(dataframe, identity, *, context, target_hashes=None):
    """Compare only hash projections in Spark for the exclusively owned pipeline target."""
    from fabricops_kit.io import read_warehouse_table
    distinct = dataframe.dropDuplicates(["_row_hash"])
    if target_hashes is not None:
        return distinct.join(target_hashes, on="_row_hash", how="left_anti").select(
            *["`" + name.replace("`", "``") + "`" for name in dataframe.columns])
    try:
        if identity.get("store_type") == "lakehouse":
            target = read_lakehouse_table(identity["table_name"], store=identity["store"],
                                          schema=identity.get("schema"), context=context)
        else:
            target = read_warehouse_table(identity["schema"], identity["table_name"],
                                          store=identity["store"], context=context)
    except Exception as exc:
        if is_table_not_found_error(exc):
            return distinct
        raise
    return distinct.join(target.select("_row_hash"), on="_row_hash", how="left_anti").select(
        *["`" + name.replace("`", "``") + "`" for name in dataframe.columns])


def row_hash_totals(dataframe):
    """Reduce cached hashes to a bounded multiset fingerprint, preserving multiplicity."""
    from pyspark.sql import functions as F
    return dataframe.select(F.col("_row_hash").alias("hash")).agg(F.count("*").alias("rows"), *[
        F.sum(F.conv(F.substring("hash", offset, 16), 16, 10).cast("decimal(38,0)")).alias(f"h{offset}")
        for offset in (1, 17, 33, 49)
    ]).first().asDict()


def validate_source_drift_configuration(configuration=None):
    """Validate independent, opt-in Engineering Source Drift settings."""
    result = {"source_drift_enabled": False, "source_drift_interval_days": 1, "source_drift_block": True}
    if configuration is not None:
        if not isinstance(configuration, dict) or set(configuration) - set(result):
            raise ValueError("Invalid Source Drift configuration.")
        result.update(configuration)
    for name in ("source_drift_enabled", "source_drift_block"):
        if type(result[name]) is not bool:
            raise ValueError(f"{name} must be a boolean.")
    if type(result["source_drift_interval_days"]) is not int or result["source_drift_interval_days"] <= 0:
        raise ValueError("source_drift_interval_days must be a positive integer.")
    return result


def source_snapshot_context(identity, *, context):
    """Bind shared history to an execution workspace and exact physical source."""
    plan = context["execution_plan"]
    physical = pipeline_physical_bindings({identity["table_id"]: identity},
        config=context["config"], workspace_id=plan.workspace_id)[identity["table_id"]]
    descriptor = {"workspace_id": plan.workspace_id, "table_id": identity["table_id"], "physical": physical}
    return _metadata_hash(descriptor), descriptor


def _source_snapshot_state(context):
    """Keep source hash rows distributed and history independent of Pipeline ID."""
    from pyspark.sql import functions as F
    try:
        return read_lakehouse_table(_PROCESSING_STATE_TABLE, store="Metadata",
            schema=metadata_table_physical_schema(context["config"], _PROCESSING_STATE_TABLE), context=context).where(
                F.col("workspace_id") == context["execution_plan"].workspace_id)
    except Exception as exc:
        if not is_table_not_found_error(exc):
            raise
        return get_spark_session(context=context).createDataFrame([], metadata_table_schema_registry()[_PROCESSING_STATE_TABLE])


def _source_snapshot_keys(identity, context):
    """Use authored Grain or source processing keys without inferring identity from values."""
    plan = context["execution_plan"]
    contract = json.loads(plan.contracts_json).get(identity["table_id"])
    payload = (contract or {}).get("contract_payload") or {}
    if not payload and (contract or {}).get("contract_payload_json"):
        payload = json.loads(contract["contract_payload_json"])
    names = {column["column_id"]: column["column_name"] for column in payload.get("table", {}).get("columns", [])}
    for rule in payload.get("guardrails", []):
        if rule.get("guardrail_type") == "grain" and rule.get("is_active", True):
            return [names.get(name, name) for name in rule.get("rule_parameters", {}).get("columns", [])]
    processing_identity = identity
    if "load_strategy_parameters_json" not in identity:
        try:
            processing_identity = resolve_catalogue_table_identity(context["config"], plan.workspace_id,
                identity["table_id"], spark_session=get_spark_session(context=context),
                context={**context, "_pipeline_identities": None})
        except Exception as exc:
            if not (is_table_not_found_error(exc) or (isinstance(exc, ValueError) and
                    str(exc).startswith("No active registered Catalogue table exists for table_id"))):
                raise
            processing_identity = {}
    processing = processing_identity.get("load_strategy_parameters_json") or {}
    if isinstance(processing, str):
        processing = json.loads(processing)
    return list(processing.get("key_columns") or [])


def source_snapshot_projection(dataframe, keys=()):
    """Project deterministic SHA256 identity/content multiplicities in Spark.

    Validated keys identify historical rows. Missing/null/nonunique keys fall
    back to content multisets; no arbitrary old/new pairing claims modifications.
    """
    from functools import reduce
    from pyspark.sql import functions as F
    columns = sorted(name for name in dataframe.columns
                     if name not in {*_TARGET_AUDIT_COLUMNS, *_SCD2_LIFECYCLE_COLUMNS, "_row_hash"}
                     and not name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES))
    content = dataframe.select(*[F.col("`" + name.replace("`", "``") + "`") for name in columns])
    schema = [(name, content.schema[name].dataType.json()) for name in columns]
    keys = list(keys)
    reason = "No authored row key; content multiset comparison."
    if keys and len(keys) == len(set(keys)) and set(keys) <= set(columns):
        key_frame = content.select(*[F.col("`" + name.replace("`", "``") + "`").alias(name) for name in keys])
        nulls = reduce(lambda left, right: left | right, [F.col("`" + name.replace("`", "``") + "`").isNull() for name in keys])
        if key_frame.where(nulls).limit(1).count() or key_frame.groupBy(*[F.col("`" + name.replace("`", "``") + "`") for name in key_frame.columns]).count().where("count > 1").limit(1).count():
            keys = []
            reason = "Authored keys contain null or duplicate values; content multiset comparison."
    else:
        if keys:
            reason = "Authored keys are missing or invalid; content multiset comparison."
        keys = []
    content_hash = row_hash_expression(content)
    if keys:
        key_frame = content.select(*[F.col("`" + name.replace("`", "``") + "`") for name in keys])
        identity_hash = row_hash_expression(key_frame)
        reason = "Historical rows compared by validated unique authored keys."
    else:
        identity_hash = content_hash
    evidence = content.select(identity_hash.alias("partition_value"), content_hash.alias("content_fingerprint"))
    evidence = evidence.groupBy("partition_value", "content_fingerprint").count().withColumnRenamed("count", "row_count")
    return evidence, {"version": 1, "schema": schema, "keys": keys, "identity_reason": reason}


def _source_evidence_totals(evidence):
    """Fingerprint the compact hash multiset and count source rows without driver collection."""
    from pyspark.sql import functions as F
    hashes = evidence.withColumn("_row_hash", F.sha2(F.to_json(F.struct(
        "partition_value", "content_fingerprint", "row_count")), 256))
    totals = row_hash_totals(hashes)
    rows = evidence.agg(F.sum("row_count").alias("rows")).first()["rows"] or 0
    return {"groups": totals["rows"], "rows": rows,
            "fingerprint": hashlib.sha256(json.dumps(totals, sort_keys=True, default=str).encode()).hexdigest()}


def compare_source_snapshot_evidence(current, previous, *, keyed):
    """Compare compact historical row evidence, retaining only ten hash samples per category."""
    from pyspark.sql import functions as F
    if not keyed:
        current = current.groupBy("content_fingerprint").agg(F.sum("row_count").alias("row_count"))
        previous = previous.groupBy("content_fingerprint").agg(F.sum("row_count").alias("row_count"))
        join_key = "content_fingerprint"
    else:
        join_key = "partition_value"
    before, after = previous.alias("p"), current.alias("c")
    changes = before.join(after, F.col("p." + join_key) == F.col("c." + join_key), "full_outer")
    if keyed:
        categories = {
            "added": (F.col("p.partition_value").isNull(), F.col("c.row_count")),
            "removed": (F.col("c.partition_value").isNull(), F.col("p.row_count")),
            "modified": (F.col("p.partition_value").isNotNull() & F.col("c.partition_value").isNotNull()
                         & (F.col("p.content_fingerprint") != F.col("c.content_fingerprint")), F.lit(1)),
        }
    else:
        delta = F.coalesce(F.col("c.row_count"), F.lit(0)) - F.coalesce(F.col("p.row_count"), F.lit(0))
        categories = {"added": (delta > 0, delta), "removed": (delta < 0, -delta)}
    counts, samples = {"modified_count": 0 if keyed else None}, {}
    for category, (condition, amount) in categories.items():
        affected = changes.where(condition).select(
            F.coalesce(F.col("p." + join_key), F.col("c." + join_key)).alias("identity_hash"),
            F.col("p.content_fingerprint").alias("previous_hash"),
            F.col("c.content_fingerprint").alias("current_hash"), amount.cast("long").alias("affected_rows"))
        counts[category + "_count"] = affected.agg(F.sum("affected_rows").alias("n")).first()["n"] or 0
        samples[category] = [row.asDict() for row in affected.orderBy("identity_hash").limit(10).collect()]
    counts["ambiguous_count"] = counts.get("ambiguous_count", 0) if keyed else counts["removed_count"]
    return {**counts, "samples": samples, "samples_limit": 10,
            "ambiguous_count_overlaps_removed": not keyed}


def _persist_source_snapshot(evidence, header, *, context):
    """Append immutable distributed row evidence, then its completeness manifest."""
    from pyspark.sql import functions as F
    schema = metadata_table_schema_registry()[_PROCESSING_STATE_TABLE]
    row_fields = {**header, "record_type": "source_row_evidence", "snapshot_payload_json": None}
    identity = F.sha2(F.concat_ws(":", F.lit(header["observation_id"]), F.col("partition_value"), F.col("content_fingerprint")), 256)
    frame = evidence.select(*[
        (identity if field.name == "record_id" else F.col(field.name) if field.name in evidence.columns else
         F.lit(row_fields.get(field.name))).cast(field.dataType).alias(field.name) for field in schema])
    write_lakehouse_table(frame, _PROCESSING_STATE_TABLE, store="Metadata",
        schema=metadata_table_physical_schema(context["config"], _PROCESSING_STATE_TABLE), context=context, mode="append", options={"mergeSchema": "true"})
    write_lakehouse_table(get_spark_session(context=context).createDataFrame([header], schema),
        _PROCESSING_STATE_TABLE, store="Metadata", schema=metadata_table_physical_schema(context["config"], _PROCESSING_STATE_TABLE),
        context=context, mode="append")


def _validated_source_snapshot(state, observation_id, *, context_key):
    """Require a complete immutable manifest and matching distributed hash multiset."""
    from pyspark.sql import functions as F
    headers = state.where((F.col("record_type") == "source_snapshot")
        & (F.col("observation_id") == observation_id)).limit(2).collect()
    if len(headers) != 1:
        raise RuntimeError("Source snapshot manifest is missing or ambiguous.")
    header = headers[0].asDict()
    metadata = json.loads(header["snapshot_payload_json"])
    if metadata.get("version") != 2 or metadata.get("context_key") != context_key:
        raise RuntimeError("Source snapshot physical context or version changed.")
    evidence = state.where((F.col("record_type") == "source_row_evidence")
        & (F.col("observation_id") == observation_id)).select("partition_value", "content_fingerprint", "row_count")
    invalid = evidence.where(F.col("row_count").isNull() | (F.col("row_count") <= 0)
        | F.col("partition_value").isNull() | ~F.col("partition_value").rlike("^[0-9a-f]{64}$")
        | F.col("content_fingerprint").isNull() | ~F.col("content_fingerprint").rlike("^[0-9a-f]{64}$"))
    if invalid.limit(1).count() or _source_evidence_totals(evidence) != metadata.get("totals"):
        raise RuntimeError("Source snapshot hash evidence is corrupt or incomplete.")
    if evidence.groupBy("partition_value", "content_fingerprint").count().where("count > 1").limit(1).count():
        raise RuntimeError("Duplicate source hash evidence.")
    if metadata.get("keys") and evidence.groupBy("partition_value").agg(F.sum("row_count").alias("n")).where("n != 1").limit(1).count():
        raise RuntimeError("Keyed source snapshot contains ambiguous identities.")
    return evidence, metadata, header


def _record_source_drift_result(result, *, context, table_id="", table_name="", rule_type="historical_source_content"):
    """Use existing aggregate Guardrail Results without any Contract policy authority."""
    context = {**context, "_fabricops_suppress_io_log": True}
    plan = context["execution_plan"]
    write_guardrail_result_row(spark_session=get_spark_session(context=context), config=context["config"],
        active_workspace_id=plan.workspace_id, run_id=plan.plan_id, dataset_name="", table_name=table_name,
        store_type="", layer="", table_id=table_id, guardrail_type="source_drift", rule_type=rule_type,
        result={**result, "guardrail_rule_id": "pipeline_source_drift_v2:" + rule_type, "guardrail_version": 2,
            "guardrail_type": "source_drift", "rule_context": {"rule_type": rule_type}}, context=context)


def source_drift_requires_intervention(result):
    """Separate historical changes from ordinary additive source growth."""
    return bool(result.get("status") == "observation_failed" or result.get("schema_changed")
        or result.get("removed_count") or result.get("modified_count"))


def observe_full_source(identity, *, dataframe=None, context):
    """Automatically observe a complete source, never the profiling or query scope."""
    plan = context.get("execution_plan")
    policy = validate_source_drift_configuration(getattr(plan, "evidence", {}).get("source_drift_policy"))
    if not policy["source_drift_enabled"]:
        return {"status": "disabled", "can_continue": True, "reason": "Source Drift disabled."}
    from pyspark import StorageLevel
    from pyspark.sql import functions as F
    from fabricops_kit.io import read_warehouse_table
    source_id = identity["table_id"]
    observations = plan.evidence.setdefault("source_drift_observations", {})
    if source_id in observations:
        return observations[source_id]
    context = {**context, "_fabricops_suppress_io_log": True}
    candidates = plan.evidence.setdefault("source_drift_candidates", {})
    evidence = None
    owned_cache = False
    result = {"table_id": source_id, "table_name": identity["table_name"], "pipeline_id": plan.pipeline_id,
              "run_id": plan.plan_id, "added_count": None, "removed_count": None, "modified_count": None,
              "ambiguous_count": None, "samples_limit": 10}
    try:
        context_key, descriptor = source_snapshot_context(identity, context=context)
        state = _source_snapshot_state(context).where(F.col("source_table_id") == source_id)
        head_id = _processing_state_id("source_drift_head", context_key)
        heads = state.where((F.col("record_type") == "source_drift_baseline")
            & (F.col("record_id") == head_id)).limit(2).collect()
        if len(heads) > 1:
            raise RuntimeError("Ambiguous shared source baseline.")
        head = heads[0].asDict() if heads else None
        now = datetime.now(UTC)
        if head:
            if head.get("status") != "committed" or not head.get("observation_id") or head.get("accepted_at") is None:
                raise RuntimeError("Accepted source baseline is incomplete.")
            last = head["accepted_at"]
            last = last.replace(tzinfo=UTC) if last.tzinfo is None else last
            if now - last < timedelta(days=policy["source_drift_interval_days"]):
                result.update(status="not_due", reason="Confirmed source observation interval has not elapsed.",
                    historical_checked=False, context_key=context_key)
                observations[source_id] = {**result, "can_continue": True}
                return observations[source_id]
        previous, previous_meta = None, None
        if head:
            previous, previous_meta, _ = _validated_source_snapshot(state, head["observation_id"], context_key=context_key)
        if dataframe is None:
            dataframe = (read_lakehouse_table(identity["table_name"], store=identity["store"], schema=identity.get("schema"), context=context)
                if (identity.get("store_type") or identity.get("store_kind")) == "lakehouse" else
                read_warehouse_table(identity["schema"], identity["table_name"], store=identity["store"], context=context))
        owned_cache = not dataframe.is_cached
        if owned_cache:
            dataframe.persist(StorageLevel.MEMORY_AND_DISK)
        evidence, metadata = source_snapshot_projection(dataframe, _source_snapshot_keys(identity, context))
        evidence.persist(StorageLevel.MEMORY_AND_DISK)
        metadata.update(version=2, context_key=context_key, physical=descriptor["physical"],
            parent_observation_id=head["observation_id"] if head else None, totals=_source_evidence_totals(evidence))
        metadata = json.loads(json.dumps(metadata))
        schema_changed = bool(previous_meta and metadata["schema"] != previous_meta["schema"])
        keyed = bool(previous_meta and metadata["keys"] and metadata["keys"] == previous_meta["keys"]
            and all(dict(metadata["schema"]).get(key) == dict(previous_meta["schema"]).get(key) for key in metadata["keys"]))
        comparison = (compare_source_snapshot_evidence(evidence, previous, keyed=keyed) if previous is not None else
            {"added_count": None, "removed_count": None, "modified_count": None, "ambiguous_count": None, "samples": {}})
        changed = previous is not None and (schema_changed or any(comparison.get(key) for key in
            ("added_count", "removed_count", "modified_count")))
        observation_id = str(uuid4())
        audit = build_pipeline_audit_fields(config=context["config"], active_workspace_id=plan.workspace_id, runtime_context=context)
        header = {**audit, "record_id": _processing_state_id(context_key, observation_id), "record_type": "source_snapshot",
            "status": "observed", "observation_id": observation_id, "pipeline_id": plan.pipeline_id, "run_id": plan.plan_id,
            "workspace_id": plan.workspace_id, "source_table_id": source_id, "source_table_name": identity["table_name"],
            "observed_at": now, "row_count": metadata["totals"]["rows"], "content_fingerprint": metadata["totals"]["fingerprint"],
            "snapshot_payload_json": json.dumps(metadata, sort_keys=True)}
        if persistence_permitted(context):
            _persist_source_snapshot(evidence, header, context=context)
        candidates[source_id] = header
        result.update(comparison, status="changes_detected" if changed else "no_change" if previous is not None else "baseline_pending",
            changed=bool(changed), historical_checked=previous is not None, schema_changed=schema_changed,
            identity_strategy="key" if keyed or (previous is None and metadata["keys"]) else "content_multiset",
            row_count=metadata["totals"]["rows"], context_key=context_key, observation_id=observation_id,
            reason=("Initial exact snapshot; no historical change counts are known. " if previous is None else
                    "Complete-source comparison. ") + metadata["identity_reason"], baseline_status="pending_finalization")
    except Exception as exc:
        candidates.pop(source_id, None)
        result.update(status="observation_failed", changed=None, historical_checked=False,
            reason="Complete source or accepted snapshot could not be verified; inspect access and snapshot integrity.",
            error_type=type(exc).__name__)
    finally:
        if evidence is not None:
            evidence.unpersist()
        if owned_cache:
            dataframe.unpersist()
    requires_intervention = source_drift_requires_intervention(result)
    addition_only = bool(result.get("changed")) and not requires_intervention
    result.update(requires_intervention=requires_intervention,
        can_continue=not (policy["source_drift_block"] and requires_intervention),
        action="Block" if policy["source_drift_block"] and not addition_only else "Warn",
        severity="blocking" if policy["source_drift_block"] and not addition_only else "warning")
    if result["status"] in {"changes_detected", "observation_failed"}:
        result["investigation_query"] = source_drift_investigation_query(plan, source_id)
    try:
        _record_source_drift_result(result, context=context, table_id=source_id, table_name=identity["table_name"])
    except Exception as exc:
        candidates.pop(source_id, None)
        result.update(status="observation_failed", requires_intervention=True, can_continue=not policy["source_drift_block"],
            action="Block" if policy["source_drift_block"] else "Warn",
            severity="blocking" if policy["source_drift_block"] else "warning",
            reason="Source Drift diagnostics could not be persisted; no baseline will be accepted.", error_type=type(exc).__name__)
    observations[source_id] = result
    return result


def source_drift_investigation_query(plan, source_id, *, evaluation_id=None):
    """Build an executable, scoped next-cell query with actual runtime identifiers."""
    schema = metadata_table_physical_schema(plan.runtime_context["config"], "METADATA_GUARDRAIL_RESULTS")
    return ("from fabricops_kit import read_lakehouse_table\nfrom pyspark.sql import functions as F\n"
            f"diagnostics = read_lakehouse_table('METADATA_GUARDRAIL_RESULTS', store='Metadata', schema={schema!r})\n"
            "display(diagnostics.where(\n"
            f"    (F.col('workspace_id') == {plan.workspace_id!r})\n"
            f"    & (F.col('run_id') == {plan.plan_id!r})\n"
            f"    & ((F.col('table_id') == {source_id!r}) | (F.col('rule_type') == 'pipeline_observation'))\n"
            "    & (F.col('guardrail_type') == 'source_drift')\n"
            f"    & (F.get_json_object('result_payload_json', '$.pipeline_id') == {plan.pipeline_id!r})\n"
            + (f"    & (F.get_json_object('result_payload_json', '$.evaluation_id') == {evaluation_id!r})\n" if evaluation_id else "")
            + ").select('table_name', 'table_id', 'rule_type', 'status', 'can_continue', 'reason', 'result_payload_json', '_committed_at'))")


def evaluate_pipeline_source_drift(plan, *, verbose=False, spark_session=None):
    """Close the Read set and consolidate every source before any target publication."""
    policy = validate_source_drift_configuration(plan.evidence.get("source_drift_policy"))
    if not policy["source_drift_enabled"]:
        return {"status": "disabled", "can_continue": True, "sources": []}
    if "source_drift_decision" in plan.evidence:
        decision = plan.evidence["source_drift_decision"]
        if not decision["can_continue"]:
            error = RuntimeError("Source Drift blocks publication; restore the source or review source_drift_block=False in a new run.")
            error.result = decision
            raise error
        return decision
    identities = json.loads(plan.participants_json)
    source_ids = {tid for tid, identity in identities.items() if "source" in identity["roles"] and identity.get("source_type") != "file"}
    observations = plan.evidence.get("source_drift_observations", {})
    missing = source_ids - set(observations)
    results = [observations[tid] for tid in sorted(source_ids & set(observations))]
    unavailable = bool(missing) or any(row["status"] == "observation_failed" for row in results)
    changed = any(row.get("changed") for row in results)
    requires_intervention = unavailable or any(source_drift_requires_intervention(row) for row in results)
    allowed = not missing and not (policy["source_drift_block"] and requires_intervention)
    decision = {"status": "blocked" if not allowed else "warning" if unavailable or changed else "not_due"
        if not results or all(row["status"] == "not_due" for row in results) else "baseline_pending"
        if any(row["status"] == "baseline_pending" for row in results) else "no_change",
        "can_continue": allowed, "requires_intervention": requires_intervention, "sources": results, "source_ids": sorted(source_ids),
        "missing_source_ids": sorted(missing), "enabled": True, "interval_days": policy["source_drift_interval_days"],
        "block": policy["source_drift_block"], "observed": sum(row["status"] != "not_due" for row in results),
        "skipped": sum(row["status"] == "not_due" for row in results), "baseline_status": "pending_finalization"}
    for name in ("added_count", "removed_count", "modified_count", "ambiguous_count"):
        decision[name] = sum(row[name] for row in results) if results and all(row.get(name) is not None for row in results) else None
    plan.evidence["source_drift_reads_closed"] = True
    context = {**plan.runtime_context, "execution_plan": plan, "_spark_session": spark_session, "_fabricops_suppress_io_log": True}
    try:
        _record_source_drift_result({**decision, "sources": [{k: v for k, v in row.items() if k not in {"samples", "investigation_query"}} for row in results],
            "pipeline_id": plan.pipeline_id, "action": "Block" if not allowed else "Warn",
            "severity": "blocking" if not allowed else "warning", "reason": "All required sources must be read before Write." if missing else "Consolidated complete-source decision."},
            context=context, rule_type="pipeline_observation")
    except Exception as exc:
        unavailable = True
        decision.update(status="observation_failed", can_continue=not policy["source_drift_block"] and not missing,
            diagnostics_error_type=type(exc).__name__)
    if unavailable or not decision["can_continue"]:
        plan.evidence["source_drift_candidates"] = {}
        decision["baseline_status"] = "not_eligible"
    plan.evidence["source_drift_decision"] = decision
    if verbose:
        counts = " · ".join(name.removesuffix("_count").title() + ": " +
            (str(decision[name]) if decision[name] is not None else "unknown") for name in
            ("added_count", "removed_count", "modified_count"))
        print(f"FabricOps SOURCE DRIFT · Sources: {len(source_ids)} · Observed: {decision['observed']} · Skipped: {decision['skipped']}")
        print(counts + f" · Decision: {decision['status']} · Publication: {'Allowed' if decision['can_continue'] else 'Blocked'}")
    if not decision["can_continue"]:
        error = RuntimeError("Source Drift blocks publication. Read every source before any Write; review complete-source diagnostics in a new execution.")
        error.result = decision
        raise error
    return decision


def record_pipeline_publication(target_table_id, status, *, receipt=None, context=None):
    """Retain exact publication outcomes for the final source baseline boundary."""
    plan = (context or {}).get("execution_plan")
    if plan is not None:
        plan.evidence.setdefault("publication_outcomes", {})[target_table_id] = {"status": status, "receipt": receipt}


def accept_pipeline_source_snapshots(plan, *, spark_session=None):
    """Conditionally accept all complete source candidates after verified finalization."""
    candidates = plan.evidence.get("source_drift_candidates", {})
    if not candidates or not plan.permits_persistence:
        plan.evidence.setdefault("source_snapshot_acceptance", {"status": "diagnostic_only" if not plan.permits_persistence else
            "not_due" if plan.evidence.get("source_drift_decision", {}).get("status") == "not_due" else "not_eligible"})
        return
    if (plan.evidence.get("final_result", {}).get("status") not in {"succeeded", "ungoverned_completed"}
            or plan.evidence["final_result"].get("boundary_completed") is not True):
        raise RuntimeError("Successful confirmed whole-run finalization is required for source baseline acceptance.")
    if not plan.evidence.get("source_drift_decision", {}).get("can_continue"):
        raise RuntimeError("A consolidated Source Drift decision is required.")
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F
    context = {**plan.runtime_context, "execution_plan": plan, "_spark_session": spark_session, "_fabricops_suppress_io_log": True}
    identities = json.loads(plan.participants_json)
    observations = plan.evidence.get("source_drift_observations", {})
    expected_sources = {tid for tid, identity in identities.items()
                        if "source" in identity["roles"] and identity.get("source_type") != "file"}
    expected_candidates = {tid for tid, row in observations.items() if row["status"] != "not_due"}
    if (set(observations) != expected_sources or expected_candidates != set(candidates)
            or any(not row.get("can_continue", True) or row["status"] == "observation_failed" for row in observations.values())):
        raise RuntimeError("Partial or blocked source observations cannot accept a baseline.")
    for tid, identity in identities.items():
        if "target" not in identity["roles"]:
            continue
        outcome = plan.evidence.get("publication_outcomes", {}).get(tid, {})
        receipt = outcome.get("receipt")
        if ((not receipt and outcome.get("status") in {"empty_incremental_scope", "no_unseen_hashes"})
                or (receipt and receipt.get("run_id") != plan.plan_id)):
            plan.evidence["source_snapshot_acceptance"] = {"status": "not_eligible",
                "reason": "A required Write has no publication from this execution; prior-run recovery cannot accept a new source snapshot.",
                "target_table_id": tid}
            return
        if not receipt or not _physical_target_has_publication({**identity,
                "store_type": identity.get("store_type") or identity.get("store_kind")}, receipt, context=context):
            raise RuntimeError("All required target publications must be confirmed; nonpublishing Writes cannot accept source baselines.")
    records = []
    for source_id, header in candidates.items():
        metadata = json.loads(header["snapshot_payload_json"])
        key = metadata["context_key"]
        state = _source_snapshot_state(context).where(F.col("source_table_id") == source_id)
        _, actual_meta, actual_header = _validated_source_snapshot(state, header["observation_id"], context_key=key)
        if actual_meta != metadata or actual_header["content_fingerprint"] != header["content_fingerprint"]:
            raise RuntimeError("Candidate source snapshot changed before acceptance.")
        head = {**header, "record_id": _processing_state_id("source_drift_head", key),
            "record_type": "source_drift_baseline", "status": "committed", "accepted_at": datetime.now(UTC)}
        records.extend([head, {**head, "record_id": _processing_state_id(head["record_id"], header["observation_id"], "acceptance"),
            "record_type": "source_snapshot_acceptance"}])
    spark = get_spark_session(spark_session, context=context)
    frame = spark.createDataFrame(records, metadata_table_schema_registry()[_PROCESSING_STATE_TABLE])
    _, _, _, path = resolve_configured_lakehouse_table("Metadata", _PROCESSING_STATE_TABLE,
        metadata_table_physical_schema(context["config"], _PROCESSING_STATE_TABLE), context=context)
    target = DeltaTable.forPath(spark, path)
    if target.detail().select("properties").first()["properties"].get("delta.isolationLevel") != "Serializable":
        raise RuntimeError("Source baseline acceptance requires Serializable Processing State; run metadata setup before enabling Source Drift.")
    parent = "get_json_object(source.snapshot_payload_json, '$.parent_observation_id')"
    same = f"target.observation_id <=> {parent}"
    values = {name: f"source.`{name}`" for name in frame.columns}
    values["observation_id"] = f"CASE WHEN ({same}) OR target.observation_id = source.observation_id THEN source.observation_id ELSE raise_error('Source baseline advanced concurrently; repeat from Read.') END"
    inserted = {name: f"source.`{name}`" for name in frame.columns}
    inserted["observation_id"] = f"CASE WHEN source.record_type <> 'source_drift_baseline' OR {parent} IS NULL THEN source.observation_id ELSE raise_error('Source baseline disappeared; repeat from Read.') END"
    try:
        retry_delta_metadata(lambda: target.alias("target").merge(frame.alias("source"), "target.record_id = source.record_id")
            .whenMatchedUpdate(condition="source.record_type = 'source_drift_baseline' AND NOT (target.observation_id <=> source.observation_id)", set=values)
            .whenNotMatchedInsert(values=inserted).execute())
    except Exception:
        # Immutable acceptance receipts survive a later legitimate head advance.
        expected = {row["record_id"]: row["observation_id"] for row in records if row["record_type"] == "source_snapshot_acceptance"}
        try:
            accepted = _source_snapshot_state(context).where(F.col("record_id").isin(*expected)
                & (F.col("status") == "committed")).select("record_id", "observation_id").collect()
        except Exception as verification_error:
            error = RuntimeError("Source baseline acceptance outcome is unknown; inspect immutable acceptance records before retrying.")
            error.outcome_unknown = True
            raise error from verification_error
        if len(accepted) != len(expected) or {row["record_id"]: row["observation_id"] for row in accepted} != expected:
            raise
    plan.evidence["source_snapshot_acceptance"] = {"status": "accepted", "source_ids": sorted(candidates)}


class PublicationBatch:
    """Bind an immutable prepared batch to a durable, exact target-write marker.

    The content identity includes processing, source membership and target identity.
    A staged receipt binds that identity to a fresh (activity, timestamp) pair;
    both audit literals are written atomically with the business rows. Legacy
    activity-only observations are deliberately ineligible for automatic recovery.
    """

    def __init__(self, dataframe, *, identity, processing, source_table_ids, audit, context):
        """Retain the publication boundary without evaluating Spark data."""
        self.dataframe = add_row_hash(dataframe)
        self.identity = identity
        self.processing = processing
        self.source_table_ids = source_table_ids
        self.audit = dict(audit)
        self.context = context
        self.already_applied = False
        self.finalization_recovery = False
        self.receipt = {}
        self.publication_snapshot = []
        self._pending_caller_snapshot = None
        self._owns_cache = True

    def __enter__(self):
        """Materialize and identify the exact input before staging or writing."""
        from pyspark import StorageLevel
        from pyspark.sql import functions as F

        if self._owns_cache:
            self.dataframe.persist(StorageLevel.MEMORY_AND_DISK)
        try:
            names = sorted(name for name in self.dataframe.columns
                           if name not in {*_TARGET_AUDIT_COLUMNS, *_SCD2_LIFECYCLE_COLUMNS, "_row_hash"}
                           and not name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES))
            if not names:
                raise ValueError("A publication batch must contain business columns.")
            totals = row_hash_totals(self.dataframe)
            self.input_rows = totals["rows"]
            boundary = {
                "workspace_id": self.context["scope_workspace_id"], "target": self.identity["table_id"],
                "sources": sorted(self.source_table_ids), "processing": self.processing,
                "schema": [(n, self.dataframe.schema[n].dataType.jsonValue()) for n in names],
                "content": totals,
            }
            batch_id = hashlib.sha256(json.dumps(boundary, sort_keys=True, default=str).encode()).hexdigest()
            # Content identifies recovery; execution identifies a new user publication.
            # A fresh Overwrite/Append All must execute even for identical content.
            content_id = batch_id
            incremental = incremental_publication_scopes(workspace_id=self.context["scope_workspace_id"],
                activity_id=source_observation_run_id(self.context) or str(self.audit["_activity_id"]),
                target_table_id=self.identity["table_id"], source_table_ids=self.source_table_ids)
            execution_id = source_observation_run_id(self.context) or str(self.audit["_activity_id"])
            journal = getattr(self.context.get("execution_plan"), "evidence", self.context)
            # Successful acceptance clears transient checkpoints. Retained-frame
            # retries must keep the identity chosen when this execution admitted it.
            classifications = journal.setdefault("publication_scopes", {})
            self.execution_scoped = classifications.setdefault((execution_id, content_id),
                self.processing["load_strategy"] == "overwrite" or (
                    self.processing["load_strategy"] == "append_all" and not incremental))
            if self.execution_scoped:
                batch_id = f"{content_id}:{execution_id}"
            # Fresh per-batch audit time, independent of a notebook's reused
            # activity and of caller-provided run-consistent audit timestamps.
            self.audit["_committed_at"] = datetime.now(UTC)
            self.receipt = {"batch_id": batch_id, "activity_id": self.audit["_activity_id"],
                            "committed_at": self.audit["_committed_at"].isoformat(), "input_rows": self.input_rows,
                            "run_id": source_observation_run_id(self.context),
                            "strategy": self.processing["load_strategy"]}
            history_rows = []
            execution_id = source_observation_run_id(self.context) or str(self.audit["_activity_id"])
            journal = getattr(self.context.get("execution_plan"), "evidence", self.context)
            recoveries = journal.setdefault("publication_recoveries", {})
            alias_key = (execution_id, content_id)
            alias = recoveries.get(alias_key)
            if alias and _accepts_publication_receipt(self, alias):
                self.receipt, self.already_applied = alias, True
            try:
                history = read_lakehouse_table(
                    _PROCESSING_STATE_TABLE, store="Metadata",
                    schema=metadata_table_physical_schema(self.context["config"], _PROCESSING_STATE_TABLE),
                    context=self.context,
                )
                receipts = []
                history_rows = _processing_state_rows(history)
                for row in history_rows:
                    if (row.get("record_type") != "publication_receipt" or row.get("workspace_id") != self.context["scope_workspace_id"]
                            or row.get("target_table_id") != self.identity["table_id"]):
                        continue
                    receipt = _publication_receipt(row, history_rows)
                    if (receipt.get("batch_id") == batch_id or (
                            self.execution_scoped
                            and row.get("status") == "staged"
                            and str(receipt.get("batch_id", "")).split(":", 1)[0] == content_id
                        )) and receipt not in receipts:
                        receipts.append(receipt)
                for receipt in receipts:
                    if _accepts_publication_receipt(self, receipt):
                        self.receipt = receipt
                        self.already_applied = True
                        break
            except Exception as exc:
                if not is_table_not_found_error(exc):
                    raise
            if not self.already_applied:
                receipt = _find_applied_publication(
                    self.identity, batch_id, context=self.context, spark_session=self.dataframe.sparkSession,
                )
                if receipt and _accepts_publication_receipt(self, receipt):
                    self.receipt = receipt
                    self.already_applied = True
            if self.already_applied and self.receipt["batch_id"] != batch_id:
                recoveries[alias_key] = dict(self.receipt)
            if self.already_applied:
                _verify_retry_observations(self, history_rows)
                self._freeze_publication_snapshot(history_rows)
            _verify_publication_progress(self, history_rows)
            self._active_sources = {
                key: [dict(row) for row in _PENDING_SOURCE_OBSERVATIONS.get(key, [])]
                for source_id in self.source_table_ids
                for key in [(self.context["scope_workspace_id"], source_observation_run_id(self.context) or str(self.audit["_activity_id"]), source_id, self.identity["table_id"])]
            }
            _ACTIVE_PUBLICATION_SOURCES.update(self._active_sources)
            return self
        except BaseException:
            if self._owns_cache:
                self.dataframe.unpersist()
            raise

    def _freeze_publication_snapshot(self, history):
        """Bind retry acknowledgement to the full durable membership of the winning receipt."""
        publication_id = _processing_state_id(
            self.context["scope_workspace_id"], self.identity["table_id"], self.receipt["batch_id"],
            self.receipt["activity_id"], self.receipt["committed_at"],
        )
        self.publication_snapshot = [dict(row) for row in history
            if row.get("publication_id") == publication_id
            and row.get("workspace_id") == self.context["scope_workspace_id"]
            and row.get("target_table_id") == self.identity["table_id"]]
        self.finalization_recovery = any(row.get("status") == "staged" for row in self.publication_snapshot)

    def confirm(self):
        """Refuse metadata advancement if a writer silently omitted this batch."""
        if self.input_rows == 0 and self.processing["load_strategy"] in {"scd1", "scd2"}:
            # An empty keyed input cannot change business rows or advance a
            # watermark; no-op merges may legitimately leave no Delta commit.
            return
        if not _physical_target_has_publication(self.identity, self.receipt, context=self.context):
            # A concurrent identical append may have won Delta's transaction
            # identity. Accept its exact receipt, never the loser's timestamp.
            receipt = _find_applied_publication(
                self.identity, self.receipt["batch_id"], context=self.context, spark_session=self.dataframe.sparkSession,
            )
            if receipt:
                self.receipt = receipt
                self.already_applied = True
                history = read_lakehouse_table(
                    _PROCESSING_STATE_TABLE, store="Metadata",
                    schema=metadata_table_physical_schema(self.context["config"], _PROCESSING_STATE_TABLE), context=self.context,
                )
                self._freeze_publication_snapshot(_processing_state_rows(history))
                return
            raise RuntimeError(
                "Physical publication did not establish the exact batch receipt; "
                "Source Observation was not committed. Inspect the target before retrying."
            )

    def materialize_caller_snapshot(self, dataframe):
        """Detach the exact writer input and retain it until caller hand-off."""
        snapshot = dataframe.localCheckpoint(eager=True)
        checkpoint_rdd = snapshot._jdf.logicalPlan().rdd()
        dataframe_unpersist = snapshot.unpersist

        def release_snapshot(blocking=False):
            dataframe_unpersist(blocking)
            checkpoint_rdd.unpersist(blocking)
            return snapshot

        # DataFrame.unpersist() only addresses SQL cache-manager entries; a local
        # checkpoint owns a separate persisted RDD. Keep the native caller-facing
        # cleanup method while extending this snapshot instance to release both.
        snapshot.unpersist = release_snapshot
        self._pending_caller_snapshot = snapshot
        return self._pending_caller_snapshot

    def transfer_caller_snapshot(self):
        """Transfer cleanup ownership of the detached writer input to the caller."""
        snapshot = self._pending_caller_snapshot
        if snapshot is None:
            raise RuntimeError("The publication input snapshot has not been materialized.")
        self._pending_caller_snapshot = None
        return snapshot

    def __exit__(self, *_exc):
        """Release internal caches and any snapshot not transferred to the caller."""
        if getattr(self, "target_hashes", None) is not None:
            self.target_hashes.unpersist()
        if hasattr(self, "filtered_dataframe"):
            self.filtered_dataframe.unpersist()
        if self._pending_caller_snapshot is not None:
            self._pending_caller_snapshot.unpersist()
        for key, captured in self._active_sources.items():
            if _ACTIVE_PUBLICATION_SOURCES.get(key) == captured:
                _ACTIVE_PUBLICATION_SOURCES.pop(key, None)
        if self._owns_cache:
            self.dataframe.unpersist()


def _source_observation_signature(rows):
    """Compare source states without activity, capture IDs or audit timestamps."""
    fields = ("partition_value", "row_count", "min_change_value", "max_change_value", "content_fingerprint", "is_present", "partition_column", "change_column", "watermark_type")
    return sorted({json.dumps({name: row.get(name) for name in fields}, sort_keys=True, default=str) for row in rows})


def _verify_retry_observations(batch, history):
    """Refuse to attach a newer Read's checkpoint to an already-published frame."""
    for source_id in batch.source_table_ids:
        key = (batch.context["scope_workspace_id"], source_observation_run_id(batch.context) or str(batch.audit["_activity_id"]), source_id, batch.identity["table_id"])
        for pending, record_type in (
            (_PENDING_SOURCE_OBSERVATIONS.get(key, []), "incremental_checkpoint"),
        ):
            if not pending:
                continue
            candidates = {}
            for row in history:
                if (row.get("workspace_id") == batch.context["scope_workspace_id"] and row.get("source_table_id") == source_id
                        and row.get("target_table_id") == batch.identity["table_id"] and row.get("record_type") == record_type
                        and _publication_receipt(row, history) == batch.receipt):
                    candidates.setdefault(row["observation_id"], []).append(row)
            if not any(_source_observation_signature(pending) == _source_observation_signature(rows) for rows in candidates.values()):
                raise RuntimeError(
                    "The already-published prepared batch does not match this Read's pending source observations. "
                    "Publish the DataFrame prepared from the pending Read; the checkpoint was not advanced."
                )


def _verify_publication_progress(batch, history):
    """Reject a retained batch after another run has advanced its source checkpoint."""
    execution_id = source_observation_run_id(batch.context) or str(batch.audit["_activity_id"])
    for source_id in batch.source_table_ids:
        scope = _INCREMENTAL_SOURCE_SCOPES.get((batch.context["scope_workspace_id"], execution_id, source_id, batch.identity["table_id"]))
        if not scope or not scope.get("has_data"):
            continue
        accepted = _latest_source_target_observation(
            history, source_table_id=source_id, target_table_id=batch.identity["table_id"], workspace_id=batch.context["scope_workspace_id"],
        )
        progress = max((row["max_change_value"] for row in accepted if row.get("max_change_value") is not None), key=_progress_key, default=None)
        expected = [scope.get("after")]
        if batch.already_applied:
            expected.append(scope.get("through"))
        if not any((progress is None and value is None) or (
            progress is not None and value is not None and _progress_key(progress) == _progress_key(value)
        ) for value in expected):
            raise RuntimeError(
                "The source checkpoint advanced after this batch's Read in another pipeline run. "
                "Start a new run and repeat Read, Transform and Write; the retained batch was not published."
            )


def _accepts_publication_receipt(batch, receipt):
    """Require current target state before suppressing a keyed SCD merge."""
    if not _physical_target_has_publication(batch.identity, receipt, context=batch.context):
        return False
    if batch.processing["load_strategy"] not in {"scd1", "scd2", "append_new_only"}:
        return True
    if batch.identity.get("store_type") == "lakehouse":
        from delta.tables import DeltaTable

        _store, _table, _schema, path = resolve_configured_lakehouse_table(
            batch.identity["store"], batch.identity["table_name"], batch.identity.get("schema"), context=batch.context,
        )
        latest = DeltaTable.forPath(batch.dataframe.sparkSession, path).history(1).select("userMetadata").first()
        return latest["userMetadata"] == json.dumps(dict(receipt), sort_keys=True)
    schema = str(batch.identity["schema"]).replace("]", "]]")
    table = str(batch.identity["table_name"]).replace("]", "]]")
    latest = read_warehouse_query(
        f"SELECT MAX([_committed_at]) AS fabricops_latest_publication FROM [{schema}].[{table}]",
        store=batch.identity["store"], context=batch.context,
    ).first()["fabricops_latest_publication"]
    instant = datetime.fromisoformat(receipt["committed_at"]).astimezone(UTC).replace(tzinfo=None)
    return latest is not None and latest.replace(tzinfo=None) == instant


def _find_applied_publication(identity, batch_id, *, context, spark_session):
    """Find the exact winning Delta receipt, including source-free publications."""
    if identity.get("store_type") != "lakehouse":
        return None
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F

    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        identity["store"], identity["table_name"], identity.get("schema"), context=context,
    )
    if not DeltaTable.isDeltaTable(spark_session, path):
        return None
    commits = DeltaTable.forPath(spark_session, path).history().where(
        F.get_json_object("userMetadata", "$.batch_id") == batch_id
    ).select("userMetadata").collect()
    for commit in commits:
        receipt = json.loads(commit["userMetadata"])
        if _physical_target_has_publication(identity, receipt, context=context):
            return receipt
    return None


def _processing_state_rows(history):
    """Reject unsupported Preview layouts before interpreting any persisted progress."""
    required = set(metadata_table_schema_registry()[_PROCESSING_STATE_TABLE].fieldNames()) - {"snapshot_payload_json"}
    if hasattr(history, "columns") and (
        required - set(history.columns) or {"observation_status", "publication_payload_json"} & set(history.columns)
    ):
        raise RuntimeError("Incompatible METADATA_PROCESSING_STATE schema; existing progress is preserved and cannot be inferred safely.")
    snapshot_types = {"source_snapshot", "source_row_evidence", "source_drift_baseline", "source_snapshot_acceptance"}
    if hasattr(history, "where"):
        from pyspark.sql import functions as F
        history = history.where(F.col("record_type").isNull() | ~F.col("record_type").isin(*snapshot_types))
    rows = [row for row in observation_rows(history) if row.get("record_type") not in snapshot_types]
    for row in rows:
        if ("observation_status" in row or "publication_payload_json" in row
                or row.get("record_type") not in {"source_observation", "incremental_checkpoint", "drift_baseline", "full_source_baseline", "publication_receipt"}
                or row.get("status") not in ({"observed"} if row.get("record_type") == "source_observation" else {"staged", "committed"})
                or not row.get("record_id")):
            raise RuntimeError("Incompatible or invalid METADATA_PROCESSING_STATE record; existing progress is preserved and cannot be inferred safely.")
    return rows


def _publication_receipt(row: Mapping[str, Any], history=()) -> dict[str, Any]:
    """Resolve one typed publication receipt without copying its payload onto source rows."""
    if row.get("record_type") != "publication_receipt":
        matches = [item for item in history if item.get("record_type") == "publication_receipt"
                   and item.get("publication_id") == row.get("publication_id")
                   and item.get("workspace_id") == row.get("workspace_id")
                   and item.get("target_table_id") == row.get("target_table_id")]
        if not row.get("publication_id"):
            return {}
        if len(matches) != 1:
            raise RuntimeError("Processing State publication reference is missing or ambiguous; reconcile before retrying.")
        row = matches[0]
    receipt = {"batch_id": row.get("publication_batch_id"), "activity_id": row.get("publication_activity_id"),
               "committed_at": _watermark_timestamp(row["publication_at"]) if row.get("publication_at") else None,
               "input_rows": row.get("publication_input_rows"), "run_id": row.get("run_id"),
               "strategy": row.get("publication_strategy")}
    if not all(receipt.get(k) for k in ("batch_id", "activity_id", "committed_at", "strategy")) or receipt["input_rows"] is None:
        raise ValueError("Processing State publication receipt is incomplete.")
    # Use the same UTC spelling as receipts stored in Delta userMetadata.
    receipt["committed_at"] = datetime.fromisoformat(receipt["committed_at"].replace("Z", "+00:00")).isoformat()
    return receipt


def _physical_target_has_publication(
    identity: Mapping[str, Any], receipt: Mapping[str, Any], *, context: Mapping[str, Any]
) -> bool:
    """Verify both literals bound to an exact staged batch's atomic write."""
    if not receipt:
        return False
    # Preserve historical receipt facts verbatim; new strategy validation rejects append.
    if receipt.get("strategy") not in {"append", "append_all", "append_new_only", "overwrite", "scd1", "scd2"}:
        raise RuntimeError("Unsupported legacy target publication receipt; reconcile and rebuild/replay the target under the new Processing State schema before retrying.")
    store_kind = str(identity.get("store_type") or identity.get("store_kind") or "").lower()
    escaped = receipt["activity_id"].replace("'", "''")
    instant = datetime.fromisoformat(receipt["committed_at"])
    if instant.tzinfo is None:
        raise ValueError("Publication marker timestamp must include its timezone.")
    try:
        if store_kind == "lakehouse":
            from delta.tables import DeltaTable
            from pyspark.sql import functions as F

            _store, _table, _schema, path = resolve_configured_lakehouse_table(
                identity["store"], identity["table_name"], identity.get("schema"), context=context,
            )
            spark = get_spark_session(context=context)
            if not DeltaTable.isDeltaTable(spark, path):
                return False
            attested = DeltaTable.forPath(spark, path).history().where(
                F.col("userMetadata") == json.dumps(dict(receipt), sort_keys=True)
            ).limit(1).count() > 0
            if receipt.get("input_rows") == 0:
                return attested
            frame = read_lakehouse_table(
                str(identity["table_name"]), store=str(identity["store"]),
                schema=identity.get("schema"), context=context,
            ).where((F.col("_activity_id") == receipt["activity_id"]) & (F.col("_committed_at") == F.lit(instant)))
            marked = frame.limit(1).count() > 0
            if marked and not attested:
                raise RuntimeError(
                    "An exact-batch target marker exists but its Delta commit receipt is unavailable; "
                    "reconcile the publication before retrying."
                )
            return marked and attested
        elif store_kind == "warehouse":
            schema = str(identity["schema"]).replace("]", "]]")
            table = str(identity["table_name"]).replace("]", "]]")
            timestamp = instant.astimezone(UTC).replace(tzinfo=None).isoformat(timespec="microseconds")
            frame = read_warehouse_query(
                f"SELECT COUNT_BIG(*) AS fabricops_publication_rows FROM [{schema}].[{table}] "
                f"WHERE [_activity_id] = '{escaped}' AND [_committed_at] = CAST('{timestamp}' AS datetime2(6))",
                store=str(identity["store"]), context=context,
            )
            marked = int(frame.first()["fabricops_publication_rows"])
            if receipt.get("strategy") in {"append", "append_all", "append_new_only", "overwrite"}:
                if marked and marked != receipt["input_rows"]:
                    raise RuntimeError("Incomplete Warehouse publication marker count; reconcile the partial publication before retrying. Checkpoint was not advanced.")
                if receipt["input_rows"] == 0:
                    raise RuntimeError("An empty Warehouse publication has no durable row marker; reconcile before retrying.")
                return marked == receipt["input_rows"]
            return marked > 0
        else:
            return False
    except Exception as exc:
        if is_table_not_found_error(exc):
            return False
        raise


def _merge_source_observation_records(
    records: list[dict[str, Any]], *, config: Any, context: Mapping[str, Any]
) -> None:
    """Idempotently merge typed Processing State records at the configured metadata target."""
    if not records or not persistence_permitted(context):
        return
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - Fabric/Delta runtime dependency
        raise RuntimeError(
            "Delta Lake merge support is required for idempotent Source Observation commits."
        ) from exc
    spark = get_spark_session(context=context)
    frame = spark.createDataFrame(records, schema=metadata_table_schema_registry()[_PROCESSING_STATE_TABLE])
    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        "Metadata", _PROCESSING_STATE_TABLE,
        metadata_table_physical_schema(config, _PROCESSING_STATE_TABLE), context=context,
    )
    target = DeltaTable.forPath(spark, path)
    _processing_state_rows(target.toDF().limit(0))
    _processing_state_rows(records)
    for row in records:
        if row["record_type"] != "source_observation" and not _publication_receipt(row, records):
            raise ValueError("A checkpoint or baseline requires its publication receipt in the same atomic merge.")
    (
        retry_delta_metadata(lambda: target.alias("target")
        .merge(frame.alias("source"), "target.record_id = source.record_id")
        .whenMatchedUpdate(condition="target.status <> 'committed'", set={name: f"source.{name}" for name in frame.columns})
        .whenNotMatchedInsertAll().execute())
    )


def _recover_completed_source_observations(
    history: Any, *, config: Any, active_workspace_id: str, context: Mapping[str, Any],
    source_table_id: str, target_table_id: str,
) -> list[dict[str, Any]]:
    """Accept an entire staged publication in one Delta transaction after verification."""
    rows = _processing_state_rows(history)
    publication_ids = {row.get("publication_id") for row in rows
                       if row.get("workspace_id") == active_workspace_id and row.get("source_table_id") == source_table_id
                       and row.get("target_table_id") == target_table_id and row.get("status") == "staged"}
    if not publication_ids:
        return rows
    identity = _CURRENT_TABLE_IDENTITIES.get(str(target_table_id))
    identity = (_validated_observation_identity(config, active_workspace_id, target_table_id, identity) if identity is not None
                else resolve_catalogue_table_identity(config, active_workspace_id, target_table_id, context=dict(context)))
    recovered = []
    for publication_id in publication_ids:
        members = [row for row in rows if row.get("publication_id") == publication_id
                   and row.get("workspace_id") == active_workspace_id and row.get("target_table_id") == target_table_id]
        receipt = _publication_receipt(members[0], rows)
        if _physical_target_has_publication(identity, receipt, context=context):
            accepted_at = datetime.now(UTC)
            recovered.extend(row if row.get("status") == "committed" else
                             {**row, "status": "committed", "accepted_at": accepted_at}
                             for row in members if row.get("status") == "staged" or row.get("record_type") == "publication_receipt")
    if recovered and not persistence_permitted(context):
        context["execution_plan"].simulations.append({"check": "Source Observation recovery", "outcome": "simulated",
                                                    "source_table_id": source_table_id, "target_table_id": target_table_id})
    _merge_source_observation_records(recovered, config=config, context=context)
    if recovered:
        context.setdefault("_fabricops_source_observation_recovery", []).append({
            "source_table_id": source_table_id, "target_table_id": target_table_id,
            "status": "metadata_recovered" if persistence_permitted(context) else "recovery_simulated",
            "batches": len({row["publication_id"] for row in recovered}),
        })
    by_id = {row["record_id"]: row for row in [*rows, *recovered]}
    return list(by_id.values())


def _ensure_unambiguous_source_observation(key, pending, *, accepted=()):
    """Keep a second Read from rebinding an unpublished DataFrame's checkpoint."""
    previous = _PENDING_SOURCE_OBSERVATIONS.get(key, [])
    scope = _INCREMENTAL_SOURCE_SCOPES.get(key, {})
    if not previous or scope.get("has_data") is False:
        return
    # An in-flight Write has already frozen these exact observations. Permit
    # its next Read, but never replace another pending Read made in the meantime.
    if key in _ACTIVE_PUBLICATION_SOURCES and previous == _ACTIVE_PUBLICATION_SOURCES[key]:
        return
    if _source_observation_signature(previous) == _source_observation_signature(accepted):
        return
    if _source_observation_signature(previous) != _source_observation_signature(pending):
        raise RuntimeError(
            "A different incremental source state is already awaiting publication for this source and target. "
            "Publish or retry the existing Read's prepared DataFrame before reading newer data; "
            "the newer Read was rejected and the pending checkpoint was preserved. "
            "If that DataFrame was discarded, create a fresh pipeline plan/run and rerun Read, Transform and Write; standalone callers can restart their notebook session."
        )


def resolve_incremental_source_scope(
    *,
    source_table_id: str,
    target_table_id: str,
    observation: Any,
    context=None,
) -> dict[str, Any]:
    """Resolve and stage the unconsumed scope for one source-to-target relationship."""
    config, active_workspace_id, context = resolve_fabric_context() if context is None else (context["config"], context["scope_workspace_id"], context)
    audit = build_pipeline_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=context)
    activity_id = source_observation_run_id(context) or str(audit["_activity_id"])
    current = observation_rows(observation)
    if not current:
        raise ValueError(f"Current source observation for {source_table_id!r} is empty.")
    try:
        history = read_lakehouse_table(
            _PROCESSING_STATE_TABLE,
            store="Metadata",
            schema=metadata_table_physical_schema(config, _PROCESSING_STATE_TABLE),
            context=context,
        )
        history = _recover_completed_source_observations(
            history,
            config=config,
            active_workspace_id=active_workspace_id,
            context=context,
            source_table_id=source_table_id,
            target_table_id=target_table_id,
        )
        previous = _latest_source_target_observation(
            history,
            source_table_id=source_table_id,
            target_table_id=target_table_id,
            workspace_id=active_workspace_id,
        )
    except Exception as exc:
        if not is_table_not_found_error(exc):
            raise RuntimeError(
                f"Unable to load Source Observation history for {source_table_id!r}: {exc}"
            ) from exc
        previous = []

    first = current[0]
    partition_column = str(first.get("partition_column") or "").strip()
    change_column = str(first.get("change_column") or "").strip()
    if not partition_column or not change_column:
        raise ValueError("Incremental Source Observation is missing its processing columns.")

    if partition_column != change_column:
        raise ValueError(
            "Incremental Source Observation must use one governed watermark column."
        )
    for row in previous:
        for field, value in (("change_column", change_column), ("watermark_type", first.get("watermark_type"))):
            if row.get(field) and value and row[field] != value:
                raise ValueError("Incremental checkpoint column or type changed; reconcile Processing State before retrying.")
    current_max_value = next(
        (row.get("max_change_value") for row in current if row.get("max_change_value") is not None),
        None,
    )
    if first.get("watermark_type") == "timestamp_ntz":
        for row in [*current, *previous]:
            value = row.get("max_change_value")
            if value is not None and datetime.fromisoformat(str(value)).tzinfo is not None:
                raise ValueError("TimestampNTZ history contains a timezone; the incompatible checkpoint is preserved and execution is blocked.")
    timestamp_watermark = first.get("watermark_type") != "timestamp_ntz" and (bool(first.get("watermark_type") == "timestamp") or isinstance(
        current_max_value, datetime
    ) or str(current_max_value or "").endswith("Z") or (
        isinstance(current_max_value, str)
        and len(current_max_value) >= 19
        and current_max_value[4:5] == "-"
        and current_max_value[7:8] == "-"
        and current_max_value[10:11] in {"T", " "}
        and current_max_value[13:14] == ":"
    ))
    if timestamp_watermark:
        for row in previous:
            value = row.get("max_change_value")
            if value is not None:
                if row.get("watermark_type") != "timestamp":
                    raise ValueError("Committed timestamp watermark has no matching explicit type; existing Processing State is preserved and cannot be interpreted safely.")
                row["max_change_value"] = _watermark_timestamp(value)
        for row in current:
            value = row.get("max_change_value")
            if value is not None:
                row["max_change_value"] = _watermark_timestamp(value)
            value = row.get("min_change_value")
            if value is not None:
                row["min_change_value"] = _watermark_timestamp(value)
            value = row.get("partition_value")
            if value not in (None, ""):
                row["partition_value"] = _watermark_timestamp(value)
    has_rows = any(int(row.get("row_count") or 0) > 0 for row in current)
    pending = [dict(row) for row in current] if has_rows else []
    key = (active_workspace_id, activity_id, source_table_id, target_table_id)
    _ensure_unambiguous_source_observation(key, pending, accepted=previous)
    _PENDING_SOURCE_OBSERVATIONS[key] = pending

    previous_values = [
        str(row["max_change_value"])
        for row in previous
        if row.get("max_change_value") is not None
    ]
    current_values = [
        str(row["max_change_value"])
        for row in current
        if row.get("max_change_value") is not None
    ]
    baseline = max(
        previous_values,
        key=lambda value: _progress_key(value, timestamp=timestamp_watermark),
        default=None,
    )
    current_max = max(
        current_values,
        key=lambda value: _progress_key(value, timestamp=timestamp_watermark),
        default=None,
    )

    if not previous:
        scope = {
            "type": "full",
            "first_run": True,
            "has_data": has_rows,
            "observed_row_count": sum(int(row.get("row_count") or 0) for row in current),
            "column": change_column,
            "through": current_max,
        }
    else:
        scope = {
            "type": "watermark",
            "first_run": False,
            "has_data": has_rows and (
                baseline is None or (current_max is not None and _progress_key(current_max) > _progress_key(baseline))
            ),
            "column": change_column,
            "after": baseline,
            "through": current_max,
        }
    _INCREMENTAL_SOURCE_SCOPES[key] = scope
    return scope


def incremental_publication_scopes(
    *, workspace_id: str, activity_id: str, target_table_id: str, source_table_ids: list[str]
) -> dict[str, dict[str, Any]]:
    """Return staged incremental scopes for one exact publication boundary."""
    return {
        source_table_id: _INCREMENTAL_SOURCE_SCOPES[
            (workspace_id, activity_id, source_table_id, target_table_id)
        ]
        for source_table_id in source_table_ids
        if (workspace_id, activity_id, source_table_id, target_table_id)
        in _INCREMENTAL_SOURCE_SCOPES
    }




def snapshot_pipeline_write_observations(*, workspace_id, activity_id, target_table_id, source_table_ids, context=None):
    """Freeze source evidence so later reads cannot change a publication's checkpoint."""
    return {
        source_id: {
            "incremental": [dict(row) for row in _PENDING_SOURCE_OBSERVATIONS.get((workspace_id, activity_id, source_id, target_table_id), [])],
        }
        for source_id in source_table_ids
    }


def _processing_state_id(*values):
    """Build stable, unambiguous identities for typed records and publication links."""
    return hashlib.sha256(json.dumps(values, default=str, separators=(",", ":")).encode()).hexdigest()


def _pipeline_write_state_records(success_context, *, audit, active_workspace_id, status):
    """Build one publication receipt and its source members for a single atomic merge."""
    receipt = success_context.get("publication")
    if not receipt:
        raise ValueError("Processing State acceptance requires an exact publication receipt.")
    persisted = success_context.get("publication_snapshot") or []
    if persisted:
        return [dict(row) if status == "staged" or row["status"] == "committed" else
                {**row, "status": "committed", "accepted_at": audit["_committed_at"]} for row in persisted]
    context = success_context.get("context") or {}
    target_id = success_context["target_table_id"]
    publication_id = _processing_state_id(active_workspace_id, target_id, receipt["batch_id"], receipt["activity_id"], receipt["committed_at"])
    target_name = success_context.get("target_table_name") or _CURRENT_TABLE_IDENTITIES.get(target_id, {}).get("table_name")
    accepted_at = audit["_committed_at"] if status == "committed" else None
    common = {"workspace_id": active_workspace_id, "target_table_id": target_id, "target_table_name": target_name,
              "publication_id": publication_id, "status": status, "accepted_at": accepted_at,
              "pipeline_id": getattr(context.get("execution_plan"), "pipeline_id", None), **audit}
    records = [{**common, "record_id": publication_id, "record_type": "publication_receipt",
                "run_id": receipt.get("run_id"), "publication_batch_id": receipt["batch_id"],
                "publication_activity_id": receipt["activity_id"], "publication_at": datetime.fromisoformat(receipt["committed_at"]),
                "publication_input_rows": receipt["input_rows"], "publication_strategy": receipt["strategy"]}]
    for source_id in success_context.get("source_table_ids", []):
        captured = success_context["observation_snapshot"][source_id]
        source_name = _CURRENT_TABLE_IDENTITIES.get(source_id, {}).get("table_name") or resolve_catalogue_table_identity(
            context["config"], active_workspace_id, source_id, context=context).get("table_name")
        for kind, record_type in (("incremental", "incremental_checkpoint"),):
            for row in captured.get(kind, []):
                records.append({**{name: row.get(name) for name in (
                    "observation_id", "partition_value", "row_count", "min_change_value", "max_change_value",
                    "content_fingerprint", "is_present", "partition_column", "change_column", "watermark_type")},
                    **common, "record_type": record_type,
                    "record_id": _processing_state_id(publication_id, record_type, source_id, row["observation_id"],
                        {"empty_source": True} if row.get("is_present") is None else row.get("partition_value")),
                    "source_table_id": source_id, "source_table_name": source_name,
                    "run_id": source_observation_run_id(context),
                    "observed_at": row.get("observed_at") or row.get("_committed_at")})
    return [coerce_metadata_row_types(_PROCESSING_STATE_TABLE, row) for row in records]


def commit_pipeline_write_success(success_context: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Commit target Lineage and acknowledge the publication's original source members."""
    if not isinstance(success_context, Mapping):
        raise ValueError("success_context must be returned by write_pipeline_prep().")
    target_table_id = str(success_context.get("target_table_id") or "").strip()
    source_table_ids = [str(value).strip() for value in success_context.get("source_table_ids") or ()]
    activity_id = str(success_context.get("activity_id") or "").strip()
    notebook_name = str(success_context.get("notebook_name") or "").strip()
    if not target_table_id or not activity_id or not notebook_name:
        raise ValueError("success_context is missing target, activity, or logical notebook identity.")

    config, active_workspace_id, context = resolve_fabric_context(context=success_context.get("context"))
    audit = build_pipeline_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=context)
    audit["_activity_id"] = activity_id
    snapshot = success_context["observation_snapshot"]
    records = _pipeline_write_state_records(success_context, audit=audit, active_workspace_id=active_workspace_id, status="committed")
    for source_table_id in source_table_ids:
        persist_lineage_participation(
            table_id=source_table_id,
            pipeline_role="source",
            activity_id=activity_id,
            context=context,
        )
    persist_lineage_participation(
        table_id=target_table_id,
        pipeline_role="target",
        activity_id=activity_id,
        context=context,
    )
    _merge_source_observation_records(records, config=config, context=context)
    record_pipeline_publication(target_table_id, "committed", receipt=success_context.get("publication"), context=context)
    for source_table_id in source_table_ids:
        key = (active_workspace_id, source_observation_run_id(context) or activity_id, source_table_id, target_table_id)
        captured = snapshot[source_table_id]
        if _PENDING_SOURCE_OBSERVATIONS.get(key, []) == captured["incremental"]:
            _PENDING_SOURCE_OBSERVATIONS.pop(key, None)
            _INCREMENTAL_SOURCE_SCOPES.pop(key, None)
    return records


def stage_pipeline_write_observations(success_context: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Durably stage target-specific observations before physical publication."""
    target_table_id = str(success_context.get("target_table_id") or "").strip()
    activity_id = str(success_context.get("activity_id") or "").strip()
    notebook_name = str(success_context.get("notebook_name") or "").strip()
    if not target_table_id or not activity_id or not notebook_name:
        raise ValueError("success_context is missing target, activity, or logical notebook identity.")
    config, active_workspace_id, context = resolve_fabric_context(context=success_context.get("context"))
    audit = build_pipeline_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=context)
    audit["_activity_id"] = activity_id
    records = _pipeline_write_state_records(success_context, audit=audit, active_workspace_id=active_workspace_id, status="staged")
    _merge_source_observation_records(records, config=config, context=context)
    return records


def _parameters(rule: dict[str, Any]) -> dict[str, Any]:
    raw = rule.get("rule_parameters_json") or "{}"
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Sensitive Data rule_parameters_json must contain a JSON object.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Sensitive Data rule_parameters_json must contain a JSON object.")
    return parsed


def _validate_token_mapping(mapping):
    """Reject missing or conflicting assignments in the supplied lookup scope."""
    from pyspark.sql import functions as F

    checked = mapping.cache()
    try:
        if checked.where(F.col("original_value").isNull() | F.col("token_value").isNull()).limit(1).count():
            raise ValueError("Existing token mappings must contain non-null original and token values.")
        if checked.groupBy("original_value").agg(F.countDistinct("token_value").alias("count")).where(F.col("count") > 1).limit(1).count():
            raise ValueError("Existing mapping assigns multiple tokens to one original value.")
        if checked.groupBy("token_value").agg(F.countDistinct("original_value").alias("count")).where(F.col("count") > 1).limit(1).count():
            raise ValueError("Existing mapping reuses one token for multiple original values.")
    finally:
        checked.unpersist()


def _build_token_mapping(dataframe, *, column_name, column_id, table_id, existing_mapping,
                         config=None, active_workspace_id=None, context=None):
    """Materialize batch lookups for a vault, or cumulative caller-owned assignments."""
    from pyspark.sql import functions as F

    required = ["table_id", "column_id", "original_value", "token_value"]
    original_type = dataframe.schema[column_name].dataType.simpleString()
    originals = dataframe.where(F.col(column_name).isNotNull()).select(
        F.col(column_name).cast("string").alias("original_value")
    ).distinct()
    target = dict(getattr(getattr(config, "governance_config", None), "sensitive_data_token_mapping", {}) or {})
    vault, saved, established = None, None, None
    io_context = {**(context or {}), "config": config, "scope_workspace_id": active_workspace_id, "_fabricops_suppress_io_log": True}
    if target:
        from delta.tables import DeltaTable

        if existing_mapping is not None:
            raise ValueError("Use the configured token mapping store or existing_mapping, not both.")
        _store, _table, _schema, path = resolve_configured_lakehouse_table(
            target["store"], target["table_name"], target.get("schema"), context=io_context,
        )
        if not DeltaTable.isDeltaTable(dataframe.sparkSession, path):
            raise ValueError("Provision the restricted Sensitive Data token mapping Delta table before running this pipeline.")
        vault = DeltaTable.forPath(dataframe.sparkSession, path)
        saved = read_lakehouse_table(target["table_name"], store=target["store"], schema=target.get("schema"),
                                    context={**(io_context or {}), "_spark_session": dataframe.sparkSession})
        if not set(required + ["original_data_type"]) <= set(saved.columns):
            raise ValueError("Token mapping store requires table_id, column_id, original_value, token_value and original_data_type.")
        if any(saved.schema[name].dataType.simpleString() != "string" for name in required + ["original_data_type"]):
            raise ValueError("Token mapping store columns must use string data types.")
        saved = saved.where((F.col("table_id") == table_id) & (F.col("column_id") == column_id)).select(*required)
        established = saved.join(originals, "original_value", "left_semi").dropDuplicates()
    elif existing_mapping is not None:
        missing = sorted(set(required) - set(existing_mapping.columns))
        if missing:
            raise ValueError("existing_mapping is missing required column(s): " + ", ".join(missing) + ".")
        established = existing_mapping.where((F.col("table_id") == table_id) & (F.col("column_id") == column_id)).select(*required).dropDuplicates()
        _validate_token_mapping(established)

    unmatched = originals if established is None else originals.join(established.select("original_value"), "original_value", "left_anti")
    generated = unmatched.withColumn("token_value", F.expr("uuid()"))
    generated = generated.withColumn("table_id", F.lit(table_id)).withColumn("column_id", F.lit(column_id)).select(*required)
    available = generated if established is None else established.unionByName(generated)
    mapping = available.withColumn("original_data_type", F.lit(original_type)).cache()
    canonical = None
    try:
        mapping.count()
        if vault is not None:
            # Only proposed new assignments enter the Delta merge. Historical rows are never merged again.
            new_assignments = mapping.join(unmatched, "original_value", "left_semi")
            if persistence_permitted(context) and new_assignments.limit(1).count():
                condition = " AND ".join(f"target.`{key}` <=> source.`{key}`" for key in ("table_id", "column_id", "original_value"))
                vault.alias("target").merge(new_assignments.alias("source"), condition).whenNotMatchedInsert(
                    values={name: f"source.`{name}`" for name in required + ["original_data_type"]}
                ).execute()
                saved = read_lakehouse_table(target["table_name"], store=target["store"], schema=target.get("schema"),
                                            context={**(io_context or {}), "_spark_session": dataframe.sparkSession}).where(
                    (F.col("table_id") == table_id) & (F.col("column_id") == column_id)
                ).select(*required)
                canonical = originals.join(saved, "original_value", "left").withColumn("original_data_type", F.lit(original_type)).cache()
                canonical.count()
            current = canonical if canonical is not None else mapping
            # Check reverse collisions only for tokens used by this batch, including collisions with absent identities.
            related = saved.join(current.select("token_value").distinct(), "token_value", "left_semi").select(*required)
            _validate_token_mapping(current.select(*required).unionByName(related).dropDuplicates())
            if canonical is not None:
                mapping.unpersist()
                return canonical
        return mapping
    except Exception:
        if canonical is not None:
            canonical.unpersist()
        mapping.unpersist()
        raise


def _apply_token_mapping(dataframe, *, column_name, column_id, table_id, mapping):
    """Join a materialized mapping without forcing a broadcast of sensitive values."""
    from pyspark.sql import functions as F

    original_temp = "__fabricops_sensitive_original"
    token_temp = "__fabricops_sensitive_token"
    while original_temp in dataframe.columns or token_temp in dataframe.columns:
        original_temp += "_"
        token_temp += "_"
    lookup = mapping.where((F.col("table_id") == table_id) & (F.col("column_id") == column_id)).select(
        F.col("original_value").alias(original_temp),
        F.col("token_value").alias(token_temp),
    )
    tokenized = (
        dataframe.withColumn(original_temp, F.col(column_name).cast("string"))
        .join(lookup, on=original_temp, how="left")
        .withColumn(
        column_name,
        F.when(F.col(original_temp).isNull(), F.lit(None)).otherwise(F.col(token_temp)),
        )
        .drop(original_temp, token_temp)
    )
    return tokenized


def _mask_column(dataframe, *, column_name, parameters):
    """Return rows with the configured middle characters obscured."""
    from pyspark.sql import functions as F

    preserve_start = parameters["preserve_start"]
    preserve_end = parameters["preserve_end"]
    value = F.col(column_name).cast("string")
    length = F.length(value)
    mask_literal = "'" + parameters["mask_character"].replace("'", "''") + "'"
    hidden = F.expr(
        f"repeat({mask_literal}, greatest(length(cast(`{column_name.replace('`', '``')}` as string)) "
        f"- {preserve_start} - {preserve_end}, 0))"
    )
    if preserve_start:
        start = F.substring(value, 1, preserve_start)
    else:
        start = F.lit("")
    if preserve_end:
        end = F.reverse(F.substring(F.reverse(value), 1, preserve_end))
    else:
        end = F.lit("")
    full_mask = F.expr(f"repeat({mask_literal}, length(cast(`{column_name.replace('`', '``')}` as string)))")
    masked = F.when(length <= preserve_start + preserve_end + 1, full_mask).otherwise(
        F.concat(
            start,
            hidden,
            end,
        )
    )
    return dataframe.withColumn(column_name, F.when(F.col(column_name).isNull(), F.lit(None)).otherwise(masked))


def _bucket_column(dataframe, *, column_name, parameters):
    """Return rows with exact numeric values replaced by coarse labels."""
    from pyspark.sql import functions as F
    from pyspark.sql.types import NumericType

    if not isinstance(dataframe.schema[column_name].dataType, NumericType):
        raise ValueError("Sensitive Data bucket treatment requires a numeric column.")
    value = F.col(column_name)
    if "bin_width" in parameters:
        from decimal import Decimal
        from pyspark.sql.types import DecimalType, DoubleType, FloatType

        width, origin = Decimal(str(parameters["bin_width"])), Decimal(str(parameters["bin_origin"]))
        source_type = dataframe.schema[column_name].dataType
        needed_scale = max(0, -width.as_tuple().exponent, -origin.as_tuple().exponent)
        working_scale = max(getattr(source_type, "scale", 0), needed_scale,
                            18 if isinstance(source_type, (FloatType, DoubleType)) else 0)
        if working_scale > 36:
            raise ValueError("Fixed-width buckets exceed supported decimal precision; use wider intervals or transform the column first.")
        exact = value.cast("string").cast(DecimalType(36, working_scale))
        shifted = exact if not origin else exact - F.lit(origin)
        lower = exact - F.pmod(shifted, F.lit(width))
        upper = lower + F.lit(width)
        bounds = dataframe.select(shifted.alias("shifted"), lower.alias("lower"), upper.alias("upper"))
        if any(getattr(field.dataType, "scale", 0) < working_scale for field in bounds.schema.fields):
            raise ValueError("Fixed-width buckets exceed supported decimal precision; use wider intervals or transform the column first.")
        def bound_label(expression):
            return F.regexp_replace(F.regexp_replace(expression.cast("string"), r"(\.\d*?)0+$", "$1"), r"\.$", "")
        invalid = ~exact.cast(source_type).eqNullSafe(value) | lower.isNull() | upper.isNull()
        label = F.when(value.isNotNull() & invalid, F.raise_error("Numeric value exceeds supported bucket precision.")).otherwise(
            F.concat(F.lit("["), bound_label(lower), F.lit(", "), bound_label(upper), F.lit(")"))
        )
        return dataframe.withColumn(column_name, F.when(value.isNull(), F.lit(None)).otherwise(label))
    bins = parameters["bins"]
    labels = parameters["labels"]
    bucket = F.lit(labels[0])
    for boundary, label in zip(bins[1:], labels[1:]):
        bucket = F.when(value >= F.lit(boundary), F.lit(label)).otherwise(bucket)
    return dataframe.withColumn(column_name, F.when(value.isNull(), F.lit(None)).otherwise(bucket))



def check_sensitive_data_rules(
    dataframe,
    *,
    rules: list[dict[str, Any]],
    identity: dict[str, Any],
    config,
    active_workspace_id: str,
    spark_session,
    run_id: str = "",
    existing_mapping=None,
    context=None,
) -> dict[str, Any]:
    """Apply supplied exact-contract Sensitive Data rules without resolving contract state."""
    from fabricops_kit.data_contract.shared import validate_sensitive_data_parameters

    transformed = dataframe
    mappings = []
    token_columns = []
    checks = []
    support_mapping = None
    try:
        for rule in rules:
            action = "Block"
            column_id = str(rule.get("column_id") or "").strip()
            column_name = str(rule.get("column_name") or "").strip()
            treatment = ""
            error = ""
            try:
                params = validate_sensitive_data_parameters(_parameters(rule))
                treatment = params["treatment"]
                if not column_id or not column_name:
                    raise ValueError("Sensitive Data Guardrail has an unresolved column identity or invalid scope.")
                if column_name not in transformed.columns:
                    raise ValueError(f"Sensitive Data column {column_name!r} is missing from the DataFrame.")
                if treatment == "remove":
                    transformed = transformed.drop(column_name)
                elif treatment == "tokenize":
                    mapping = _build_token_mapping(
                        transformed,
                        column_name=column_name,
                        column_id=column_id,
                        table_id=identity["table_id"],
                        existing_mapping=existing_mapping,
                        config=config, active_workspace_id=active_workspace_id, context=context,
                    )
                    mappings.append(mapping)
                    token_columns.append((column_name, column_id))
                elif treatment == "mask":
                    transformed = _mask_column(transformed, column_name=column_name, parameters=params)
                else:
                    transformed = _bucket_column(transformed, column_name=column_name, parameters=params)
            except ValueError as exc:
                error = str(exc)
            except Exception:
                error = f"{treatment.title() or 'Sensitive Data'} treatment could not be applied."
            passed = not error
            can_continue = passed
            check = {
                "guardrail_rule_id": str(rule.get("guardrail_rule_id") or rule.get("rule_id") or ""),
                "guardrail_version": int(rule.get("guardrail_version") or 1),
                "contract_id": str(rule.get("contract_id") or ""),
                "contract_version": int(rule.get("contract_version") or 0),
                "table_id": identity["table_id"],
                "column_id": column_id,
                "treatment": treatment,
                "action": action,
                "status": "passed" if passed else "failed",
                "can_continue": can_continue,
                "severity": "blocking",
                "reason": "Treatment applied." if passed else error,
            }
            checks.append(check)
            write_guardrail_result_row(
                spark_session=spark_session,
                config=config,
                active_workspace_id=active_workspace_id,
                run_id=run_id,
                dataset_name="",
                table_name=identity["table_name"],
                store_type=identity["store_type"],
                layer="",
                schema_name=identity["schema"],
                guardrail_type="sensitive_data",
                rule_type=treatment,
                result=check,
                column_name=column_name,
                table_id=identity["table_id"],
                contract_id=str(rule.get("contract_id") or ""),
                contract_version=int(rule.get("contract_version") or 0),

                context=context,
            )
        can_continue = all(check["can_continue"] for check in checks)
        support_mapping = None
        if not can_continue:
            for mapping in mappings:
                mapping.unpersist()
        elif mappings:
            support_mapping = mappings[0]
            if len(mappings) > 1:
                for mapping in mappings[1:]:
                    support_mapping = support_mapping.unionByName(mapping)
                # One caller-owned cache, including every treated column. The returned
                # DataFrame and support mapping both use this stable set of UUIDs.
                support_mapping = support_mapping.cache()
                support_mapping.count()
                for mapping in mappings:
                    mapping.unpersist()
            for column_name, column_id in token_columns:
                transformed = _apply_token_mapping(transformed, column_name=column_name,
                    column_id=column_id, table_id=identity["table_id"], mapping=support_mapping)
        result = {
            "status": "passed" if can_continue else "failed",
            "can_continue": can_continue,
            "dataframe": transformed,
            "support_mapping": support_mapping,
            "mapping_persisted": bool(persistence_permitted(context) and support_mapping is not None
                                      and getattr(getattr(config, "governance_config", None), "sensitive_data_token_mapping", {})),
            "checks": checks,
        }
        return result
    except Exception:
        if support_mapping is not None:
            support_mapping.unpersist()
        for mapping in mappings:
            mapping.unpersist()
        raise


def write_guardrail_result_row(
    *,
    spark_session: Any,
    config: Any,
    active_workspace_id: str,
    run_id: str,
    dataset_name: str,
    table_name: str,
    store_type: str,
    layer: str,
    schema_name: str | None = None,
    guardrail_type: str,
    rule_type: str,
    result: dict[str, Any],
    rule_key: str = "",
    column_name: str = "",
    table_id: str = "",
    contract_id: str = "",
    contract_version: int = 0,
    results_table: str = "METADATA_GUARDRAIL_RESULTS",
    context=None,
) -> None:
    """Append one aggregate outcome for one exact contract and Guardrail revision."""
    del dataset_name, store_type, layer, schema_name, column_name
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        return
    guardrail_rule_id = str(result.get("guardrail_rule_id") or "").strip()
    if not guardrail_rule_id:
        return
    guardrail_version = int(result.get("guardrail_version") or 0)
    if guardrail_version <= 0:
        raise ValueError("guardrail_version is required to persist a Guardrail result.")
    plan = (context or {}).get("execution_plan")
    audit = build_pipeline_audit_fields(config=config, active_workspace_id=active_workspace_id,
                                       runtime_context=plan.runtime_context if plan is not None else context)
    resolved_run_id = str(run_id or "").strip() or str(audit["_activity_id"])
    resolved_execution_type = plan.execution_mode if plan is not None else "governed"
    if plan is not None:
        resolved_run_id = plan.plan_id
    payload = {
        key: value
        for key, value in result.items()
        if key not in {"dataframe", "support_mapping"}
    }
    rule_context = result.get("rule_context") or {}
    if not rule_context:
        try:
            rules = load_table_guardrail_rules(
                config, active_workspace_id, spark_session=spark_session,
                table_id=str(table_id or result.get("table_id") or "").strip(),
                context=context or {"config": config, "scope_workspace_id": active_workspace_id},
            )
            for rule_row in observation_rows(rules):
                if (str(rule_row.get("guardrail_rule_id") or "") == guardrail_rule_id
                        and int(rule_row.get("guardrail_version") or 0) == guardrail_version):
                    rule_context = rule_row
                    break
        except Exception:
            rule_context = {}
    row = {
        "guardrail_result_id": str(uuid4()),
        "guardrail_rule_id": guardrail_rule_id,
        "guardrail_version": guardrail_version,
        "table_id": None if str(table_id).startswith("file:") else str(table_id or result.get("table_id") or "").strip(),
        "source_id": table_id if str(table_id).startswith("file:") else None,
        "table_name": str(table_name or "").strip(),
        "contract_id": str(contract_id or result.get("contract_id") or "").strip(),
        "contract_version": int(contract_version or result.get("contract_version") or 0),
        "execution_type": resolved_execution_type,
        "run_id": resolved_run_id,
        "workspace_id": active_workspace_id,
        "status": str(result.get("status") or "not_run"),
        "can_continue": bool(result.get("can_continue", True)),
        "severity": str(result.get("severity") or "blocking"),
        "guardrail_type": str(result.get("guardrail_type") or rule_context.get("guardrail_type") or guardrail_type or ""),
        "rule_id": str(result.get("rule_id") or rule_context.get("rule_id") or rule_key or ""),
        "rule_type": str(result.get("rule_type") or rule_context.get("rule_type") or rule_type or ""),
        "action": str(result.get("action") or rule_context.get("action") or result.get("severity") or ""),
        "reason": str(result.get("reason") or result.get("message") or ""),
        "result_payload_json": json.dumps(payload, default=str, sort_keys=True, separators=(",", ":")),
        **audit,
    }
    if plan is not None:
        plan.results.append(row)
        if not plan.permits_persistence:
            plan.evidence.setdefault("guardrail_history", []).append(dict(row))
    if not persistence_permitted(context):
        return
    write_lakehouse_table(
        spark_session.createDataFrame([coerce_metadata_row_types(results_table, row)],
            schema=metadata_table_schema_registry()[results_table]),
        results_table,
        store="Metadata",
        schema=metadata_table_physical_schema(config, results_table),
        context={"config": config, "scope_workspace_id": active_workspace_id,
                 "_fabricops_suppress_io_log": (context or {}).get("_fabricops_suppress_io_log", False)},
        mode="append",
    )

_DEFAULT_STABILITY_EXCLUDE_COLUMNS = {
    "_fabricops_run_id",
    "_fabricops_pipeline_name",
    "_fabricops_created_at",
    "_dq_check_status",
    "_dq_failed_rules",
}

_DEFAULT_STABILITY_EXCLUDE_PREFIXES = ("_fabricops_", "_dq_")

_ACTIVE_RULE_REVIEW_STATUSES = {"authored", "self_approved", "governance_approved", "active_pending_governance_review"}

_BYPASS_POST_REVIEW_WARNING = "Rule is active through approval bypass and requires governance post-review."




STANDARD_DQ_RULE_TYPES = ("completeness", "uniqueness", "value_set", "range", "pattern")
TABLE_DQ_RULE_TYPES = (
    "column_relationship", "conditional_completeness", "conditional_values",
    "custom_expression",
)
DQ_RULE_TYPES = [*STANDARD_DQ_RULE_TYPES, *TABLE_DQ_RULE_TYPES]


def dq_tolerance_parameter(rule_type: str, mode: str = "") -> str | None:
    """Return the meaningful percentage setting for a DQ rule, if applicable.

    Prohibited values are strict. Structural Guardrails (Schema, Grain,
    Sensitive Data) and freshness/drift limits do not use a DQ row percentage.
    """
    if rule_type in {"completeness", "conditional_completeness"}:
        return "maximum_missing_percent"
    if rule_type == "uniqueness":
        return "maximum_failure_percent"
    if rule_type in {"value_set", "conditional_values"}:
        return "maximum_failure_percent" if mode == "allow" else None
    if rule_type in {"range", "pattern", "column_relationship", "custom_expression"}:
        return "maximum_failure_percent"
    return None

DQ_COMPARISON_OPERATORS = ("=", "!=", ">", ">=", "<", "<=")

_COMPARISON_SCOPES = {"complete", "partitions", "partial"}

def _is_spark_dataframe(dataframe) -> bool:
    """Return whether a value exposes the Spark DataFrame contract used here."""
    return dataframe is not None and hasattr(dataframe, "sparkSession") and hasattr(dataframe, "schema")

def _local_source_rows(dataframe) -> list[dict]:
    """Return local row mappings without accepting Spark DataFrames."""
    if _is_spark_dataframe(dataframe):
        raise TypeError("Spark DataFrames must use the distributed changes implementation")
    if dataframe is None:
        return []
    rows = [dataframe] if isinstance(dataframe, dict) else dataframe
    return [_row_to_dict(row) for row in rows]

def _stable_source_value(value):
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _stable_source_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_stable_source_value(item) for item in value]
    return value

def _source_hash(payload) -> str:
    encoded = json.dumps(_stable_source_value(payload), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

def _validate_changes_configuration(comparison_scope, refresh_days):
    scope = str(comparison_scope).strip().lower()
    if scope not in _COMPARISON_SCOPES:
        raise ValueError("comparison_scope must be one of: complete, partitions, partial")
    if isinstance(refresh_days, bool):
        raise ValueError("refresh_days must be a non-negative integer")
    try:
        window_days = int(refresh_days)
    except (TypeError, ValueError) as exc:
        raise ValueError("refresh_days must be a non-negative integer") from exc
    if window_days < 0:
        raise ValueError("refresh_days must be a non-negative integer")
    return scope, window_days

def _partition_identity(row, partitions):
    return tuple(row.get(column) for column in partitions) if partitions else ("__FULL_SOURCE__",)

def _validate_local_logical_keys(rows, keys):
    seen = set()
    for row in rows:
        identity = tuple(row.get(column) for column in keys)
        if any(value is None for value in identity):
            raise ValueError("logical key columns must not contain null values")
        key_hash = _source_hash(identity)
        if key_hash in seen:
            raise ValueError("logical key columns must uniquely identify rows")
        seen.add(key_hash)

def _local_partition_observations(rows, partitions, range_column, all_columns):
    grouped = {}
    for row in rows:
        grouped.setdefault(_partition_identity(row, partitions), []).append(row)
    observations = []
    for partition, members in sorted(grouped.items(), key=lambda item: str(item[0])):
        values = [row.get(range_column) for row in members if range_column and row.get(range_column) is not None]
        row_hashes = sorted(_source_hash([(column, row.get(column)) for column in all_columns]) for row in members)
        observations.append({
            "partition": dict(zip(partitions, partition, strict=True)) if partitions else {},
            "row_count": len(members),
            "min_value": _stable_source_value(min(values)) if values else None,
            "max_value": _stable_source_value(max(values)) if values else None,
            "fingerprint": _source_hash(row_hashes),
            "_partition_id": _source_hash(partition),
        })
    return observations

def _changed_partition_sets(current_observations, previous_observations, scope):
    current = {item["_partition_id"]: item for item in current_observations}
    previous = {item["_partition_id"]: item for item in previous_observations}
    changed = {key for key in current.keys() & previous.keys() if current[key]["fingerprint"] != previous[key]["fingerprint"]}
    new = current.keys() - previous.keys()
    missing = previous.keys() - current.keys() if scope == "complete" else set()
    return changed, set(new), set(missing)

def _classify_change_date(value, recent_start):
    observed = _coerce_date(value)
    return "recent" if observed is not None and observed >= recent_start else "historical"

def _local_row_comparison(current, previous, *, relevant_current_partitions, relevant_previous_partitions,
                          partitions, keys, content_columns, range_column, scope, recent_start):
    current = [row for row in current if _source_hash(_partition_identity(row, partitions)) in relevant_current_partitions]
    previous = [row for row in previous if _source_hash(_partition_identity(row, partitions)) in relevant_previous_partitions]

    def keyed(rows):
        output = {}
        for row in rows:
            identity = tuple(row.get(column) for column in keys)
            if any(value is None for value in identity):
                raise ValueError("logical key columns must not contain null values")
            key_hash = _source_hash(identity)
            if key_hash in output:
                raise ValueError("logical key columns must uniquely identify rows")
            output[key_hash] = (row, _source_hash([(column, row.get(column)) for column in content_columns]))
        return output

    current_by_key, previous_by_key = keyed(current), keyed(previous)
    inserted = sorted(set(current_by_key) - set(previous_by_key))
    shared = set(current_by_key) & set(previous_by_key)
    updated = sorted(key for key in shared if current_by_key[key][1] != previous_by_key[key][1])
    deletion_allowed = scope in {"complete", "partitions"}
    deleted = sorted(set(previous_by_key) - set(current_by_key)) if deletion_allowed else []
    changes = {"inserted": inserted, "updated": updated, "deleted": deleted}
    recent, historical = [], []
    for change_type, hashes in changes.items():
        source = previous_by_key if change_type == "deleted" else current_by_key
        for key_hash in hashes:
            classified = {"key_hash": key_hash, "change_type": change_type}
            if range_column:
                target = recent if _classify_change_date(source[key_hash][0].get(range_column), recent_start) == "recent" else historical
                target.append(classified)
    return changes, recent, historical

def _spark_column(name):
    from pyspark.sql import functions as F
    return F.col(f"`{str(name).replace('`', '``')}`")

def _spark_canonical_hash(columns):
    from pyspark.sql import functions as F
    struct = F.struct(*[_spark_column(column).alias(str(column)) for column in columns])
    return F.sha2(F.to_json(struct, {"ignoreNullFields": "false"}), 256)

def _validate_spark_logical_keys(dataframe, keys):
    from functools import reduce
    from pyspark.sql import functions as F
    null_key = reduce(lambda left, right: left | right, [_spark_column(column).isNull() for column in keys])
    if dataframe.filter(null_key).limit(1).count():
        raise ValueError("logical key columns must not contain null values")
    if dataframe.groupBy(*keys).count().filter(F.col("count") > 1).limit(1).count():
        raise ValueError("logical key columns must uniquely identify rows")

def _spark_partition_frame(dataframe, partitions, range_column, all_columns):
    from pyspark.sql import functions as F
    partition_id = _spark_canonical_hash(partitions) if partitions else F.lit(_source_hash(("__FULL_SOURCE__",)))
    row_hash = _spark_canonical_hash(all_columns)
    prepared = dataframe.withColumn("__fabricops_partition_id", partition_id).withColumn("__fabricops_row_hash", row_hash)
    grouping = ["__fabricops_partition_id", *partitions]
    aggregates = [
        F.count(F.lit(1)).alias("row_count"),
        F.min("__fabricops_row_hash").alias("__min_hash"),
        F.max("__fabricops_row_hash").alias("__max_hash"),
        F.sum(F.xxhash64("__fabricops_row_hash").cast("decimal(38,0)")).alias("__hash_sum"),
    ]
    if range_column:
        aggregates.extend([F.min(_spark_column(range_column)).alias("min_value"), F.max(_spark_column(range_column)).alias("max_value")])
    grouped = prepared.groupBy(*grouping).agg(*aggregates)
    grouped = grouped.withColumn(
        "fingerprint",
        F.sha2(F.concat_ws("|", F.col("row_count"), F.col("__min_hash"), F.col("__max_hash"), F.col("__hash_sum")), 256),
    )
    return prepared.drop("__fabricops_row_hash"), grouped

def _collect_spark_observations(grouped, partitions):
    from pyspark.sql import functions as F
    rows = grouped.select("__fabricops_partition_id", *partitions, "row_count", "min_value" if "min_value" in grouped.columns else F.lit(None).alias("min_value"), "max_value" if "max_value" in grouped.columns else F.lit(None).alias("max_value"), "fingerprint").collect()
    return [{
        "partition": {column: _stable_source_value(row[column]) for column in partitions},
        "row_count": row["row_count"],
        "min_value": _stable_source_value(row["min_value"]),
        "max_value": _stable_source_value(row["max_value"]),
        "fingerprint": row["fingerprint"],
        "_partition_id": row["__fabricops_partition_id"],
    } for row in rows]

def _spark_row_comparison(current, previous, *, relevant_current_partitions, relevant_previous_partitions,
                          keys, content_columns, range_column, scope, recent_start, include_row_changes):
    from pyspark.sql import functions as F
    current = current.filter(F.col("__fabricops_partition_id").isin(sorted(relevant_current_partitions)))
    previous = previous.filter(F.col("__fabricops_partition_id").isin(sorted(relevant_previous_partitions)))
    current = current.withColumn("key_hash", _spark_canonical_hash(keys)).withColumn("non_key_hash", _spark_canonical_hash(content_columns))
    previous = previous.withColumn("key_hash", _spark_canonical_hash(keys)).withColumn("non_key_hash", _spark_canonical_hash(content_columns))
    for dataframe in (current, previous):
        if dataframe.groupBy("key_hash").count().filter(F.col("count") > 1).limit(1).count():
            raise ValueError("logical key columns must uniquely identify rows")
    current_rows = current.select("key_hash", "non_key_hash", *([_spark_column(range_column).alias("range_value")] if range_column else [F.lit(None).alias("range_value")]))
    previous_rows = previous.select("key_hash", "non_key_hash", *([_spark_column(range_column).alias("range_value")] if range_column else [F.lit(None).alias("range_value")]))
    joined = current_rows.alias("c").join(previous_rows.alias("p"), "key_hash", "full_outer")
    deletion_allowed = scope in {"complete", "partitions"}
    classified = joined.withColumn("change_type", F.when(F.col("p.non_key_hash").isNull(), "inserted").when(F.col("c.non_key_hash").isNull() & F.lit(deletion_allowed), "deleted").when(F.col("c.non_key_hash") != F.col("p.non_key_hash"), "updated"))
    classified = classified.filter(F.col("change_type").isNotNull())
    change_date = F.coalesce(F.col("c.range_value"), F.col("p.range_value")).cast("date")
    classified = classified.withColumn("age_class", F.when(change_date >= F.lit(recent_start), "recent").otherwise("historical") if range_column else F.lit(None).cast("string"))
    counts = {row["change_type"]: row["count"] for row in classified.groupBy("change_type").count().collect()}
    ages = {row["age_class"]: row["count"] for row in classified.filter(F.col("age_class").isNotNull()).groupBy("age_class").count().collect()}
    row_changes = {"inserted": [], "updated": [], "deleted": [], "recent": [], "historical": []}
    if include_row_changes:
        for row in classified.select("key_hash", "change_type", "age_class").collect():
            row_changes[row["change_type"]].append(row["key_hash"])
            if row["age_class"]:
                row_changes[row["age_class"]].append({"key_hash": row["key_hash"], "change_type": row["change_type"]})
    return counts, ages, row_changes

def _strip_internal_observation_fields(observations):
    return [{key: value for key, value in item.items() if not key.startswith("_")} for item in observations]

def _changes_content_columns(columns, keys, non_key_columns):
    """Resolve the business content columns used for comparison."""
    if non_key_columns is not None:
        return tuple(non_key_columns)
    return tuple(
        column
        for column in columns
        if column not in keys
    )


def _rule_review_status(row: dict) -> str:
    return _string_value(_catalogue_value(row, "review_state", "review_status")).lower()

def _is_active_guardrail_rule(row: dict) -> bool:
    activation_state = _string_value(_catalogue_value(row, "activation_state")).lower()
    if activation_state:
        if activation_state != "active":
            return False
    elif _catalogue_value(row, "is_active") is not True:
        return False
    review_status = _rule_review_status(row)
    return not review_status or review_status in _ACTIVE_RULE_REVIEW_STATUSES

def _parse_rule_parameters(row: dict) -> dict:
    raw = _catalogue_value(row, "rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except Exception:
        return {}

def _select_table_guardrail_rule(rules_df, *, guardrail_type: str, dataset_name: str, table_name: str, workspace_id: str = "", table_id: str = "") -> dict | None:
    if rules_df is None:
        return None
    rows = rules_df.collect() if hasattr(rules_df, "collect") else ([rules_df] if isinstance(rules_df, dict) else rules_df)
    candidates = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if _string_value(_catalogue_value(row, "guardrail_type")).lower() != guardrail_type:
            continue
        rule_workspace_id = _string_value(_catalogue_value(row, "workspace_id"))
        if rule_workspace_id and workspace_id and rule_workspace_id != workspace_id:
            continue
        if dataset_name and _string_value(_catalogue_value(row, "dataset_name")) != dataset_name:
            continue
        if table_name and _string_value(_catalogue_value(row, "table_name")) != table_name:
            continue
        rule_table_id = _string_value(_catalogue_value(row, "table_id"))
        if table_id and rule_table_id != table_id:
            continue
        if not _is_active_guardrail_rule(row):
            continue
        candidates.append(row)
    if not candidates:
        return None
    candidates.sort(key=lambda row: (int(_catalogue_value(row, "configuration_version") or 0), metadata_timestamp_sort_key(_catalogue_value(row, "approved_at", "created_at", "_committed_at"))), reverse=True)
    return candidates[0]

def _contract_payload(row: dict[str, Any]) -> dict[str, Any]:
    """Return and minimally validate one frozen Data Contract payload."""
    try:
        payload = json.loads(str(row.get("contract_payload_json") or ""))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Active Data Contract contract_payload_json is invalid JSON.") from exc
    contract = payload.get("contract") if isinstance(payload, dict) else None
    table = payload.get("table") if isinstance(payload, dict) else None
    if not isinstance(contract, dict) or not isinstance(table, dict):
        raise ValueError("Active Data Contract payload must identify its contract and table.")
    if str(contract.get("contract_id") or "") != str(row.get("contract_id") or ""):
        raise ValueError("Active Data Contract payload contract_id does not match its version row.")
    if int(contract.get("contract_version") or 0) != int(row.get("contract_version") or 0):
        raise ValueError("Active Data Contract payload contract_version does not match its version row.")
    if str(table.get("table_id") or "") != str(row.get("table_id") or ""):
        raise ValueError("Active Data Contract payload table_id does not match its version row.")
    return payload



def resolve_data_contract_version(
    config,
    active_workspace_id: str,
    table_id: str,
    contract_id: str,
    contract_version: Any,
    *,
    spark_session=None,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve and validate one exact immutable Data Contract version."""
    try:
        requested_version = int(contract_version)
    except (TypeError, ValueError) as exc:
        raise ValueError("data_contract_version must identify an exact integer version.") from exc
    try:
        frame = read_lakehouse_table(
            DATA_CONTRACT_TABLE,
            store="Metadata",
            schema=metadata_table_physical_schema(config, DATA_CONTRACT_TABLE),
            context={**(context or {"config": config, "scope_workspace_id": active_workspace_id}), "_spark_session": spark_session},
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            raise ValueError(
                f"Data Contract {contract_id!r} version {requested_version} does not exist."
            ) from exc
        raise
    escaped_contract_id = contract_id.replace("'", "''")
    matches = [
        _row_to_dict(row)
        for row in frame.filter(
            f"`contract_id` = '{escaped_contract_id}' "
            f"AND `contract_version` = {requested_version}"
        ).limit(2).collect()
    ]
    if not matches:
        raise ValueError(f"Data Contract {contract_id!r} version {requested_version} does not exist.")
    if len(matches) > 1:
        raise RuntimeError(
            f"Data Contract integrity error: {contract_id!r} version {requested_version} has duplicate version rows."
        )
    row = dict(matches[0])
    if (row.get("source_id") or str(row.get("table_id") or "")) != table_id:
        raise ValueError(
            f"Data Contract {contract_id!r} version {requested_version} does not belong to table_id {table_id!r}."
        )
    if str(row.get("status") or "").strip().lower() != "frozen":
        raise ValueError(f"Data Contract {contract_id!r} version {requested_version} must be frozen before validation.")
    row["contract_payload"] = _contract_payload(row)
    return row


def prepare_pipeline_execution(table_ids, *, execution_plan, spark_session=None):
    """Validate explicit run authority and reuse its frozen contract snapshots."""
    if not isinstance(execution_plan, PipelineExecutionPlan):
        raise ValueError("An explicit PipelineExecutionPlan is required for every Read and Write.")
    plan = execution_plan
    config, active_workspace_id, runtime = resolve_fabric_context(context=plan.runtime_context)
    if active_workspace_id != plan.workspace_id or str(runtime.get("notebook_id") or "") != plan.notebook_id:
        raise ValueError("Execution plan workspace_id or notebook identity changed; create a new plan.")
    identities = json.loads(plan.participants_json)
    if set(table_ids) - set(identities):
        raise ValueError("Every Read/Write table must participate in the execution plan.")
    context = {**runtime, "config": config, "scope_workspace_id": active_workspace_id, "execution_plan": plan,
               "_pipeline_contracts": json.loads(plan.contracts_json),
               "_pipeline_rules": {}, "_pipeline_identities": identities}
    # Isolate transient Dry Run caches without replacing persisted Fabric audit identity.
    if plan.execution_mode == "dry_run":
        context["activity_id"] = plan.plan_id
    context.pop("data_contract_overrides", None)
    if plan.execution_mode == "governed":
        from fabricops_kit.activated_pipeline.shared import verify_governed_plan
        verify_governed_plan(plan, spark_session=spark_session)
    for table_id in identities:
        contract = context["_pipeline_contracts"].get(table_id)
        if identities[table_id].get("source_type") == "file" and contract is not None:
            payload = contract.get("contract_payload") or _contract_payload(contract)
            if payload.get("source") != file_participant_source(identities[table_id]):
                raise ValueError("File source or reader options differ from the exact frozen contract.")
        load_table_guardrail_rules(config, active_workspace_id, table_id=table_id, spark_session=spark_session, context=context)
    return context


def tested_contract_identities(context, table_ids):
    """Describe exact immutable versions covered by this diagnostic relationship."""
    return {
        table_id: {"contract_id": contract["contract_id"], "contract_version": contract["contract_version"],
                   "payload_sha256": hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest()}
        for table_id in table_ids
        if (contract := context["_pipeline_contracts"].get(table_id)) is not None
    }


def source_guardrail_results(context, sources):
    """Enforce each configured Read rule before consuming its source in Write.

    No Contract, empty rule lists and disabled checks impose no requirement.
    Results must belong to this plan and exact frozen rule revision; a caught
    failed Read cannot authorize publication using an earlier successful result.
    """
    plan = context["execution_plan"]
    outcomes = []
    for source in sources:
        table_id = participant_id(source)
        identity_field = "source_id" if source.get("source_type") == "file" else "table_id"
        contract = context["_pipeline_contracts"].get(table_id)
        if contract is None:
            continue
        for rule in context["_pipeline_rules"].get(table_id, []):
            kind = rule["guardrail_type"]
            if kind not in {"schema", "grain", "freshness", "data_quality"}:
                continue
            if kind == "freshness" and rule.get("rule_type") == "skip":
                continue
            def matches(row):
                if kind == "grain":
                    try:
                        scope = json.loads(row.get("result_payload_json") or "{}").get("validation_scope")
                    except (TypeError, ValueError, AttributeError):
                        return False
                    if scope not in {"read_full", "read_incremental_batch"}:
                        return False
                return all(row.get(key) == value for key, value in {
                    identity_field: table_id, "contract_id": contract["contract_id"],
                    "contract_version": contract["contract_version"], "guardrail_type": kind,
                    "guardrail_rule_id": rule["guardrail_rule_id"],
                    "guardrail_version": rule.get("guardrail_version", 1),
                }.items())
            saved = [row for row in source.get("guardrail_outcomes", []) if matches(row)]
            current = [row for row in plan.results if matches(row)]
            def permits(rows):
                if not rows:
                    return False
                latest = max(metadata_timestamp_sort_key(row.get("_committed_at")) for row in rows)
                return all(row.get("can_continue") is True and str(row.get("status")).lower() in {
                    "passed", "pass", "warning", "warn", "baseline_created"
                } for row in rows if metadata_timestamp_sort_key(row.get("_committed_at")) == latest)
            allowed = permits(saved) and permits(current)
            outcome = {identity_field: table_id, "guardrail_rule_id": rule["guardrail_rule_id"],
                       "guardrail_type": kind, "action": rule.get("action"), "can_continue": allowed,
                       "status": ("warning" if any(str(row.get("status")).lower() in {"warn", "warning"}
                                                  for row in saved) else "passed") if allowed else "blocked"}
            outcomes.append(outcome)
            if not allowed and plan.permits_persistence:
                raise RuntimeError(f"Source {table_id!r} configured {kind} Guardrail has no successful Read result for this plan and contract revision.")
    return outcomes


def pipeline_guardrail_types(context, table_id):
    """Return configured active Guardrail types for a resolved participant."""
    return {str(row.get("guardrail_type") or "").lower() for row in context["_pipeline_rules"].get(table_id, [])}


def print_pipeline_contract(context, table_id, *, operation, guardrails, verbose):
    """Explain the contract decision once before the planned execution stages."""
    if not verbose:
        return
    contract = context["_pipeline_contracts"].get(table_id)
    if contract is None and any(context["_pipeline_contracts"].values()):
        print("No target Data Contract selected; enforcing configured source Guardrails.")
    elif contract is None:
        print(f"No Data Contract selected; no Guardrails. Continuing with {operation.title()}.")
    elif guardrails:
        print(f"Data Contract v{contract['contract_version']} · Checking {', '.join(guardrails)}.")
    else:
        print(f"Data Contract v{contract['contract_version']} · No applicable {operation.title()} Guardrails.")


def resolve_pipeline_data_contract(
    config,
    active_workspace_id: str,
    table_id: str,
    *,
    spark_session=None,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Resolve only an explicit plan snapshot; Governed snapshots come from activation."""
    cache = (context or {}).get("_pipeline_contracts")
    if cache is not None and table_id in cache:
        return cache[table_id]
    raise ValueError("Data Contract resolution requires an explicit execution plan; Governed authority is activated metadata.")


def resolve_catalogue_table_id(
    config,
    active_workspace_id: str,
    *,
    store_type: str,
    layer: str,
    schema_name: str | None,
    table_name: str,
    spark_session=None,
) -> str:
    """Resolve one physical runtime table to its canonical Catalogue identity."""
    frame = read_lakehouse_table(
        CATALOGUE_TABLE, store="Metadata",
        schema=metadata_table_physical_schema(config, CATALOGUE_TABLE),
        context={"config": config, "scope_workspace_id": active_workspace_id, "_spark_session": spark_session},
    )
    expected = tuple(str(value or "").strip().lower() for value in (store_type, layer, schema_name, table_name))
    matches = []
    for raw in frame.collect():
        row = _row_to_dict(raw)
        actual = tuple(str(row.get(name) or "").strip().lower() for name in ("store_type", "layer", "schema_name", "table_name"))
        if (
            str(row.get("workspace_id") or "") == active_workspace_id
            and (str(row.get("metadata_level") or "").lower() == "table" or not row.get("column_id"))
            and row.get("is_active") is not False
            and actual == expected
        ):
            matches.append(str(row.get("table_id") or ""))
    identities = sorted(set(value for value in matches if value))
    if not identities:
        raise ValueError(
            f"No active Catalogue table matches runtime table {table_name!r}; "
            "profile and register the table before enforcing its Data Contract."
        )
    if len(identities) > 1:
        raise RuntimeError(f"Catalogue integrity error: runtime table {table_name!r} resolves to multiple table_id values.")
    return identities[0]


def resolve_catalogue_table_identity(
    config,
    active_workspace_id: str,
    table_id: str,
    *,
    spark_session=None,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one active registered Catalogue table by canonical table identity."""
    canonical_id = str(table_id or "").strip()
    if not canonical_id:
        raise ValueError("table_id must be a non-empty canonical FabricOps table identity.")
    cache = (context or {}).get("_pipeline_identities")
    if cache is not None and canonical_id in cache:
        return cache[canonical_id]
    frame = read_lakehouse_table(
        CATALOGUE_TABLE,
        store="Metadata",
        schema=metadata_table_physical_schema(config, CATALOGUE_TABLE),
        context={
            **(dict(context) if context is not None else {"config": config, "scope_workspace_id": active_workspace_id}),
            "_fabricops_suppress_io_log": True,
            "_spark_session": spark_session,
        },
    )
    matches = []
    if hasattr(frame, "where"):
        from pyspark.sql import functions as F
        frame = frame.where((F.col("table_id") == canonical_id) & (F.col("workspace_id") == active_workspace_id) & (F.col("metadata_level") == "table"))
    for raw in frame.collect():
        row = decode_metadata_row(CATALOGUE_TABLE, _row_to_dict(raw))
        if (
            str(row.get("workspace_id") or "") == active_workspace_id
            and str(row.get("table_id") or "").strip() == canonical_id
            and str(row.get("metadata_level") or "").strip().lower() == "table"
            and not str(row.get("column_id") or "").strip()
            and row.get("is_active") is not False
        ):
            matches.append(row)
    if not matches:
        raise ValueError(
            f"No active registered Catalogue table exists for table_id {canonical_id!r} "
            f"in workspace_id {active_workspace_id!r}."
        )
    if len(matches) != 1:
        raise RuntimeError(
            f"Catalogue integrity error: table_id {canonical_id!r} resolves to "
            f"{len(matches)} active table identities."
        )
    row = dict(matches[0])
    required = ("store_type", "layer", "table_name")
    missing = [name for name in required if not str(row.get(name) or "").strip()]
    if missing:
        raise ValueError(
            f"Catalogue table_id {canonical_id!r} is not a registered table identity; "
            f"missing {', '.join(missing)}."
        )
    store_type = str(row["store_type"]).strip().lower()
    if store_type not in {"lakehouse", "warehouse"}:
        raise ValueError(
            f"Catalogue table_id {canonical_id!r} has unsupported store_type {store_type!r}."
        )
    identity = {
        **row,
        "table_id": canonical_id,
        "store_type": store_type,
        "store": str(row["layer"]).strip(),
        "schema": str(row.get("schema_name") or "").strip() or None,
        "table_name": str(row["table_name"]).strip(),
    }

    if cache is not None:
        cache[canonical_id] = identity
    return identity


def catalogue_authored_processing(identity: Mapping[str, Any]) -> dict[str, Any]:
    """Return current processing authoring from a Catalogue table identity."""
    strategy = str(identity.get("load_strategy") or "").strip()
    parameters = identity.get("load_strategy_parameters_json") or {}
    return {"load_strategy": strategy, **{name: value for name, value in parameters.items() if value is not None}}


def validate_grain_parameters(parameters, *, active=True):
    """Validate a singular table Grain key; inactive definitions may have no key.

    Grain rejects SQL null in any key component. Empty strings are values.
    The key combination is unique within the evaluated DataFrame only.
    """
    if not isinstance(parameters, dict):
        raise ValueError("Grain parameters must be an object.")
    if set(parameters) - {"columns"}:
        raise ValueError("Grain supports only configured key columns.")
    columns = parameters.get("columns", [])
    if (not isinstance(columns, list)
            or any(not isinstance(name, str) or not name.strip() for name in columns)
            or len(set(columns)) != len(columns)
            or any(name != name.strip() for name in columns)):
        raise ValueError("Grain columns must be distinct non-blank column names.")
    if active and not columns:
        raise ValueError("Enforced Grain requires at least one key column.")
    return {"columns": list(columns)}


def contract_guardrail_rows(contract: dict[str, Any], *, workspace_id: str, table_id: str) -> list[dict[str, Any]]:
    """Adapt frozen contract Guardrails to the existing runtime rule shape."""
    payload = contract.get("contract_payload") or _contract_payload(contract)
    table = payload.get("table")
    if not isinstance(table, dict) or "columns" not in table:
        raise ValueError("Active Data Contract table.columns is missing.")
    columns = table["columns"]
    if not isinstance(columns, list):
        raise ValueError("Active Data Contract table.columns must be a list.")
    expected_schema: dict[str, str] = {}
    column_names_by_id: dict[str, str] = {}
    for index, column in enumerate(columns):
        if not isinstance(column, dict):
            raise ValueError(f"Active Data Contract table.columns[{index}] must be an object.")
        column_id = str(column.get("column_id") or "").strip()
        column_name = str(column.get("column_name") or "").strip()
        data_type = str(column.get("data_type") or "").strip()
        if not column_id or not column_name or not data_type:
            raise ValueError(
                f"Active Data Contract table.columns[{index}] must define non-blank column_id, column_name, and data_type."
            )
        if column_name in expected_schema:
            raise ValueError(f"Active Data Contract table.columns contains duplicate column_name {column_name!r}.")
        expected_schema[column_name] = data_type
        column_names_by_id[column_id] = column_name
    required_columns = [str(column["column_name"]) for column in columns if column.get("presence", "required") == "required"]
    rules = payload.get("guardrails")
    if not isinstance(rules, list):
        raise ValueError("Active Data Contract guardrails must be a list.")
    authored_schema = next((rule for rule in rules if rule.get("guardrail_type") == "schema"), {})
    structural = {
        "guardrail_rule_id": authored_schema.get("guardrail_rule_id") or str(uuid5(NAMESPACE_URL, f"fabricops-schema:{contract['contract_id']}:{contract['contract_version']}")),
        "guardrail_version": int(authored_schema.get("guardrail_version") or 1), "guardrail_type": "schema", "rule_id": "contract_schema", "rule_type": "strict",
        "action": "Block", "is_active": True,
        "rule_parameters": {"required_columns": required_columns},
    }
    adapted = []
    for raw in [structural, *[rule for rule in rules if rule.get("guardrail_type") not in {"schema", "source_drift"} ]]:
        if not isinstance(raw, dict):
            raise ValueError("Active Data Contract contains an invalid Guardrail definition.")
        if raw.get("is_active", True) is False:
            continue
        params = raw.get("rule_parameters") or {}
        if not isinstance(params, dict):
            raise ValueError("Active Data Contract Guardrail rule_parameters must be an object.")
        if str(raw.get("guardrail_type") or "").strip().lower() == "schema":
            params = {
                **{
                    name: value for name, value in params.items()
                    if name not in {"columns", "data_types", "selected_columns", "expected_data_types"}
                },
                "columns": list(expected_schema),
                "data_types": expected_schema,
            }
            if "required_columns" in params:
                params["required_columns"] = [
                    column_names_by_id.get(str(column), str(column))
                    for column in params["required_columns"]
                ]
        if str(raw.get("guardrail_type") or "").strip().lower() == "grain":
            params = validate_grain_parameters(params)
            if raw.get("column_id") or raw.get("rule_type") != "uniqueness":
                raise ValueError("Grain requires a table-level uniqueness rule.")
            if set(params["columns"]) - set(expected_schema):
                raise ValueError("Grain references columns outside the Data Contract.")
            if raw.get("action", "Block") not in {"Warn", "Block"}:
                raise ValueError("Grain policy must be Warn or Block.")
            if any(row.get("managed_by") == "grain" for row in adapted):
                raise ValueError("A Data Contract has one Grain definition.")
        adapted.append({
            **{name: value for name, value in raw.items() if name not in {"rule_parameters", "severity"}},
            **({"guardrail_type": "data_quality", "managed_by": "grain"} if raw.get("guardrail_type") == "grain" else {}),
            "table_id": table_id,
            "column_name": column_names_by_id.get(str(raw.get("column_id") or ""), ""),
            "workspace_id": workspace_id,
            "rule_parameters_json": json.dumps({**params, **({"require_non_null": True, "maximum_failure_percent": 0} if raw.get("guardrail_type") == "grain" else {})}, sort_keys=True),
            "is_active": True,
            "activation_state": "active",
            "review_status": "governance_approved",
            "configuration_version": int(raw.get("guardrail_version") or 1),
        })
    return adapted


def validated_processing(processing: Any) -> dict[str, Any]:
    """Return a valid Engineering-owned executable processing definition."""
    if not isinstance(processing, dict):
        raise ValueError("Engineering processing definition is missing or malformed.")
    strategy = str(processing.get("load_strategy") or "").strip().lower()
    if strategy not in {"overwrite", "append_all", "append_new_only", "scd1", "scd2"}:
        raise ValueError("Processing definition has an invalid load_strategy.")
    definition = {**processing, "load_strategy": strategy}
    allowed = {
        "overwrite": {"load_strategy", "watermark_column"},
        "append_all": {"load_strategy", "watermark_column"},
        "append_new_only": {"load_strategy", "watermark_column"},
        "scd1": {"load_strategy", "key_columns", "watermark_column"},
        "scd2": {
            "load_strategy", "key_columns", "effective_column", "tracked_columns", "watermark_column",
        },
    }[strategy]
    unexpected = sorted(set(definition) - allowed)
    if unexpected:
        raise ValueError(f"Processing definition for {strategy} contains unsupported fields: {', '.join(unexpected)}.")
    for name in ("key_columns", "tracked_columns"):
        if name not in definition:
            continue
        values = definition[name]
        if not isinstance(values, list | tuple) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError(f"Processing definition {name} must be a non-empty sequence of column names.")
        definition[name] = [value.strip() for value in values]
    if strategy in {"scd1", "scd2"} and "key_columns" not in definition:
        raise ValueError(f"Processing definition for {strategy} requires key_columns.")
    for name in ("effective_column", "watermark_column"):
        if name in definition and (not isinstance(definition[name], str) or not definition[name].strip()):
            raise ValueError(f"Processing definition {name} must be a non-empty column name.")
        if name in definition:
            definition[name] = definition[name].strip()
    if strategy == "scd2" and "effective_column" not in definition:
        raise ValueError("Processing definition for scd2 requires effective_column.")
    return definition


def validated_pipeline_processing(*, role, read_mode, write_mode, read_parameters, write_parameters, repartition_by):
    """Validate and snapshot the exact Engineering parameters retained for approval."""
    if role == "source":
        if read_mode not in {"full", "incremental"} or write_mode is not None or write_parameters is not None or repartition_by is not None:
            raise ValueError("Invalid source processing configuration.")
        parameters = read_parameters if read_parameters is not None else {}
        if not isinstance(parameters, dict) or set(parameters) - {"watermark_column"}:
            raise ValueError("Invalid read_parameters; only watermark_column is supported.")
        if read_mode == "incremental":
            if not isinstance(parameters.get("watermark_column"), str) or not parameters["watermark_column"].strip():
                raise ValueError("Incremental reads require an explicit watermark_column.")
        elif parameters:
            raise ValueError("Full reads do not accept read_parameters.")
        return {"read_parameters": dict(parameters), "write_parameters": None, "repartition_by": None}
    if role != "target" or read_mode is not None or read_parameters is not None:
        raise ValueError("Invalid target processing configuration.")
    parameters = write_parameters if write_parameters is not None else {}
    if not isinstance(parameters, dict) or set(parameters) - {"watermark_column", "key_columns", "effective_column", "tracked_columns"}:
        raise ValueError("Invalid write_parameters.")
    validated_processing({**parameters, "load_strategy": write_mode})
    if repartition_by is not None and (type(repartition_by) is not int or repartition_by < 1):
        raise ValueError("repartition_by must be a positive integer.")
    return {"read_parameters": None, "write_parameters": json.loads(canonical_pipeline_json(parameters)), "repartition_by": repartition_by}


def resolve_scd2_tracked_columns(columns: list[str], processing: Mapping[str, Any]) -> list[str]:
    """Return explicit or default business columns used to detect SCD2 changes."""
    explicit = processing.get("tracked_columns")
    if explicit:
        invalid = sorted(
            name for name in explicit
            if name not in columns
            or name in {*processing["key_columns"], processing["effective_column"], *_TARGET_TECHNICAL_COLUMNS}
            or name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES)
        )
        if invalid:
            raise ValueError(f"SCD2 tracked_columns must contain only business columns: {', '.join(invalid)}.")
        return list(explicit)
    excluded = {
        *processing["key_columns"],
        processing["effective_column"],
        *_TARGET_TECHNICAL_COLUMNS,
    }
    return [
        name for name in columns
        if name not in excluded and not name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]


def resolve_scd1_business_columns(columns: list[str], key_columns: list[str]) -> list[str]:
    """Return non-key business columns eligible for SCD change detection."""
    return [
        name for name in columns
        if name not in {*key_columns, *_TARGET_TECHNICAL_COLUMNS}
        and not name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]


def resolve_target_audit_fields(context: Mapping[str, Any] | None) -> dict[str, Any]:
    """Resolve one compact, run-consistent audit record for business target rows."""
    runtime_context = dict(context or {})
    values = build_pipeline_audit_fields(
        config=runtime_context.get("config"),
        active_workspace_id=runtime_context.get("scope_workspace_id"),
        runtime_context=runtime_context,
    )
    return {name: values[name] for name in _TARGET_AUDIT_COLUMNS}


def add_target_audit_fields(df, audit_fields: Mapping[str, Any]):
    """Add resolved operational audit literals to incoming target rows."""
    from pyspark.sql import functions as F

    result = df if "_row_hash" in df.columns else add_row_hash(df)
    for name in _TARGET_AUDIT_COLUMNS:
        result = result.withColumn(name, F.lit(audit_fields[name]))
    return result


def validate_processing_input(dataframe, processing):
    """Evaluate common strategy input checks without staging or publication."""
    definition = validated_processing(dict(processing))
    strategy = definition["load_strategy"]
    columns = list(getattr(dataframe, "columns", ()))
    if not columns or len(columns) != len(set(columns)):
        raise ValueError("Prepared input must have unique named columns.")
    if strategy not in {"scd1", "scd2"}:
        return
    from pyspark.sql import functions as F

    keys = list(definition["key_columns"])
    if len(columns) != len(set(columns)) or set(keys) - set(columns):
        raise ValueError("SCD input must have unique named columns and all business keys.")
    if dataframe.where(reduce(lambda a, b: a | b, [F.col(key).isNull() for key in keys])).limit(1).count():
        raise ValueError("Incoming target scope contains null business keys.")
    if dataframe.groupBy(*keys).count().where(F.col("count") > 1).limit(1).count():
        raise ValueError("Incoming target scope contains duplicate business keys.")
    if strategy == "scd2":
        if definition["effective_column"] not in columns:
            raise ValueError("SCD2 input is missing its effective_column.")
        resolve_scd2_tracked_columns(columns, definition)
    else:
        resolve_scd1_business_columns(columns, keys)


def execute_lakehouse_processing(
    df,
    *,
    table_name: str,
    store: str,
    schema: str | None,
    processing: Mapping[str, Any],
    scope: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
) -> None:
    """Apply one already-resolved governed load definition to a Lakehouse target."""
    strategy = validated_processing(dict(processing))["load_strategy"]
    scope_type = str(scope.get("type") or "").strip()
    if scope_type != "full_dataset":
        raise ValueError("Write processing scope must use full_dataset.")

    columns = set(getattr(df, "columns", ()))
    persisted_df = df
    if not set(_TARGET_AUDIT_COLUMNS) <= columns:
        persisted_df = add_target_audit_fields(df, resolve_target_audit_fields(context))

    if strategy in {"append_all", "append_new_only"}:
        write_lakehouse_table(persisted_df, table_name, store=store, schema=schema, mode="append", context=context)
        return
    if strategy == "overwrite":
        write_lakehouse_table(persisted_df, table_name, store=store, schema=schema, mode="overwrite", context=context)
        return

    from delta.tables import DeltaTable
    from pyspark.sql import functions as F

    _store, _table, _schema, path = resolve_configured_lakehouse_table(store, table_name, schema, context=context)
    keys = list(processing["key_columns"])
    validate_processing_input(persisted_df, processing)
    if not DeltaTable.isDeltaTable(df.sparkSession, path):
        receipt = (context or {}).get("_fabricops_publication_receipt")
        options = {"userMetadata": json.dumps(receipt, sort_keys=True)} if receipt else None
        write_lakehouse_table(persisted_df, table_name, store=store, schema=schema, mode="overwrite", options=options, context=context)
        return
    merge_session = df.sparkSession
    receipt = (context or {}).get("_fabricops_publication_receipt")
    if receipt:
        merge_session = df.sparkSession.newSession()
        # Keep the caller's processing semantics while isolating commit tags.
        for name in ("spark.sql.session.timeZone", "spark.sql.caseSensitive",
                     "spark.sql.ansi.enabled", "spark.sql.storeAssignmentPolicy"):
            merge_session.conf.set(name, df.sparkSession.conf.get(name))
        merge_session.conf.set("spark.databricks.delta.schema.autoMerge.enabled",
                               df.sparkSession.conf.get("spark.databricks.delta.schema.autoMerge.enabled", "false"))
        merge_session.conf.set("spark.databricks.delta.commitInfo.userMetadata", json.dumps(receipt, sort_keys=True))
    delta = DeltaTable.forPath(merge_session, path)
    condition = " AND ".join(f"target.`{key}` <=> source.`{key}`" for key in keys)
    metrics = (context or {}).get("_fabricops_write_metrics")

    def capture_merge_metrics() -> None:
        """Decode the tagged MERGE commit without starting another Spark job."""
        if not isinstance(metrics, dict) or not receipt:
            return
        from fabricops_kit.io.shared import DeltaCommitMetrics

        native = DeltaCommitMetrics(token=json.dumps(receipt, sort_keys=True)).read_metrics(
            merge_session, path, operation="MERGE"
        )
        if native is None:
            return
        inserted = native.get("numTargetRowsInserted")
        updated = native.get("numTargetRowsUpdated")
        if inserted is None:
            return
        if strategy == "scd1":
            metrics.update(
                rows_inserted=inserted,
                measurement_source="delta_merge",
            )
        else:
            metrics.update(
                versions_inserted=inserted,
                measurement_source="delta_merge",
            )
        if updated is not None:
            metrics["rows_committed"] = inserted + updated

    if strategy == "scd1":
        business_columns = resolve_scd1_business_columns(list(df.columns), keys)
        change = " OR ".join(f"NOT (target.`{name}` <=> source.`{name}`)" for name in business_columns) or "FALSE"
        technical_updates = {
            name: f"source.`{name}`" for name in persisted_df.columns
            if name in _TARGET_TECHNICAL_COLUMNS or name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES)
        }
        merge = delta.alias("target").merge(persisted_df.alias("source"), condition).whenMatchedUpdateAll(condition=change)
        if technical_updates:
            merge = merge.whenMatchedUpdate(set=technical_updates)
        merge.whenNotMatchedInsertAll().execute()
        capture_merge_metrics()
        return

    effective = str(processing["effective_column"])
    tracked = resolve_scd2_tracked_columns(list(df.columns), processing)
    current_column, end_column = "_is_current", "_effective_to"
    current_rows = delta.toDF().where(F.col(current_column))
    if current_rows.groupBy(*keys).count().where(F.col("count") > 1).limit(1).count():
        raise RuntimeError("SCD2 target contains multiple current records for one or more business keys.")
    change = " OR ".join(f"NOT (target.`{name}` <=> source.`{name}`)" for name in tracked) or "FALSE"
    technical_updates = {
        name: f"source.`{name}`" for name in persisted_df.columns
        if (name in _TARGET_TECHNICAL_COLUMNS or name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES))
        and name not in {*_SCD2_LIFECYCLE_COLUMNS, "_row_hash"}
    }
    if "_row_hash" in persisted_df.columns:
        # Only technical fields are refreshed on an unchanged version. In particular,
        # effective/untracked business values remain from the stored version.
        values = {
            name: F.col(
                ("source." if name in technical_updates else "target.")
                + "`" + name.replace("`", "``") + "`"
            )
            for name in persisted_df.columns
        }
        technical_updates["_row_hash"] = row_hash_expression(persisted_df, values=values)
    merge_keys = [f"_fabricops_merge_key_{index}" for index, _key in enumerate(keys)]
    reserved = sorted(set(merge_keys) & set(persisted_df.columns))
    if reserved:
        raise ValueError(f"Incoming target scope uses reserved SCD2 columns: {', '.join(reserved)}.")
    current_for_change = current_rows.select(
        *[F.col(name) for name in keys],
        *[F.col(name).alias(f"_fabricops_current_{index}") for index, name in enumerate(tracked)],
    )
    joined = persisted_df.alias("incoming").join(current_for_change.alias("current"), on=keys, how="inner")
    changed_expression = reduce(
        lambda left, right: left | right,
        [
            ~F.col(f"incoming.`{name}`").eqNullSafe(F.col(f"current.`_fabricops_current_{index}`"))
            for index, name in enumerate(tracked)
        ],
        F.lit(False),
    )
    changed_matches = joined.where(changed_expression)
    current_starts = current_rows.select(
        *[F.col(name) for name in keys],
        F.col("_effective_from").alias("_fabricops_previous_start"),
    )
    invalid_time = (
        changed_matches.select("incoming.*")
        .join(current_starts, on=keys, how="inner")
        .where(F.col(effective).isNull() | (F.col(effective) <= F.col("_fabricops_previous_start")))
    )
    if invalid_time.limit(1).count():
        raise ValueError("Changed SCD2 rows require an effective time later than the current version start.")
    changed_existing = changed_matches.select("incoming.*")
    keyed = persisted_df
    inserts = changed_existing
    for merge_key, key in zip(merge_keys, keys, strict=True):
        keyed = keyed.withColumn(merge_key, F.col(key))
        inserts = inserts.withColumn(merge_key, F.lit(None).cast(persisted_df.schema[key].dataType))
    staged = keyed.unionByName(inserts)
    merge_condition = " AND ".join(
        f"target.`{key}` <=> source.`{merge_key}`"
        for key, merge_key in zip(keys, merge_keys, strict=True)
    ) + f" AND target.`{current_column}` = TRUE"
    merge = (
        delta.alias("target").merge(staged.alias("source"), merge_condition)
        .whenMatchedUpdate(condition=change, set={current_column: "false", end_column: f"source.`{effective}`"})
    )
    if technical_updates:
        merge = merge.whenMatchedUpdate(condition=f"NOT ({change})", set=technical_updates)
    merge.whenNotMatchedInsert(
        values={name: f"source.`{name}`" for name in persisted_df.columns}
    ).execute()
    capture_merge_metrics()


def load_table_guardrail_rules(
    config,
    active_workspace_id: str,
    *,
    spark_session=None,
    table_id: str = "",
    context: Mapping[str, Any] | None = None,
):
    """Resolve Guardrails from the pipeline-selected Data Contract."""
    if not table_id:
        raise ValueError("Guardrail resolution requires a canonical Catalogue table_id.")
    cache = (context or {}).get("_pipeline_rules")
    if cache is not None and table_id in cache:
        return cache[table_id]
    contract = resolve_pipeline_data_contract(config, active_workspace_id, table_id, spark_session=spark_session, context=context)
    rows = contract_guardrail_rows(contract, workspace_id=active_workspace_id, table_id=table_id) if contract else []
    if cache is not None:
        cache[table_id] = rows
    return rows


def select_table_guardrail_rule(rules_df, *, guardrail_type: str, table_id: str, workspace_id: str = "") -> dict | None:
    """Select the latest active approved table rule by canonical identity."""
    return _select_table_guardrail_rule(
        rules_df, guardrail_type=guardrail_type, dataset_name="", table_name="",
        workspace_id=workspace_id, table_id=table_id,
    )



def _apply_bypass_post_review_warning(result: dict, rule: dict | None) -> dict:
    if rule and _rule_review_status(rule) == "active_pending_governance_review":
        reason = str(result.get("reason") or result.get("message") or "")
        message = _BYPASS_POST_REVIEW_WARNING if not reason else f"{reason} {_BYPASS_POST_REVIEW_WARNING}"
        result["reason"] = message
        result["message"] = message
        result["bypass_warning"] = _BYPASS_POST_REVIEW_WARNING
    return result

class SchemaDriftError(Exception):
    """Raised when a guardrail check is configured to stop execution.

    Notes
    -----
    This exception is shared by schema-check workflows so notebook callers
    have one failure type to catch when they choose fail-fast behavior.

    """

def _normalize_datatype(data_type) -> str:
    raw = str(data_type).strip().lower()
    raw = re.sub(r"\s+", "", raw)

    decimal_match = re.search(r"decimaltype\((\d+),(\d+)\)|decimal\((\d+),(\d+)\)", raw)
    if decimal_match:
        precision = decimal_match.group(1) or decimal_match.group(3)
        scale = decimal_match.group(2) or decimal_match.group(4)
        return f"decimal({precision},{scale})"

    aliases = {
        "integertype()": "int",
        "integertype": "int",
        "integer": "int",
        "int32": "int",
        "int": "int",
        "longtype()": "bigint",
        "longtype": "bigint",
        "long": "bigint",
        "int64": "bigint",
        "bigint": "bigint",
        "stringtype()": "string",
        "stringtype": "string",
        "str": "string",
        "object": "string",
        "string": "string",
        "datetype()": "date",
        "datetype": "date",
        "date": "date",
        "timestamptype()": "timestamp",
        "timestamptype": "timestamp",
        "timestamp": "timestamp",
        "datetime64[ns]": "timestamp",
        "doubletype()": "double",
        "doubletype": "double",
        "double": "double",
        "float64": "double",
        "floattype()": "float",
        "floattype": "float",
        "float32": "float",
        "float": "float",
        "booleantype()": "boolean",
        "booleantype": "boolean",
        "bool": "boolean",
        "boolean": "boolean",
    }
    return aliases.get(raw, raw)

def _actual_schema(df) -> tuple[list[str], dict[str, str]]:
    schema = getattr(df, "schema", None)
    if schema is not None and hasattr(schema, "fields"):
        columns = [str(field.name) for field in schema.fields]
        types = {str(field.name): _normalize_datatype(getattr(field, "dataType", "")) for field in schema.fields}
        return columns, types

    dtypes = getattr(df, "dtypes", None)
    if dtypes is not None:
        dtype_items = dtypes.items() if hasattr(dtypes, "items") else dtypes
        types = {str(name): _normalize_datatype(dtype) for name, dtype in dtype_items}
        columns = [str(column) for column in getattr(df, "columns", list(types))]
        return columns, types

    columns = [str(column) for column in getattr(df, "columns", [])]
    return columns, {}







_SCHEMA_PRESETS = {"strict", "allow_new_columns", "monitor_only"}

def _guardrail_schema_check_base(
    dataframe,
    expected_schema: dict[str, str] | None = None,
    *,
    preset: str = "strict",
    rules_df=None,
    dataset_name: str = "",
    table_name: str = "",
    workspace_id: str = "",
    table_id: str = "",
) -> dict:
    """Apply an internal runtime schema check for the governed runtime checks.

    This helper is not a notebook-facing callable. It preserves runtime schema
    enforcement for widget-led guardrail flows without exposing a public schema
    validation API.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    expected_schema : dict[str, str]
        Mapping of required column names to expected datatype strings.
    preset : {"strict", "allow_new_columns", "monitor_only"}, default="strict"
        Schema validation intent. ``strict`` blocks missing columns, datatype
        changes, and unexpected columns. ``allow_new_columns`` blocks missing
        columns and datatype changes while reporting additional columns as a
        warning. ``monitor_only`` reports all differences without blocking.
    rules_df : DataFrame or iterable of mappings, optional
        Approved schema rules used instead of ``expected_schema``.
    dataset_name : str, optional
        Dataset identity used to select an approved rule.
    table_name : str, optional
        Table identity used to select an approved rule.
    workspace_id : str, optional
        Workspace identity used to select an approved rule.
    table_id : str, optional
        Canonical table identity used to select an approved rule.

    Returns
    -------
    dict
        Standard guardrail result with ``status``, ``can_continue``,
        ``checks``, and ``message`` plus detailed schema difference fields.

    Raises
    ------
    ValueError
        If ``preset`` is not one of the supported schema presets.

    Notes
    -----
    This private helper is called by the governed runtime checks only. Notebook
    authors should use widget-authored rules and the guardrail gate instead of
    calling schema validation helpers directly.

    """
    rule = None
    rule_type = ""
    severity = "blocking"
    if rules_df is None and expected_schema is not None and not isinstance(expected_schema, dict):
        rules_df, expected_schema = expected_schema, None
    if rules_df is not None:
        rule = _select_table_guardrail_rule(rules_df, guardrail_type="schema", dataset_name=dataset_name, table_name=table_name, workspace_id=workspace_id, table_id=table_id)
        if not rule:
            expected_schema, preset = {}, "monitor_only"
        else:
            params = _parse_rule_parameters(rule)
            expected = params.get("data_types") or params.get("expected_data_types") or {}
            selected_columns = params.get("columns") or params.get("selected_columns") or list(expected)
            expected_schema = {column: expected.get(column, "") for column in selected_columns}
            rule_type = _string_value(_catalogue_value(rule, "rule_type") or "relaxed").lower()
            preset = {"strict": "strict", "minimum_required": "allow_new_columns", "relaxed": "allow_new_columns", "skip": "monitor_only"}.get(rule_type, "allow_new_columns")
            severity = _string_value(("blocking" if str(_catalogue_value(rule, "action") or "Block").casefold() == "block" else "warning")).lower()
    elif expected_schema is None:
        raise ValueError("expected_schema is required when rules_df is not supplied")

    normalized_preset = str(preset).lower()
    if normalized_preset not in _SCHEMA_PRESETS:
        raise ValueError("preset must be one of: strict, allow_new_columns, monitor_only")
    if severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")

    actual_columns, actual_types = _actual_schema(dataframe)
    actual_set = set(actual_columns)
    expected_names = [str(column) for column in expected_schema]
    expected_set = set(expected_names)

    missing_columns = [column for column in expected_names if column not in actual_set]
    datatype_mismatches = []
    for column, expected_type in expected_schema.items():
        column_name = str(column)
        if column_name in actual_set and column_name in actual_types:
            expected = _normalize_datatype(expected_type)
            actual = actual_types[column_name]
            if actual != expected:
                datatype_mismatches.append({"column": column_name, "expected": expected, "actual": actual})

    checks = []
    for column in missing_columns:
        checks.append({"check": "missing_column", "column": column, "status": "failed", "passed": False})
    for mismatch in datatype_mismatches:
        checks.append({"check": "datatype_mismatch", **mismatch, "status": "failed", "passed": False})
    actual_unexpected = [column for column in actual_columns if str(column) not in expected_set]
    for column in actual_unexpected:
        checks.append({"check": "unexpected_column", "column": column, "status": "warning" if normalized_preset == "allow_new_columns" else "failed", "passed": normalized_preset == "allow_new_columns"})

    blocking = bool(missing_columns or datatype_mismatches)
    if normalized_preset == "strict":
        blocking = blocking or bool(actual_unexpected)
    if normalized_preset == "monitor_only":
        status = "warning" if checks else "passed"
        can_continue = True
    elif blocking:
        status = "failed"
        can_continue = False
    elif normalized_preset == "allow_new_columns" and actual_unexpected:
        status = "warning"
        can_continue = True
    else:
        status = "passed"
        can_continue = True
    if status == "failed" and severity == "warning":
        status = "warning"
        can_continue = True

    message = (
        "Schema validation passed."
        if status == "passed"
        else f"Schema validation {status}: {len(missing_columns)} missing, {len(actual_unexpected)} unexpected, {len(datatype_mismatches)} datatype mismatch(es)."
    )
    result = {
        "status": status,
        "can_continue": can_continue,
        "checks": checks,
        "message": message,
        "missing_columns": missing_columns,
        "unexpected_columns": actual_unexpected,
        "datatype_mismatches": datatype_mismatches,
        "preset": normalized_preset,
        "severity": severity,
    }
    if rule is not None:
        result.update({"guardrail_type": "schema", "rule_type": rule_type, "rule_key": _string_value(_catalogue_value(rule, "rule_key", "rule_id"))})
        return _apply_bypass_post_review_warning(result, rule)
    return result

def _row_to_dict(row) -> dict:
    if row is None:
        return {}
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "asDict"):
        return row.asDict(recursive=True)
    return {name: getattr(row, name) for name in dir(row) if not name.startswith("_")}



def _max_column_value(dataframe, column_name: str, *, config=None):
    if dataframe is None or not column_name:
        return None
    if hasattr(dataframe, "agg"):
        from pyspark.sql import functions as F

        aggregate = dataframe.agg(F.max(F.col(column_name)).alias("latest_value"))
        schema = getattr(aggregate, "schema", None)
        kind = type(schema["latest_value"].dataType).__name__ if schema is not None else ""
        if kind == "TimestampType":
            # Avoid interpreting collected naive datetime values as author input.
            rows = aggregate.select(F.unix_micros("latest_value").alias("latest_value")).collect()
            micros = rows[0]["latest_value"] if rows else None
            return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(microseconds=micros) if micros is not None else None
        rows = aggregate.collect()
        if not rows:
            return None
        row = rows[0]
        if isinstance(row, dict):
            return row.get("latest_value")
        if hasattr(row, "asDict"):
            return row.asDict().get("latest_value")
        try:
            return row["latest_value"]
        except Exception:
            return getattr(row, "latest_value", None)
    if isinstance(dataframe, dict):
        values = [dataframe.get(column_name)]
    else:
        values = []
        for row in dataframe or []:
            if isinstance(row, dict):
                values.append(row.get(column_name))
            elif hasattr(row, "asDict"):
                values.append(row.asDict().get(column_name))
            else:
                values.append(getattr(row, column_name, None))
    values = [value for value in values if value not in (None, "")]
    temporal = [_coerce_datetime(value, config) for value in values]
    if temporal and all(value is not None for value in temporal):
        return values[max(range(len(values)), key=lambda index: temporal[index].astimezone(UTC))]
    return max(values) if values else None

def _coerce_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None

def _coerce_datetime(value, config=None) -> datetime | None:
    """Preserve offsets and interpret date/naive freshness values in the audit zone."""
    if value in (None, ""):
        return None
    try:
        return normalize_audit_datetime(value, config)
    except ValueError:
        return None

def _iso_date_value(value) -> str:
    parsed = _coerce_date(value)
    return parsed.isoformat() if parsed is not None else ("" if value is None else str(value))

def freshness_check_core(
    dataframe,
    freshness_column: str | None = None,
    max_lag_days: int | str | None = None,
    severity: str = "blocking",
    *,
    reference_date: date | datetime | str | None = None,
    rules_df=None,
    dataset_name: str = "",
    table_name: str = "",
    workspace_id: str = "",
    table_id: str = "",
    config: Any = None,
) -> dict:
    """Enforce that a DataFrame contains recent enough data.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame or iterable of row-like mappings to check.
    freshness_column : str or None
        Column whose maximum value represents the latest available data date.
        When omitted, the freshness guardrail is skipped.
    max_lag_days : int or str or None
        Maximum allowed lag, in days, between ``reference_date`` and the latest
        value in ``freshness_column``. Required when ``freshness_column`` is set.
    severity : {"blocking", "warning"}, default="blocking"
        Whether stale data blocks continuation or returns a non-blocking warning.
    reference_date : date, datetime, str, optional
        Reference time. Defaults to the configured audit clock. Offsets preserve
        instants; dates and timezone-free values use the configured audit zone.
    rules_df : DataFrame or iterable of mappings, optional
        Approved freshness rules used instead of direct arguments.
    dataset_name : str, optional
        Dataset identity used to select an approved rule.
    table_name : str, optional
        Table identity used to select an approved rule.
    workspace_id : str, optional
        Workspace identity used to select an approved rule.
    table_id : str, optional
        Canonical table identity used to select an approved rule.
    config : FrameworkConfig or dict, optional
        Audit timezone for the reference clock and timezone-free inputs.

    Returns
    -------
    dict
        Standard guardrail result with ``status``, ``can_continue``,
        ``check_type``, latest value, required minimum value, and message.

    """
    rule = None
    rule_type = ""
    max_age_seconds = None
    if rules_df is None and freshness_column is not None and not isinstance(freshness_column, str):
        rules_df, freshness_column = freshness_column, None
    if rules_df is not None:
        rule = _select_table_guardrail_rule(rules_df, guardrail_type="freshness", dataset_name=dataset_name, table_name=table_name, workspace_id=workspace_id, table_id=table_id)
        if rule:
            params = _parse_rule_parameters(rule)
            rule_type = _string_value(_catalogue_value(rule, "rule_type") or "max_lag_days").lower()
            if rule_type != "skip":
                freshness_column = params.get("freshness_column") or params.get("column_name") or _catalogue_value(rule, "column_name")
                if params.get("maximum_age") not in (None, ""):
                    unit = str(params.get("maximum_age_unit") or "days").lower()
                    factors = {"minutes": 60, "hours": 3600, "days": 86400}
                    if unit not in factors:
                        raise ValueError("maximum_age_unit must be minutes, hours, or days")
                    max_age_seconds = float(params["maximum_age"]) * factors[unit]
                else:
                    max_lag_days = params.get("max_lag_days")
                    max_age_seconds = None
                severity = ("blocking" if str(_catalogue_value(rule, "action") or "Block").casefold() == "block" else "warning")

    dataframe_columns = set(getattr(dataframe, "columns", ()))
    if not dataframe_columns and isinstance(dataframe, (list, tuple)) and dataframe:
        dataframe_columns = set(_row_to_dict(dataframe[0]))
    observation_evidence = {"table_id", "partition_value", "change_column", "max_change_value", "_committed_at"} <= dataframe_columns
    if observation_evidence and rule_type != "skip":
        rows = dataframe.collect() if hasattr(dataframe, "collect") else dataframe
        change_columns = {_string_value(_catalogue_value(_row_to_dict(row), "change_column")) for row in rows or []}
        change_columns.discard("")
        if len(change_columns) != 1:
            raise ValueError("Observation evidence must contain one authoritative change_column.")
        observation_change_column = next(iter(change_columns))
        configured_freshness_column = str(freshness_column or "").strip()
        if configured_freshness_column and configured_freshness_column != observation_change_column:
            raise ValueError(
                "Active freshness rule is invalid for observation evidence: "
                f"freshness_column {configured_freshness_column!r} does not match change_column {observation_change_column!r}."
            )
        freshness_column = "max_change_value"
    column = str(freshness_column or "").strip()
    normalized_severity = str(severity or "blocking").lower().strip()
    if normalized_severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")

    base_result = {
        "status": "skipped",
        "can_continue": True,
        "check_type": "freshness",
        "freshness_column": column,
        "freshness_max_lag_days": "" if max_lag_days in (None, "") else max_lag_days,
        "freshness_severity": normalized_severity,
        "latest_value": "",
        "required_min_value": "",
        "freshness_status": "skipped",
        "freshness_can_continue": True,
        "freshness_message": "Freshness check skipped because no freshness column is configured.",
        "message": "Freshness check skipped because no freshness column is configured.",
    }
    if rule is not None:
        base_result.update({
            "guardrail_type": "freshness",
            "rule_type": rule_type,
            "rule_key": _string_value(_catalogue_value(rule, "rule_key", "rule_id")),
            "guardrail_rule_id": _string_value(_catalogue_value(rule, "guardrail_rule_id", "rule_id")),
            "guardrail_version": int(_catalogue_value(rule, "guardrail_version", "configuration_version") or 1),
            "rule_id": _string_value(_catalogue_value(rule, "rule_id")),
        })
    if not column:
        return _apply_bypass_post_review_warning(base_result, rule)
    if max_age_seconds is None and (max_lag_days is None or str(max_lag_days).strip() == ""):
        raise ValueError("max_lag_days is required when freshness_column is set")
    lag_days = int(max_lag_days or 0)
    if lag_days < 0:
        raise ValueError("max_lag_days must be greater than or equal to zero")
    base_result["freshness_max_lag_days"] = lag_days

    reference = _coerce_datetime(reference_date, config) if reference_date is not None else datetime.fromisoformat(get_current_audit_timestamp(config, drop_microseconds=False))
    if reference is None:
        raise ValueError("reference_date must be a date, datetime, or ISO date string")
    reference = reference.astimezone(UTC)
    required_min = reference - timedelta(seconds=max_age_seconds) if max_age_seconds is not None else reference - timedelta(days=lag_days)
    latest_raw = _max_column_value(dataframe, column, config=config)
    latest_date = _coerce_datetime(latest_raw, config)
    latest_display = latest_date.isoformat() if max_age_seconds is not None and latest_date else _iso_date_value(latest_raw)
    required_local = normalize_audit_datetime(required_min, config)
    required_display = required_local.isoformat() if max_age_seconds is not None else required_local.date().isoformat()
    base_result.update(latest_value=latest_display, required_min_value=required_display)

    if latest_date is not None and latest_date.astimezone(UTC) >= required_min:
        message = "Freshness check passed."
        base_result.update(
            status="passed",
            can_continue=True,
            freshness_status="passed",
            freshness_can_continue=True,
            freshness_message=message,
            message=message,
        )
        return _apply_bypass_post_review_warning(base_result, rule)

    message = f"Freshness check failed: latest {column} is older than allowed lag."
    status = "failed" if normalized_severity == "blocking" else "warning"
    can_continue = normalized_severity == "warning"
    base_result.update(
        status=status,
        can_continue=can_continue,
        freshness_status=status,
        freshness_can_continue=can_continue,
        freshness_message=message,
        message=message,
    )
    return _apply_bypass_post_review_warning(base_result, rule)


def _catalogue_value(row: dict, *names: str):
    for name in names:
        if name in row:
            return row.get(name)
        upper = name.upper()
        if upper in row:
            return row.get(upper)
        lower = name.lower()
        for key, value in row.items():
            if str(key).lower() == lower:
                return value
    return None

def _string_value(value) -> str:
    return "" if value is None else str(value)



def stop_if_failed(result) -> None:
    """Stop notebook execution when a guardrail result is blocking.

    Parameters
    ----------
    result : dict
        Direct schema, freshness, profile behavior, or DQ guardrail result.

    Raises
    ------
    SchemaDriftError
        If the resolved result has ``can_continue=False``.

    """
    resolved = (result or {}).get("result") if isinstance(result, dict) and "result" in result else result
    resolved = resolved or {}
    if bool(resolved.get("can_continue", True)):
        return
    status = resolved.get("status", "failed")
    detail = resolved.get("message") or resolved.get("summary") or "Guardrail blocked execution."
    raise SchemaDriftError(f"Guardrail blocked execution with status: {status}. {detail}")


def _canonical_dq_rule_type(rule_type: Any) -> str:
    return str(rule_type or "").strip()

def _normalize_dq_severity(severity: Any) -> str:
    """Normalize guardrail/DQ severity labels for DQ validation."""
    value = str(severity or "warning").strip().lower()
    return "error" if value in {"block", "blocking", "error"} else "warning"

def _spark_sql_helpers():
    """Return Spark SQL helper modules lazily for DQ runtime helpers."""
    try:
        from pyspark.sql import SparkSession, functions as F
        from pyspark.sql.window import Window
    except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
        raise RuntimeError("DQ enforcement helpers require pyspark in the active runtime.") from exc
    return SparkSession, F, Window


_CUSTOM_COLUMN_METHODS = {
    "isNull", "isNotNull", "isin", "rlike", "contains", "startswith", "endswith",
}


def _custom_expression_tree(expression: str) -> ast.Expression:
    """Parse the deliberately small, side-effect-free PySpark Column grammar."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Custom DQ expression is not valid Python expression syntax.") from exc
    allowed = (
        ast.Expression, ast.BinOp, ast.BitAnd, ast.BitOr,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
        ast.UnaryOp, ast.Invert, ast.USub, ast.UAdd,
        ast.Compare, ast.Eq, ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE,
        ast.Call, ast.Attribute, ast.Name, ast.Load, ast.Constant,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"Custom DQ expression contains unsupported syntax: {type(node).__name__}.")
        if isinstance(node, ast.Name) and node.id != "F":
            raise ValueError(f"Custom DQ expression contains unsupported name {node.id!r}.")
        if isinstance(node, ast.Call):
            is_col = (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "F"
                and node.func.attr in {"col", "lit"}
            )
            is_method = isinstance(node.func, ast.Attribute) and node.func.attr in _CUSTOM_COLUMN_METHODS
            if not (is_col or is_method) or node.keywords:
                raise ValueError(
                    "Custom DQ expression contains an unsupported call. Allowed operations are "
                    "F.col, F.lit, isNull, isNotNull, isin, rlike, contains, startswith, and endswith."
                )
            if is_col:
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant):
                    raise ValueError(f"{node.func.attr} requires exactly one literal argument.")
                if node.func.attr == "col" and not isinstance(node.args[0].value, str):
                    raise ValueError("F.col requires a literal string column name.")
            elif node.func.attr in {"isNull", "isNotNull"} and node.args:
                raise ValueError(f"{node.func.attr} does not accept arguments.")
            elif node.func.attr == "isin":
                if not node.args or not all(isinstance(argument, ast.Constant) for argument in node.args):
                    raise ValueError("isin requires one or more literal values.")
            elif node.func.attr in {"rlike", "contains", "startswith", "endswith"}:
                if (
                    len(node.args) != 1
                    or not isinstance(node.args[0], ast.Constant)
                    or not isinstance(node.args[0].value, str)
                ):
                    raise ValueError(f"{node.func.attr} requires exactly one literal string.")
        if isinstance(node, ast.BinOp) and not isinstance(
            node.op, (ast.BitAnd, ast.BitOr, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)
        ):
            raise ValueError("Custom DQ expression contains an unsupported binary operator.")
        if isinstance(node, ast.UnaryOp) and not isinstance(
            node.op, (ast.Invert, ast.USub, ast.UAdd)
        ):
            raise ValueError("Custom DQ expression contains an unsupported unary operator.")
        if isinstance(node, ast.Compare) and (len(node.ops) != 1 or len(node.comparators) != 1):
            raise ValueError("Custom DQ expression comparisons must be explicit and joined with & or |.")
    return tree


def _custom_expression_columns(expression: str) -> set[str]:
    """Return statically referenced columns after validating the custom grammar."""
    tree = _custom_expression_tree(expression)
    columns: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "F"
            and node.func.attr == "col"
        ):
            if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                raise ValueError("F.col requires exactly one literal column name.")
            columns.add(node.args[0].value)
    if not columns:
        raise ValueError("Custom DQ expression must reference at least one column with F.col().")
    return columns


def _custom_expression_column(expression: str, functions):
    """Compile the constrained AST into a native Spark boolean Column without eval()."""
    tree = _custom_expression_tree(expression)

    def build(node):
        if isinstance(node, ast.Expression):
            return build(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            left, right = build(node.left), build(node.right)
            if isinstance(node.op, ast.BitAnd):
                return left & right
            if isinstance(node.op, ast.BitOr):
                return left | right
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Mod):
                return left % right
            raise ValueError("Custom DQ expression contains an unsupported binary operator.")
        if isinstance(node, ast.UnaryOp):
            operand = build(node.operand)
            if isinstance(node.op, ast.Invert):
                return ~operand
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.UAdd):
                return +operand
            raise ValueError("Custom DQ expression contains an unsupported unary operator.")
        if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators) == 1:
            left, right, operator = build(node.left), build(node.comparators[0]), node.ops[0]
            if isinstance(operator, ast.Eq):
                return left == right
            if isinstance(operator, ast.NotEq):
                return left != right
            if isinstance(operator, ast.Gt):
                return left > right
            if isinstance(operator, ast.GtE):
                return left >= right
            if isinstance(operator, ast.Lt):
                return left < right
            return left <= right
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                value = build(node.args[0])
                return functions.col(value) if node.func.attr == "col" else functions.lit(value)
            target = build(node.func.value)
            return getattr(target, node.func.attr)(*[build(argument) for argument in node.args])
        raise ValueError("Custom DQ expression could not be compiled to a Spark Column.")

    return build(tree)

def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate canonical DQ rules before loading or enforcement."""
    if not isinstance(rules, list):
        raise ValueError("DQ rules must be a list of dictionaries.")

    optional_common = {"severity", "description", "rule_id", "is_active", "review_status"}
    del optional_common  # Documents intentionally accepted fields for callers and tests.

    def require_columns(rule: dict[str, Any], count: int | None = None, *, minimum: int | None = None) -> list[str]:
        cols = rule.get("columns")
        if isinstance(cols, str):
            cols = [c.strip() for c in cols.split(",") if c.strip()]
            rule["columns"] = cols
        if not isinstance(cols, list) or not cols or not all(str(c).strip() for c in cols):
            raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' columns must be a non-empty list.")
        cols = [str(c).strip() for c in cols]
        rule["columns"] = cols
        if count is not None and len(cols) != count:
            raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' requires exactly {count} column(s).")
        if minimum is not None and len(cols) < minimum:
            raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' requires at least {minimum} column(s).")
        return cols

    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"DQ rule at index {i} must be a dictionary.")
        rule.setdefault("rule_id", f"dq_rule_{i + 1}")
        rule.setdefault("severity", "warning")
        rule["severity"] = _normalize_dq_severity(rule.get("severity"))
        rule.setdefault("description", "")
        rule["rule_type"] = _canonical_dq_rule_type(rule.get("rule_type"))
        rtype = rule["rule_type"]
        if rtype not in DQ_RULE_TYPES:
            raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported rule_type '{rtype}'.")

        if rtype in {"completeness", "value_set", "range", "pattern"}:
            require_columns(rule, count=1)
        elif rtype == "uniqueness":
            require_columns(rule, minimum=1)
        elif rtype == "column_relationship":
            require_columns(rule, count=2)
        elif rtype in {"conditional_completeness", "conditional_values"}:
            require_columns(rule, count=2)
        elif rtype == "custom_expression":
            rule.setdefault("columns", [])

        if rtype == "completeness":
            if rule.get("maximum_missing_percent") is None:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires maximum_missing_percent.")
            if isinstance(rule["maximum_missing_percent"], bool):
                raise ValueError("maximum_missing_percent must be a percentage between 0 and 100.")
            threshold = float(rule["maximum_missing_percent"])
            if not 0 <= threshold <= 100:
                raise ValueError(f"DQ rule '{rule['rule_id']}' maximum_missing_percent must be between 0 and 100.")
            rule["maximum_missing_percent"] = threshold
            if not isinstance(rule.get("treat_blank_as_missing"), bool):
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires boolean treat_blank_as_missing.")
        if rtype == "uniqueness" and "minimum_unique_percent" in rule:
            if isinstance(rule.get("minimum_unique_percent"), bool):
                raise ValueError("minimum_unique_percent must be a percentage between 0 and 100.")
            threshold = float(rule["minimum_unique_percent"])
            if not 0 <= threshold <= 100:
                raise ValueError(
                    f"DQ rule '{rule['rule_id']}' minimum_unique_percent must be between 0 and 100."
                )
            rule["minimum_unique_percent"] = threshold
        if rtype == "value_set":
            if rule.get("mode") not in {"allow", "block"}:
                raise ValueError(f"DQ rule '{rule['rule_id']}' mode must be 'allow' or 'block'.")
            if not isinstance(rule.get("values"), list) or not rule["values"]:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires a non-empty values list.")
        if rtype == "range":
            if rule.get("minimum") is None and rule.get("maximum") is None:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires minimum or maximum.")
            rule["minimum_inclusive"] = bool(rule.get("minimum_inclusive", True))
            rule["maximum_inclusive"] = bool(rule.get("maximum_inclusive", True))
        if rtype == "pattern" and not str(rule.get("pattern") or ""):
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires pattern.")
        if rtype == "column_relationship":
            if rule["columns"][0] == rule["columns"][1]:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires two different columns.")
            if str(rule.get("operator") or "") not in DQ_COMPARISON_OPERATORS:
                raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported operator.")
        if rtype in {"conditional_completeness", "conditional_values"}:
            if rule["columns"][0] == rule["columns"][1]:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires two different columns.")
            if str(rule.get("condition_operator") or "") not in {"=", "!="}:
                raise ValueError(
                    f"DQ rule '{rule['rule_id']}' condition_operator must be '=' or '!='."
                )
            if "condition_value" not in rule:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires condition_value.")
        if rtype == "conditional_completeness":
            if not isinstance(rule.get("treat_blank_as_missing"), bool):
                raise ValueError(
                    f"DQ rule '{rule['rule_id']}' requires boolean treat_blank_as_missing."
                )
        if rtype == "conditional_values":
            if rule.get("mode") not in {"allow", "block"}:
                raise ValueError(f"DQ rule '{rule['rule_id']}' mode must be 'allow' or 'block'.")
            if not isinstance(rule.get("values"), list) or not rule["values"]:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires a non-empty values list.")
        if rtype == "custom_expression":
            if str(rule.get("expression_language") or "").lower() != "pyspark":
                raise ValueError(f"DQ rule '{rule['rule_id']}' expression_language must be 'pyspark'.")
            expression = str(rule.get("expression") or "").strip()
            if not expression:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires expression.")
            rule["columns"] = sorted(_custom_expression_columns(expression))
        tolerance = dq_tolerance_parameter(rtype, str(rule.get("mode") or ""))
        if rtype == "uniqueness" and "minimum_unique_percent" in rule and "maximum_failure_percent" not in rule:
            tolerance = "minimum_unique_percent"
        for field in {"maximum_missing_percent", "minimum_unique_percent", "maximum_failure_percent"}:
            if field in rule and field != tolerance:
                raise ValueError(f"DQ rule '{rule['rule_id']}' does not support {field}; prohibited-value rules are strict.")
        if tolerance:
            value = rule.get(tolerance, 100 if tolerance == "minimum_unique_percent" else 0)
            if isinstance(value, bool):
                raise ValueError(f"{tolerance} must be a percentage between 0 and 100.")
            value = float(value)
            if not 0 <= value <= 100:
                raise ValueError(f"{tolerance} must be a percentage between 0 and 100.")
            rule[tolerance] = value
    return rules

def _load_active_dq_rules(metadata_df, table_id: str, active_workspace_id: str | None = None, dataset_name: str | None = None) -> list[dict[str, Any]]:
    """Load active DQ guardrail rules from append-only metadata rows."""
    if isinstance(metadata_df, list):
        latest = [row for row in metadata_df
                  if str(row.get("table_id") or "") == table_id
                  and str(row.get("guardrail_type") or "").lower() == "data_quality"
                  and (active_workspace_id is None or row.get("workspace_id") == active_workspace_id)
                  and (dataset_name is None or "dataset_name" not in row or row.get("dataset_name") == dataset_name)
                  and _is_active_guardrail_rule(row)]
    else:
        _, F, Window = _spark_sql_helpers()
        columns = set(getattr(metadata_df, "columns", []))
        if "rule_key" in columns:
            partition_columns = ["rule_key"]
        elif "rule_id" in columns:
            partition_columns = ["rule_id"]
        else:
            partition_columns = [name for name in ("table_id", "column_name", "rule_type") if name in columns]
        if not partition_columns:
            raise ValueError("DQ metadata must include rule_key or rule identity columns.")
        if "table_id" not in columns:
            raise ValueError("DQ metadata must include table_id for canonical table scoping.")
        latest = metadata_df.filter(F.col("table_id") == table_id)
        if "guardrail_type" in columns:
            latest = latest.filter(F.lower(F.col("guardrail_type")) == "data_quality")
        if active_workspace_id is not None and "workspace_id" in columns:
            latest = latest.filter(F.col("workspace_id") == active_workspace_id)
        if dataset_name is not None and "dataset_name" in columns:
            latest = latest.filter(F.col("dataset_name") == dataset_name)
        order_columns = [name for name in ("_committed_at", "approved_at") if name in columns]
        if order_columns:
            window = Window.partitionBy(*[F.col(name) for name in partition_columns]).orderBy(
                *[F.col(name).desc_nulls_last() for name in order_columns]
            )
            latest = latest.withColumn("_rn", F.row_number().over(window)).filter(F.col("_rn") == 1).drop("_rn")
        if "activation_state" in columns:
            latest = latest.filter(F.lower(F.coalesce(F.col("activation_state"), F.lit(""))) == "active")
        elif "is_active" in columns:
            latest = latest.filter(F.col("is_active") == True)
        else:
            return []
        if "action_type" in columns:
            latest = latest.filter(F.lower(F.coalesce(F.col("action_type"), F.lit("created"))) != "deactivated")
        if "review_state" in columns and "review_status" in columns:
            review_expr = F.coalesce(F.col("review_state"), F.col("review_status"))
        elif "review_state" in columns:
            review_expr = F.col("review_state")
        elif "review_status" in columns:
            review_expr = F.col("review_status")
        else:
            return []
        latest = latest.filter(F.lower(F.coalesce(review_expr, F.lit(""))).isin("self_approved", "governance_approved", "active_pending_governance_review"))

    rules: list[dict[str, Any]] = []
    for row in observation_rows(latest):
        params_raw = row.get("rule_parameters_json") or "{}"
        try:
            params = json.loads(params_raw) if isinstance(params_raw, str) else dict(params_raw)
        except Exception:
            params = {}
        columns_value = params.get("columns") or row.get("columns") or row.get("column_name")
        if isinstance(columns_value, str):
            rule_columns = [c.strip() for c in columns_value.split(",") if c.strip()]
        else:
            rule_columns = list(columns_value or [])
        params = {k: v for k, v in params.items() if k != "columns"}
        rules.append(
            {
                "rule_id": str(row.get("rule_id") or ""),
                "guardrail_rule_id": str(row.get("guardrail_rule_id") or row.get("rule_id") or ""),
                "guardrail_version": int(row.get("guardrail_version") or row.get("configuration_version") or 1),
                "rule_key": str(row.get("rule_key") or row.get("rule_id") or ""),
                "rule_type": _canonical_dq_rule_type(row.get("rule_type")),
                "columns": rule_columns,
                "severity": _normalize_dq_severity(row.get("action") or row.get("severity")),
                "description": str(row.get("description") or ""),
                "review_status": str(row.get("review_status") or ""),
                **({"managed_by": "grain"} if row.get("managed_by") == "grain" else {}),
                **params,
            }
        )
    return _validate_dq_rules(rules)

def check_dq_runtime(
    dataframe,
    config,
    active_workspace_id: str,
    table_name: str,
    *,
    table_id: str,
    store: str,
    store_type: str,
    schema_name: str | None,
    dataset_name: str = "",
    run_id: str = "",
    row_identity_columns: list[str] | None = None,
    context: Mapping[str, Any] | None = None,
    rules_df: Any = None,
    contract_id: str = "",
    contract_version: int = 0,
    diagnostics: str = "sample",
) -> dict[str, Any]:
    """Evaluate native Spark DQ flags, persist rule summaries, and return details.

    Exact observed counts remain visible even within tolerance. The default
    sample mode captures at most ten illustrative source records per rule in
    the same aggregation and stores them in the rule result payload. Full
    diagnostics are an explicit lazy output; none returns no examples. No rows
    are dropped. Unrelated source columns are excluded from sampled examples.
    """
    plan = (context or {}).get("execution_plan")
    execution_mode = plan.execution_mode if plan is not None else "governed"
    if diagnostics not in {"none", "sample", "full"}:
        raise ValueError("diagnostics must be 'none', 'sample', or 'full'.")
    spark_session = getattr(dataframe, "sparkSession", None)
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        raise RuntimeError("check_dq requires a Spark DataFrame in the active Microsoft Fabric runtime.")
    source_columns = list(getattr(dataframe, "columns", []))
    identities = list(row_identity_columns or [])
    if not identities:
        identities = [name for name in ("row_uuid", "_row_uuid", "row_id") if name in source_columns][:1]
    missing_identities = [name for name in identities if name not in source_columns]
    if missing_identities:
        raise ValueError(f"row_identity_columns not found in dataframe: {', '.join(missing_identities)}")
    metadata_df = rules_df
    if metadata_df is None:
        metadata_df = load_table_guardrail_rules(
            config, active_workspace_id, spark_session=spark_session, table_id=table_id, context=context,
        )
    rules = (
        []
        if isinstance(metadata_df, list) and not metadata_df
        else _load_active_dq_rules(metadata_df, table_id, active_workspace_id=active_workspace_id, dataset_name=dataset_name or None)
    )
    evaluation = _evaluate_dq_rules(
        dataframe, table_name, rules, sample_size=10 if diagnostics != "none" else 0,
        row_identity_columns=identities,
    )
    checks = evaluation["checks"]
    result = _summarize_dq_guardrail(checks)
    result["diagnostics"] = {"mode": diagnostics, "sample_limit_per_rule": 10 if diagnostics != "none" else 0}
    result["dataframe"] = _dq_tagged_dataframe(dataframe, rules, evaluation=evaluation)
    total_count = evaluation["total_count"]
    failed_rule_count = sum(not check["passed"] for check in checks)
    failed_row_count = evaluation["failed_row_count"]
    applicable_count = evaluation["applicable_row_count"]
    result["summary"] = {
        "DQ_STATUS": result["status"],
        "DQ_RULE_COUNT": len(checks),
        "DQ_FAILED_RULE_COUNT": failed_rule_count,
        "DQ_WARNING_RULE_COUNT": sum(check["status"] == "warning" for check in checks),
        "DQ_ERROR_RULE_COUNT": sum(check["status"] == "failed" for check in checks),
        "DQ_FAILED_ROW_COUNT": failed_row_count,
        "DQ_FAILED_ROW_PERCENT": round((failed_row_count / applicable_count) * 100, 4) if applicable_count else 0.0,
        "DQ_TOTAL_ROW_COUNT": total_count,
        "DQ_CHECKED_ROW_COUNT": applicable_count,
        "DQ_NOT_APPLICABLE_ROW_COUNT": total_count - applicable_count,
        "DQ_PASSED_ROW_COUNT": applicable_count - failed_row_count,
        "DQ_PASSED_ROW_PERCENT": round(((applicable_count - failed_row_count) / applicable_count) * 100, 4) if applicable_count else 0.0,
        "DQ_VIOLATING_RULE_COUNT": sum(check["failed_count"] > 0 for check in checks),
        "DQ_CHECKED_AT": get_current_audit_timestamp(config=config, drop_microseconds=False),
    }
    if not rules:
        result["failed_values"] = _dq_empty_failed_values(spark_session)
        return result

    audit = build_pipeline_audit_fields(config=config, active_workspace_id=active_workspace_id,
                                       runtime_context=plan.runtime_context if plan is not None else context)
    resolved_run_id = str(run_id or "").strip() or str(audit["_activity_id"]).strip()
    if plan is not None:
        resolved_run_id = plan.plan_id
    result["run_id"] = resolved_run_id
    summary_rows = []
    for rule, check in zip(rules, checks, strict=True):
        summary_rows.append({
            "guardrail_result_id": str(uuid4()),
            "guardrail_rule_id": rule["guardrail_rule_id"],
            "guardrail_version": rule["guardrail_version"],
            "table_id": None if str(table_id).startswith("file:") else table_id,
            "source_id": table_id if str(table_id).startswith("file:") else None,
            "contract_id": str(contract_id or ""),
            "contract_version": int(contract_version or 0),
            "execution_type": execution_mode,
            "result_id": str(uuid4()),
            "run_id": resolved_run_id,
            "rule_key": rule["rule_key"],
            "workspace_id": active_workspace_id,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "column_name": ",".join(rule["columns"]),
            "guardrail_type": "data_quality",
            "rule_type": rule["rule_type"],
            "status": check["status"],
            "can_continue": check["status"] != "failed",
            "severity": rule["severity"],
            "reason": f"{check['failed_count']} observed violation(s) in {check['applicable_count']} applicable row(s); "
                      + ("within tolerance." if check["passed"] else "tolerance exceeded."),
            "expected_value_json": json.dumps({key: value for key, value in rule.items() if key not in {"description", "guardrail_rule_id", "rule_id", "rule_key", "severity"}}, default=str, sort_keys=True),
            "actual_value_json": json.dumps({"failed_count": check["failed_count"], "failed_percent": check["failed_percent"], "total_count": check["total_count"]}, sort_keys=True),
            "result_payload_json": json.dumps(check, default=str, sort_keys=True),
            **audit,
        })
    plan = (context or {}).get("execution_plan")
    if plan is not None:
        plan.results.extend(summary_rows)
        if not plan.permits_persistence:
            plan.evidence.setdefault("guardrail_history", []).extend(dict(row) for row in summary_rows)
    if persistence_permitted(context):
        write_lakehouse_table(
            spark_session.createDataFrame([coerce_metadata_row_types("METADATA_GUARDRAIL_RESULTS", row) for row in summary_rows],
                schema=metadata_table_schema_registry()["METADATA_GUARDRAIL_RESULTS"]),
            "METADATA_GUARDRAIL_RESULTS", store="Metadata",
            schema=metadata_table_physical_schema(config, "METADATA_GUARDRAIL_RESULTS"),
            context=context or {"config": config, "scope_workspace_id": active_workspace_id}, mode="append",
        )

    if diagnostics == "full":
        result["failed_values"] = _dq_failed_values_dataframe(
            dataframe, rules, run_id=resolved_run_id, row_identity_columns=identities, evaluation=evaluation,
        )
    elif diagnostics == "sample":
        result["failed_values"] = _dq_sample_failed_values(dataframe, rules, checks, run_id=resolved_run_id)
    else:
        result["failed_values"] = _dq_empty_failed_values(spark_session)
    return result


def _dq_failed_value_schema():
    """Return the stable normalized schema for caller-owned DQ failure details."""
    from pyspark.sql.types import StringType, StructField, StructType

    nullable = {"raw_value"}
    return StructType([
        StructField(name, StringType(), name in nullable)
        for name in (
            "failure_event_id", "run_id", "row_identity", "guardrail_rule_id",
            "rule_id", "rule_type", "action", "column_name", "column_role",
            "raw_value", "raw_value_type", "failure_reason",
        )
    ])


def _dq_empty_failed_values(spark_session):
    """Build canonical empty details without starting a Python Spark worker."""
    _, F, _ = _spark_sql_helpers()
    return spark_session.range(0).select(*[
        F.lit(None if field.nullable else "").cast(field.dataType).alias(field.name)
        for field in _dq_failed_value_schema()
    ])


def _dq_sample_failed_values(dataframe, rules, checks, *, run_id):
    """Return bounded captured examples without evaluating the source again."""
    _, F, _ = _spark_sql_helpers()
    types = dict(dataframe.dtypes)
    rows = []
    for rule, check in zip(rules, checks, strict=True):
        for example in check["failure_examples"]:
            values = {item["column_name"]: item["raw_value"] for item in example["values"]}
            event_id = hashlib.sha256(f"{run_id}|{rule['guardrail_rule_id']}|{example['source_record_id']}".encode()).hexdigest()
            for index, name in enumerate(rule["columns"]):
                role = ("left" if index == 0 else "right") if rule["rule_type"] == "column_relationship" else (
                    "participating" if rule["rule_type"] == "uniqueness" and len(rule["columns"]) > 1 else "target"
                )
                rows.append((event_id, run_id, example["row_identity"], rule["guardrail_rule_id"],
                             rule["rule_id"], rule["rule_type"], "Block" if rule["severity"] == "error" else "Warn",
                             name, role, values[name], types[name], f"Row violated {rule['rule_type']} rule {rule['rule_id']}."))
    empty = _dq_empty_failed_values(dataframe.sparkSession)
    if not rows:
        return empty
    schema = _dq_failed_value_schema()
    records = [F.struct(*[F.lit(value).cast(field.dataType).alias(field.name)
                         for field, value in zip(schema, row, strict=True)]) for row in rows]
    # One tiny native relation; union only relaxes raw_value nullability to the stable schema.
    return dataframe.sparkSession.range(1).select(F.explode(F.array(*records)).alias("record")).select("record.*").unionByName(empty)


def _dq_failed_values_dataframe(dataframe, rules, *, run_id: str, row_identity_columns: list[str], evaluation=None):
    """Expand shared failure flags into details using native Spark expressions."""
    _, F, _ = _spark_sql_helpers()
    evaluation = evaluation if evaluation is not None else _evaluate_dq_rules(dataframe, "", rules)
    source_columns = list(dataframe.columns)
    source_types = dict(dataframe.dtypes)
    if row_identity_columns:
        row_identity = F.to_json(
            F.struct(*[F.col(name).alias(name) for name in row_identity_columns]),
            {"ignoreNullFields": "false"},
        )
    else:
        canonical_row = F.to_json(
            F.struct(*[F.col(name).alias(name) for name in sorted(source_columns)]),
            {"ignoreNullFields": "false"},
        )
        row_identity = F.sha2(canonical_row, 256)
    source = evaluation["frame"]
    source_id = F.monotonically_increasing_id()
    events = []
    for rule, flag in zip(rules, evaluation["flags"], strict=True):
        if flag is None:
            continue
        columns = [str(name) for name in rule.get("columns") or ()]
        rule_type = str(rule.get("rule_type") or "")
        if rule_type == "column_relationship":
            column_roles = [(columns[0], "left"), (columns[1], "right")]
        else:
            role = "participating" if rule_type == "uniqueness" and len(columns) > 1 else "target"
            column_roles = [(name, role) for name in columns]
            condition = str(rule.get("condition_column") or "").strip()
            if condition and condition not in columns:
                column_roles.append((condition, "condition"))
        details = F.array(*[
            F.struct(
                F.lit(column_name).alias("column_name"),
                F.lit(column_role).alias("column_role"),
                (
                    F.when(F.col(flag), F.col(column_name).cast("string"))
                    if column_name in source_types
                    else F.lit(None).cast("string")
                ).alias("raw_value"),
                F.lit(source_types.get(column_name, "missing")).alias("raw_value_type"),
            )
            for column_name, column_role in column_roles
        ])
        event_id = F.sha2(F.concat_ws(
            "|", F.lit(run_id), F.lit(rule["guardrail_rule_id"]),
            source_id.cast("string"),
        ), 256)
        reason = f"Row failed {rule['rule_type']} rule {rule['rule_id']}."
        action = "Block" if rule["severity"] == "error" else "Warn"
        events.append(F.struct(
            F.col(flag).alias("failed"),
            F.coalesce(event_id, F.lit("")).alias("failure_event_id"),
            F.lit(run_id).alias("run_id"),
            F.coalesce(row_identity, F.lit("")).alias("row_identity"),
            F.lit(rule["guardrail_rule_id"]).alias("guardrail_rule_id"),
            F.lit(rule["rule_id"]).alias("rule_id"),
            F.lit(rule["rule_type"]).alias("rule_type"), F.lit(action).alias("action"),
            details.alias("details"), F.lit(reason).alias("failure_reason"),
        ))
    if not events:
        return _dq_empty_failed_values(dataframe.sparkSession)
    # Filter the array before exploding so passing rows/rules emit no detail rows.
    return (
        source.select(F.explode(F.filter(F.array(*events), lambda event: event["failed"])).alias("event"))
        .select("event.*")
        .select("*", F.explode("details").alias("detail"))
        .select(
            "failure_event_id", "run_id", "row_identity", "guardrail_rule_id",
            "rule_id", "rule_type", "action", "detail.column_name",
            "detail.column_role", "detail.raw_value", "detail.raw_value_type", "failure_reason",
        )
    ).to(_dq_failed_value_schema())

def _dq_failed_expression(df, rule: dict[str, Any]):
    """Build a raw row predicate without Spark actions or percentage gating."""
    _, F, Window = _spark_sql_helpers()
    rule = _validate_dq_rules([dict(rule)])[0]
    rtype = str(rule["rule_type"])
    cols = [str(column) for column in rule.get("columns", [])]
    dataframe_columns = set(getattr(df, "columns", []))
    missing_columns = [column for column in cols if column not in dataframe_columns]
    if missing_columns:
        raise ValueError(f"DQ rule '{rule['rule_id']}' references missing column(s): {', '.join(missing_columns)}.")
    col_name = cols[0] if cols else None

    def empty_string(column: str):
        return F.col(column).isNull() | (F.trim(F.col(column).cast("string")) == "")

    def compare(left, operator: str, right):
        if operator == "=":
            return left.eqNullSafe(right)
        if operator == "!=":
            return ~left.eqNullSafe(right)
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
        if operator == "<":
            return left < right
        return left <= right

    if rtype == "completeness":
        failed = empty_string(col_name) if rule["treat_blank_as_missing"] else F.col(col_name).isNull()
    elif rtype == "uniqueness":
        failed = F.count(F.lit(1)).over(
            Window.partitionBy(*[F.col("`" + c.replace("`", "``") + "`") for c in sorted(set(cols))])
        ) > F.lit(1)
        if rule.get("require_non_null"):
            for column in cols:
                failed = failed | F.col("`" + column.replace("`", "``") + "`").isNull()
    elif rtype == "value_set":
        contained = F.col(col_name).isin(list(rule["values"]))
        failed = F.col(col_name).isNotNull() & (contained if rule["mode"] == "block" else ~contained)
    elif rtype == "range":
        value_col = F.col(col_name)
        cond = F.lit(False)
        if rule.get("minimum") is not None:
            minimum = F.lit(rule["minimum"])
            cond = cond | (value_col < minimum if rule["minimum_inclusive"] else value_col <= minimum)
        if rule.get("maximum") is not None:
            maximum = F.lit(rule["maximum"])
            cond = cond | (value_col > maximum if rule["maximum_inclusive"] else value_col >= maximum)
        failed = F.col(col_name).isNotNull() & cond
    elif rtype == "pattern":
        failed = F.col(col_name).isNotNull() & ~F.col(col_name).cast("string").rlike(rule["pattern"])
    elif rtype == "column_relationship":
        left = F.col(cols[0])
        right = F.col(cols[1])
        failed = ~compare(left, rule["operator"], right)
        if rule["operator"] in {">", ">=", "<", "<="}:
            one_null = left.isNull() != right.isNull()
            failed = one_null | (left.isNotNull() & right.isNotNull() & failed)
    elif rtype in {"conditional_completeness", "conditional_values"}:
        condition_column = F.col(cols[0])
        condition_value = F.lit(rule["condition_value"])
        condition = compare(condition_column, rule["condition_operator"], condition_value)
        target_column = F.col(cols[1])
        if rtype == "conditional_completeness":
            target_failed = (
                empty_string(cols[1])
                if rule["treat_blank_as_missing"]
                else target_column.isNull()
            )
        else:
            contained = target_column.isin(list(rule["values"]))
            target_failed = target_column.isNotNull() & (
                contained if rule["mode"] == "block" else ~contained
            )
        failed = condition & target_failed
    elif rtype == "custom_expression":
        try:
            passed = _custom_expression_column(rule["expression"], F)
            resolved = df.select(passed.alias("_fabricops_custom_dq_predicate")).schema[0]
            if resolved.dataType.simpleString() != "boolean":
                raise ValueError(
                    "Custom DQ expression must resolve to a boolean Spark Column; "
                    f"received {resolved.dataType.simpleString()}."
                )
            failed = ~passed
        except Exception as exc:  # noqa: BLE001 - normalize Spark analysis failures as rule errors
            raise ValueError(f"Custom DQ rule '{rule['rule_id']}' could not be evaluated: {exc}") from exc
    else:
        raise ValueError(f"Unsupported rule_type: {rtype}")
    return F.coalesce(failed, F.lit(False))

def _dq_applicable_expression(rule):
    """Define the denominator without counting unrelated or ignored rows as passes."""
    _, F, _ = _spark_sql_helpers()
    kind, columns = rule["rule_type"], rule["columns"]
    if kind in {"value_set", "range", "pattern"}:
        return F.col(columns[0]).isNotNull()
    if kind == "custom_expression":
        return _custom_expression_column(rule["expression"], F).isNotNull()
    if kind in {"conditional_completeness", "conditional_values"}:
        condition = F.col(columns[0]).eqNullSafe(F.lit(rule["condition_value"]))
        if rule["condition_operator"] == "!=":
            condition = ~condition
        if kind == "conditional_values":
            condition = condition & F.col(columns[1]).isNotNull()
        return condition
    return F.lit(True)


def _dq_sample_record(rule, source_id, identities):
    """Build a narrow diagnostic record; unrelated business columns are excluded."""
    _, F, _ = _spark_sql_helpers()
    identity = (
        F.to_json(F.struct(*[F.col(name).alias(name) for name in identities]), {"ignoreNullFields": "false"})
        if identities else F.concat(F.lit("source_record:"), source_id.cast("string"))
    )
    return F.struct(
        source_id.cast("string").alias("source_record_id"), identity.alias("row_identity"),
        F.array(*[F.struct(
            F.lit(name).alias("column_name"), F.col(name).cast("string").alias("raw_value"),
        ) for name in sorted(set(rule["columns"]))]).alias("values"),
    )


def _evaluate_dq_rules(df, table_name: str, rules: list[dict[str, Any]], *, sample_size: int = 0,
                       row_identity_columns: list[str] | None = None) -> dict[str, Any]:
    """Aggregate exact observed outcomes and bounded examples in one Spark action.

    Percent tolerances affect the rule decision, never observed counts. Each
    sample slot retains one minimum hashed candidate per distinct predicate;
    no unbounded collection, failure sort, or second data scan is needed.
    Examples are illustrative and can contain fewer than sample_size records.
    """
    _, F, Window = _spark_sql_helpers()
    _validate_dq_rules(rules)
    if not rules:
        return {"frame": df, "flags": [], "checks": [], "total_count": int(df.count()),
                "failed_row_count": 0, "applicable_row_count": 0}
    prefix = "_fabricops_dq_"
    while any(name.startswith(prefix) for name in df.columns):
        prefix += "_"
    expressions, rule_flags, shared_flags, distinct_flags, applicable_flags = [], [], {}, {}, {}
    reporting_fields = {
        "rule_id", "guardrail_rule_id", "guardrail_version", "rule_key", "severity", "business_requirement",
        "description", "is_active", "review_status", "maximum_missing_percent", "minimum_unique_percent",
        "maximum_failure_percent",
    }
    representative_rules = {}
    for rule in rules:
        parameters = {key: value for key, value in rule.items() if key not in reporting_fields}
        if rule["rule_type"] == "uniqueness":
            parameters["columns"] = sorted(set(rule["columns"]))
        signature = json.dumps(parameters, default=lambda value: {
            "python_type": f"{type(value).__module__}.{type(value).__qualname__}", "value": str(value),
        }, sort_keys=True)
        if signature not in shared_flags:
            name = f"{prefix}failed_{len(shared_flags)}"
            shared_flags[signature] = name
            representative_rules[name] = rule
            applicable_flags[name] = f"{name}_applicable"
            expressions.extend([
                _dq_failed_expression(df, rule).alias(name),
                _dq_applicable_expression(rule).alias(applicable_flags[name]),
            ])
        rule_flags.append(shared_flags[signature])
        if rule["rule_type"] == "uniqueness" and "minimum_unique_percent" in rule:
            keys = tuple(sorted(set(rule["columns"])))
            if keys not in distinct_flags:
                name = f"{prefix}distinct_{len(distinct_flags)}"
                distinct_flags[keys] = name
                window = Window.partitionBy(*[F.col(key) for key in keys]).orderBy(F.lit(1))
                expressions.append((F.row_number().over(window) == 1).alias(name))
    evaluated = df.select("*", *expressions)
    source_name = f"{prefix}source_id"
    if sample_size:
        evaluated = evaluated.withColumn(source_name, F.monotonically_increasing_id())
    flags = list(shared_flags.values())
    any_failure = reduce(lambda left, right: left | right, [F.col(name) for name in flags], F.lit(False))
    any_applicable = reduce(lambda left, right: left | right,
                            [F.col(name) for name in applicable_flags.values()], F.lit(False))

    def count_true(predicate):
        return F.sum(F.when(predicate, 1).otherwise(0))

    samples = []
    for flag, rule in representative_rules.items():
        if not sample_size:
            break
        source_id = F.col(source_name)
        record = _dq_sample_record(rule, source_id, list(row_identity_columns or []))
        for slot in range(sample_size):
            samples.append(F.min(F.when(F.col(flag), F.struct(
                F.xxhash64(source_id, F.lit(slot)).alias("rank"), record.alias("record"),
            ))).alias(f"{flag}_sample_{slot}"))
    counts = evaluated.agg(
        F.count(F.lit(1)).alias("__total"),
        *[count_true(F.col(name)).alias(name) for name in [*flags, *applicable_flags.values(), *distinct_flags.values()]],
        count_true(any_failure).alias("__any_failed"), count_true(any_applicable).alias("__any_applicable"), *samples,
    ).first()
    checks = _dq_checks_from_counts(table_name, rules, rule_flags, distinct_flags, applicable_flags, counts)
    for check, flag in zip(checks, rule_flags, strict=True):
        examples = {}
        for slot in range(sample_size):
            candidate = counts[f"{flag}_sample_{slot}"]
            if candidate is not None:
                record = candidate["record"].asDict(recursive=True)
                examples[record["source_record_id"]] = record
        check["failure_examples"] = list(examples.values())
    return {
        "frame": evaluated, "flags": rule_flags, "checks": checks,
        "total_count": int(counts["__total"]), "failed_row_count": int(counts["__any_failed"] or 0),
        "applicable_row_count": int(counts["__any_applicable"] or 0),
    }


def _dq_checks_from_counts(table_name, rules, rule_flags, distinct_flags, applicable_flags, counts):
    """Keep exact observed metrics separate from the authored continuation decision."""
    total = int(counts["__total"])
    checks = []
    for rule, flag in zip(rules, rule_flags, strict=True):
        failed = int(counts[flag] or 0)
        applicable = int(counts[applicable_flags[flag]] or 0)
        failed_percent = (failed / applicable) * 100 if applicable else 0.0
        parameter = dq_tolerance_parameter(rule["rule_type"], str(rule.get("mode") or ""))
        threshold = float(rule.get(parameter, 0)) if parameter else 0.0
        if rule["rule_type"] == "uniqueness" and "minimum_unique_percent" in rule:
            threshold = float(rule["minimum_unique_percent"])
            parameter = "minimum_unique_percent"
            keys = tuple(sorted(set(rule["columns"])))
            distinct = int(counts[distinct_flags[keys]] or 0)
            observed = (distinct / total) * 100 if total else 100.0
            exceeded = observed < threshold
            metric, operator = "distinct_key_percent", ">="
        else:
            observed = failed_percent
            exceeded = observed > threshold
            metric, operator = "missing_percent" if parameter == "maximum_missing_percent" else "failure_percent", "<="
        severity = _normalize_dq_severity(rule.get("severity"))
        checks.append({
            **({"managed_by": "grain", "label": "GRAIN — Uniqueness"} if rule.get("managed_by") == "grain" else {}),
            "check": "dq_rule", "table_name": table_name, "rule_id": str(rule.get("rule_id") or ""),
            "rule_type": rule["rule_type"], "columns": list(rule["columns"]), "severity": severity,
            "status": ("failed" if severity == "error" else "warning") if exceeded else "passed",
            "passed": not exceeded, "tolerance_exceeded": exceeded,
            "failed_count": failed, "total_count": total, "applicable_count": applicable,
            "not_applicable_count": total - applicable, "passed_count": applicable - failed,
            "failed_percent": round(failed_percent, 4),
            "passed_percent": round(((applicable - failed) / applicable) * 100, 4) if applicable else 0.0,
            "observed_metric": metric, "observed_value": round(observed, 4),
            "threshold_parameter": parameter, "threshold_value": threshold, "threshold_operator": operator,
            "description": str(rule.get("description") or ""),
        })
    return checks


def _dq_tagged_dataframe(df, rules: list[dict[str, Any]], *, evaluation=None):
    """Return the full DataFrame tagged with failed DQ rule IDs and row status."""
    _, F, _ = _spark_sql_helpers()
    evaluation = evaluation if evaluation is not None else _evaluate_dq_rules(df, "", rules)
    evaluated = evaluation["frame"]
    sorted_rules = sorted(zip(rules, evaluation["flags"], evaluation["checks"], strict=True), key=lambda pair: str(pair[0].get("rule_id") or ""))
    failed_rule_columns = [
        F.when(F.col(flag), F.lit(str(rule.get("rule_id") or "")))
        for rule, flag, check in sorted_rules if flag is not None
    ]
    failed_rules = F.concat_ws(",", *failed_rule_columns) if failed_rule_columns else F.lit("")
    error_failures = [
        F.when(F.col(flag), F.lit(1)).otherwise(F.lit(0))
        for rule, flag, check in sorted_rules
        if flag is not None and check["status"] == "failed"
    ]
    warning_failures = [
        F.when(F.col(flag), F.lit(1)).otherwise(F.lit(0))
        for rule, flag, check in sorted_rules
        if flag is not None and check["status"] != "failed"
    ]
    error_count = error_failures[0] if error_failures else F.lit(0)
    for failure in error_failures[1:]:
        error_count = error_count + failure
    warning_count = warning_failures[0] if warning_failures else F.lit(0)
    for failure in warning_failures[1:]:
        warning_count = warning_count + failure
    return (
        evaluated.withColumn("_dq_failed_rules", failed_rules)
        .withColumn(
            "_dq_check_status",
            F.when(error_count > F.lit(0), F.lit("failed"))
            .when(warning_count > F.lit(0), F.lit("warning"))
            .otherwise(F.lit("passed")),
        ).select(*[
            F.col("`" + name.replace("`", "``") + "`")
            for name in dict.fromkeys([*df.columns, "_dq_failed_rules", "_dq_check_status"])
        ])
    )


def _summarize_dq_guardrail(checks: list[dict[str, Any]]) -> dict[str, Any]:
    if any(check.get("status") == "failed" for check in checks):
        status = "failed"
        can_continue = False
    elif any(check.get("status") == "warning" for check in checks):
        status = "warning"
        can_continue = True
    else:
        status = "passed"
        can_continue = True
    failed_checks = [check for check in checks if check.get("status") in {"warning", "failed"}]
    if not checks:
        message = "No active guardrail DQ rules found."
    elif failed_checks:
        message = f"DQ guardrail found {len(failed_checks)} rule failure(s): {status}."
    else:
        message = f"DQ guardrail passed {len(checks)} active guardrail rule(s)."
    return {"status": status, "can_continue": can_continue, "checks": checks, "message": message}

# ---------------------------------------------------------------------------
# Canonical Guardrail rule/runtime adapters
# ---------------------------------------------------------------------------

def _parse_parameters(row: Mapping[str, Any]) -> dict[str, Any]:
    raw = row.get("rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except (TypeError, json.JSONDecodeError):
        return {}

def _select_rule(
    rules_df: Any,
    *,
    guardrail_type: str,
    table_id: str,
    workspace_id: str = "",
) -> dict[str, Any] | None:
    if rules_df is None:
        return None
    rows = (
        rules_df.collect()
        if hasattr(rules_df, "collect")
        else ([rules_df] if isinstance(rules_df, dict) else rules_df)
    )
    candidates: list[dict[str, Any]] = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if str(row.get("guardrail_type") or "").lower() != guardrail_type.lower():
            continue
        if (row.get("source_id") or str(row.get("table_id") or "")) != table_id:
            continue
        rule_workspace_id = str(row.get("workspace_id") or "")
        if workspace_id and rule_workspace_id != workspace_id:
            continue
        if row.get("is_active") is not True:
            continue
        candidates.append(row)
    if not candidates:
        return None
    candidates.sort(
        key=lambda row: (
            int(row.get("guardrail_version") or 0),
            metadata_timestamp_sort_key(row.get("_committed_at")),
        ),
        reverse=True,
    )
    return candidates[0]

def schema_check_core(
    dataframe: Any,
    expected_schema: dict[str, str] | None = None,
    *,
    preset: str = "strict",
    rules_df: Any = None,
    dataset_name: str = "",
    table_name: str = "",
    workspace_id: str = "",
    table_id: str = "",
) -> dict[str, Any]:
    """Evaluate schema intent using the canonical Guardrail rule contract."""
    del dataset_name, table_name
    if rules_df is None:
        return _guardrail_schema_check_base(dataframe, expected_schema, preset=preset)
    rule = _select_rule(
        rules_df,
        guardrail_type="schema",
        table_id=table_id,
        workspace_id=workspace_id,
    )
    if rule is None:
        return _guardrail_schema_check_base(dataframe, {}, preset="monitor_only")
    params = _parse_parameters(rule)
    expected = params.get("data_types") or {}
    selected_columns = params.get("columns") or list(expected)
    expected_schema = {
        str(column): str(expected.get(column, "")) for column in selected_columns
    }
    rule_type = str(rule.get("rule_type") or "relaxed").lower()
    if "required_columns" in params:
        required_columns = set(params["required_columns"])
        actual_columns, _ = _actual_schema(dataframe)
        # Presence applies only to Required selections; every present contracted
        # column still uses its frozen datatype, regardless of that selection.
        expected_schema = {
            column: datatype for column, datatype in expected_schema.items()
            if column in required_columns or column in actual_columns
        }
    resolved_preset = "strict"
    result = _guardrail_schema_check_base(dataframe, expected_schema, preset=resolved_preset)
    result.update(
        guardrail_type="schema",
        guardrail_rule_id=str(rule.get("guardrail_rule_id") or ""),
        guardrail_version=int(rule.get("guardrail_version") or 1),
        rule_id=str(rule.get("rule_id") or ""),
        rule_type=rule_type,
        severity="blocking",
        action="Block",
    )
    return result


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(value: str | None, label: str) -> str:
    text = str(value or "").strip()
    if not _IDENTIFIER.fullmatch(text):
        raise ValueError(f"{label} must be a simple identifier containing letters, numbers, and underscores.")
    return text


def _warehouse_observation_query(schema: str, table_name: str, partition_column: str, change_column: str, *, watermark_only: bool = False) -> str:
    if watermark_only:
        return (
            f"SELECT MAX([{change_column}]) AS partition_value, COUNT_BIG(*) AS row_count, "
            f"MIN([{change_column}]) AS min_change_value, MAX([{change_column}]) AS max_change_value, "
            f"CAST('' AS varchar(64)) AS content_fingerprint FROM [{schema}].[{table_name}]"
        )
    return (
        "SELECT\n"
        f"  [{partition_column}] AS partition_value,\n"
        "  COUNT_BIG(*) AS row_count,\n"
        f"  MIN([{change_column}]) AS min_change_value,\n"
        f"  MAX([{change_column}]) AS max_change_value,\n"
        "  CONVERT(varchar(64), HASHBYTES('SHA2_256', "
        "STRING_AGG(CONVERT(varchar(max), row_fingerprint), '') "
        "WITHIN GROUP (ORDER BY row_fingerprint)), 2) AS content_fingerprint\n"
        "FROM (\n"
        "  SELECT source_row.*, CONVERT(varchar(64), HASHBYTES('SHA2_256', "
        "(SELECT source_row.* FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)), 2) AS row_fingerprint\n"
        f"  FROM [{schema}].[{table_name}] AS source_row\n"
        ") AS fingerprinted\n"
        f"GROUP BY [{partition_column}]"
    )


def _compact_rows(frame: Any, *, timestamp_columns: set[str] | None = None) -> list[dict[str, Any]]:
    timestamp_columns = timestamp_columns or set()
    schema = {field.name: type(field.dataType).__name__ for field in getattr(getattr(frame, "schema", None), "fields", ())}
    source_types = {field.name: field.dataType.simpleString() for field in getattr(getattr(frame, "schema", None), "fields", ())}
    timestamp_columns = timestamp_columns | {name for name, kind in schema.items() if kind == "TimestampType"}
    ntz_columns = {name for name, kind in schema.items() if kind == "TimestampNTZType"}
    compact = []
    for row in frame.collect():
        value = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        minimum = value.get("min_change_value")
        maximum = value.get("max_change_value")
        compact.append(
            {
                "partition_value": _compact_value(
                    value.get("partition_value"), timestamp="partition_value" in timestamp_columns,
                    timestamp_ntz="partition_value" in ntz_columns,
                ),
                "watermark_type": ("timestamp" if "max_change_value" in timestamp_columns else "timestamp_ntz" if "max_change_value" in ntz_columns else source_types.get("max_change_value", "string")),
                "is_present": int(value.get("row_count") or 0) > 0,
                "row_count": int(value.get("row_count") or 0),
                "min_change_value": _compact_value(minimum, timestamp="min_change_value" in timestamp_columns, timestamp_ntz="min_change_value" in ntz_columns),
                "max_change_value": _compact_value(maximum, timestamp="max_change_value" in timestamp_columns, timestamp_ntz="max_change_value" in ntz_columns),
                "content_fingerprint": str(value.get("content_fingerprint") or ""),
            }
        )
    return compact


def _observe_lakehouse(
    table_name: str,
    store: str,
    schema: str | None,
    partition_column: str,
    change_column: str,
    *,
    spark_session: Any,
    context: dict[str, Any],
    watermark_only: bool = False,
) -> list[dict[str, Any]]:
    from pyspark.sql import functions as F

    frame = read_lakehouse_table(
        table_name,
        store=store,
        schema=schema,
        context={**(context or {}), "_spark_session": spark_session},
    )
    return _observe_dataframe(frame, partition_column, change_column, watermark_only=watermark_only)


def _observe_dataframe(
    frame: Any, partition_column: str, change_column: str, *, watermark_only: bool = False
) -> list[dict[str, Any]]:
    """Aggregate an already-read source DataFrame into observation rows."""
    from pyspark.sql import functions as F

    if watermark_only:
        observed = frame.agg(
            F.max(F.col(change_column)).alias("partition_value"),
            F.count(F.lit(1)).alias("row_count"),
            F.min(F.col(change_column)).alias("min_change_value"),
            F.max(F.col(change_column)).alias("max_change_value"),
        ).select(
            "partition_value", "row_count",
            "min_change_value", "max_change_value", F.lit("").alias("content_fingerprint"),
        )
    else:
        observed = _observe_partition_dataframe(frame, partition_column, change_column)
    schema = {field.name: type(field.dataType).__name__ for field in frame.schema.fields}
    timestamp_columns = {"min_change_value", "max_change_value"} if schema.get(change_column) == "TimestampType" else set()
    if schema.get(partition_column) == "TimestampType":
        timestamp_columns.add("partition_value")
    return _compact_rows(observed, timestamp_columns=timestamp_columns)


def _observe_partition_dataframe(frame: Any, partition_column: str, change_column: str) -> Any:
    """Keep Source Drift fingerprints separate from incremental progress aggregates."""
    from pyspark.sql import functions as F

    row_columns = sorted(frame.columns)
    with_fingerprint = frame.withColumn(
        "_fabricops_content_hash",
        F.sha2(F.to_json(F.struct(*[F.col(name) for name in row_columns])), 256),
    )
    return (
        with_fingerprint.groupBy(partition_column)
        .agg(
            F.count(F.lit(1)).alias("row_count"),
            F.min(F.col(change_column)).alias("min_change_value"),
            F.max(F.col(change_column)).alias("max_change_value"),
            F.sha2(
                F.concat_ws("", F.sort_array(F.collect_list("_fabricops_content_hash"))),
                256,
            ).alias("content_fingerprint"),
        )
        .select(
            F.col(partition_column).alias("partition_value"),
            "row_count",
            "min_change_value",
            "max_change_value",
            "content_fingerprint",
        )
    )


def _validated_observation_identity(
    config: Any, active_workspace_id: str, table_id: str, identity: Mapping[str, Any]
) -> dict[str, Any]:
    """Revalidate a cached physical identity against the active workspace_id."""
    resolved = resolve_physical_table_identity(
        config,
        active_workspace_id,
        store=str(identity["store"]),
        schema=identity.get("schema"),
        table_name=str(identity["table_name"]),
    )
    if str(resolved["table_id"]) != str(table_id):
        raise ValueError(
            f"Physical identity for {table_id!r} does not match workspace_id {active_workspace_id!r}."
        )
    return resolved


def capture_source_observation(
    *,
    table_id: str,
    dataframe: Any = None,
    incremental_columns: tuple[str, str] | None = None,
    source_identity: Mapping[str, Any] | None = None,
    context=None,
    spark_session=None,
) -> Any:
    """Capture independently configured current-run source Guardrail evidence."""
    config, active_workspace_id, context = resolve_fabric_context() if context is None else (context["config"], context["scope_workspace_id"], context)
    spark = get_spark_session(spark_session, dataframe=dataframe, context=context)
    # An explicit physical source identity does not require Catalogue activation.
    # Revalidate it against this workspace_id rather than trusting global cache state.
    governed_source = (
        _validated_observation_identity(config, active_workspace_id, table_id, source_identity)
        if source_identity is not None
        else None
    )
    if governed_source is None:
        governed_source = resolve_catalogue_table_identity(
            config,
            active_workspace_id,
            table_id,
            spark_session=spark,
            context=context,
        )
    governed_table_id = str(governed_source["table_id"])
    store_key = str(governed_source["store"])
    table_value = _identifier(governed_source["table_name"], "table_name")
    schema = governed_source.get("schema")
    schema_value = _identifier(schema, "schema") if schema is not None else None
    source_type = str(
        governed_source.get("store_type") or governed_source.get("store_kind") or ""
    ).lower()
    if source_type not in {"lakehouse", "warehouse"}:
        raise ValueError(f"Store {store_key!r} must resolve to a Lakehouse or Warehouse.")
    configured_store = get_store(config, active_workspace_id, store_key)
    warehouse_history_path = None
    if source_type == "warehouse":
        configured_schema = schema_value if schema_value is not None else getattr(configured_store, "schema", None)
        if configured_schema is None or not str(configured_schema).strip():
            raise ValueError("schema is required for Warehouse observation; pass it or configure a default schema.")
        schema_value, table_value, _object_name = resolve_warehouse_table_location(
            configured_store, configured_schema, table_value, warehouse_name=configured_store.key
        )
        # Fabric Warehouse publishes read-only Delta logs for tables in OneLake.
        # Metadata may lag the SQL commit; failed access stays unavailable.
        warehouse_history_path = (
            f"abfss://{configured_store.workspace_id}@onelake.dfs.fabric.microsoft.com/"
            f"{configured_store.item_id}/Tables/{schema_value}/{table_value}"
        )
    else:
        table_value, schema_value, _path = resolve_lakehouse_table_location(configured_store, table_value, schema_value)
        if getattr(configured_store, "schema_enabled", False) and schema_value is None:
            raise ValueError(
                "schema is required for schema-enabled Lakehouse observation; pass it or configure a default schema."
            )

    rules_df = load_table_guardrail_rules(
        config,
        active_workspace_id,
        spark_session=spark,
        table_id=governed_table_id,
        context=context,
    )
    freshness_rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="freshness",
        table_id=governed_table_id,
        workspace_id=active_workspace_id,
    )
    audit = build_pipeline_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=context)

    if (
        freshness_rule is not None
        and str(_catalogue_value(freshness_rule, "rule_type") or "").strip().lower() != "skip"
    ):
        parameters = validate_freshness_parameters(_parse_rule_parameters(freshness_rule))
        # Batch scope is evaluated after the incremental filter by check_freshness.
        if parameters["evaluation_scope"] == "full_dataset":
            evidence = collect_freshness_evidence(parameters,
                source={"source_type": "table", "table_id": governed_table_id, "store_type": source_type,
                        "resolved_path": _path if source_type == "lakehouse" else warehouse_history_path}, spark_session=spark)
            _CURRENT_FRESHNESS_EVIDENCE[
                (active_workspace_id, source_observation_run_id(context) or str(audit["_activity_id"]), governed_table_id)
            ] = {**evidence, "_activity_id": str(audit["_activity_id"])}

    def capture_columns(partition_column: str, change_column: str, *, watermark_only: bool = False) -> Any:
        observation_columns = {partition_column, change_column}
        if dataframe is not None and observation_columns <= set(
            getattr(dataframe, "columns", ())
        ):
            current = _observe_dataframe(dataframe, partition_column, change_column, watermark_only=watermark_only)
        elif source_type == "warehouse":
            current = _compact_rows(
                read_warehouse_query(
                    _warehouse_observation_query(
                        schema_value, table_value, partition_column, change_column, watermark_only=watermark_only
                    ),
                    store=store_key,
                    context={**(context or {}), "_spark_session": spark},
                )
            )
        else:
            current = _observe_lakehouse(
                table_value,
                store_key,
                schema_value,
                partition_column,
                change_column,
                spark_session=spark,
                context=context,
                watermark_only=watermark_only,
            )
        if not current:
            current = [{"partition_value": None, "row_count": 0, "is_present": None}]
        observation_id = str(uuid4())
        values = [
            {
                **coerce_metadata_row_types(
                    _PROCESSING_STATE_TABLE,
                    {
                        **row,
                        "observation_id": observation_id,
                        "source_table_id": governed_table_id,
                        "target_table_id": None,
                        "workspace_id": active_workspace_id,
                        "run_id": source_observation_run_id(context),
                        "record_id": _processing_state_id(active_workspace_id, governed_table_id, observation_id,
                            {"empty_source": True} if row.get("is_present") is None else row.get("partition_value")),
                        "record_type": "source_observation", "status": "observed",
                        "source_table_name": table_value, "observed_at": audit["_committed_at"],
                        "pipeline_id": getattr(context.get("execution_plan"), "pipeline_id", None),
                        **audit,
                    },
                ),
                "partition_column": partition_column,
                "change_column": change_column,
            }
            for row in current
        ]
        _merge_source_observation_records(values, config=config, context=context)
        return spark.createDataFrame(values, schema=metadata_table_schema_registry()[_PROCESSING_STATE_TABLE])

    if incremental_columns is not None:
        return capture_columns(*incremental_columns, watermark_only=True)
    return None


def _summary_value(value):
    """Group numeric display values while retaining text and unavailable markers."""
    if value is None:
        return "Not captured"
    if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        return format(value, ",")
    return str(value)


class ExecutionSummary:
    """Format notebook summaries without materializing any DataFrame."""

    def __init__(self, operation, *, verbose):
        """Start the lifecycle wall clock independently of rounded stage durations."""
        self.operation = operation
        self.verbose = verbose
        self.started = time.perf_counter()

    def details(self, fields):
        """Print aligned, explicit unavailable values to notebook stdout."""
        if self.verbose:
            for label, value in fields:
                print(f"   {label:<16}{' ' if len(label) >= 16 else ''}→ {_summary_value(value)}")

    def finish(self, fields):
        """Print a concise successful summary; expand it when verbose output is enabled."""
        elapsed = round(max(0.01, time.perf_counter() - self.started), 2)
        total = int(round(elapsed))
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        if self.verbose:
            print(f"\nFabricOps {self.operation} Summary")
            for label, value in [*fields, ("Total duration", duration)]: print(f"   {label:<16}{' ' if len(label) >= 16 else ''}→ {_summary_value(value)}")  # noqa: E701
        else: print(f"FabricOps {self.operation} Summary · " + " · ".join(f"{label}: {_summary_value(value)}" for label, value in [*fields, ("Total duration", duration)]))  # noqa: E701, E501
        return elapsed


def participant_id(participant):
    """Return a typed participant's canonical Table ID or distinct file Source ID."""
    return participant.get("source_id") or participant["table_id"]


def resolve_file_participant(*, store, relative_path, file_format, read_options=None, context):
    """Resolve the configured Files root and reuse the canonical contract identity."""
    from fabricops_kit.io.shared import resolve_configured_file_path
    from fabricops_kit.data_contract.shared import file_source_identity
    # Validate before path resolution, including traversal that a path normalizer could hide.
    file_source_identity(workspace_id="validation", item_id="validation", relative_path=relative_path,
                         file_format=file_format, reader_options=read_options)
    options = dict(read_options or {})
    if any(str(key).lower() in {"path", "paths", "context", "store", "relative_path"} for key in options):
        raise ValueError("read_options cannot override the approved file location or runtime context.")
    configured, path, _ = resolve_configured_file_path(store, relative_path, context=context)
    if str(configured.kind).lower() != "lakehouse":
        raise ValueError("File reads require a Lakehouse store; Warehouse file routing is unsupported.")
    source = file_source_identity(workspace_id=configured.workspace_id, item_id=configured.item_id,
        relative_path=path, file_format=file_format, reader_options=options)
    return {**source, "store": store, "logical_id": f"{store}/Files/{source['relative_path']}"}


def read_file_participant(identity, *, context, spark_session):
    """Read a planned file using foundational I/O and the execution-owned Spark session."""
    from fabricops_kit.io import read_lakehouse_csv, read_lakehouse_json, read_lakehouse_parquet, read_lakehouse_excel
    from fabricops_kit.io.shared import resolve_configured_file_path
    readers = {"csv": read_lakehouse_csv, "json": read_lakehouse_json,
               "parquet": read_lakehouse_parquet, "excel": read_lakehouse_excel}
    _, _, path = resolve_configured_file_path(identity["store"], identity["relative_path"], context=context)
    frame = readers[identity["file_format"]](identity["relative_path"], store=identity["store"],
        context={**context, "_spark_session": spark_session, "_fabricops_suppress_io_log": True}, **identity["reader_options"])
    return {**file_participant_source(identity), "store": identity["store"], "dataframe": frame,
            "source_location": {"workspace_id": identity["workspace_id"], "item_id": identity["item_id"],
                                "relative_path": identity["relative_path"]},
            "resolved_path": path, "read_mode": "full", "is_query": False,
            "_reader_name": readers[identity["file_format"]].__name__,
            "read_metrics": {"rows_read": None, "columns": len(frame.columns), "measurement_source": None}}


def schedule_file_profiling(dataframe, *, source_id, context, presentations):
    """Run pipeline-owned profiling activities without creating table snapshots.

    File completion history is session-local. No durable interval is consumed;
    each new execution reevaluates eligibility because files may be replaced.
    """
    plan = context["execution_plan"]
    settings = validate_pipeline_profiling(plan.evidence.get("profiling_configuration"))
    history = plan.evidence.setdefault("file_profiles", {}).setdefault(source_id, {})
    policy = pipeline_profiling_policy(context=context)
    due = {activity for activity in PROFILING_ACTIVITIES
           if profiling_due(policy[activity], history.get(activity, {}), "read", datetime.now(UTC))}
    if not due:
        return {"status": "not_due" if any(policy[name]["enabled"] for name in policy) else "disabled",
                "source_id": source_id, "results_persisted": False}
    limit = settings["profiling_max_rows"]
    scope = {"profile_scope": "bounded_selection" if limit is not None else "supplied_dataframe", "profiling_max_rows": limit}
    selected = dataframe.limit(limit) if limit is not None else dataframe
    profile = build_profile_dataframe(selected).cache()
    try:
        row = profile.select("ROW_COUNT").first()
        row_count = int(row["ROW_COUNT"]) if row is not None else 0
        candidates = (_spark_profile_key_candidates(selected, profile, max_columns=3, max_candidates=8)
                      if "grain" in due else [])
        frequency_columns = _selected_frequency_columns(selected, profile, None, 80.0) if "frequency" in due else []
        frequency = build_frequency_distribution_dataframe(selected, columns=frequency_columns, top_n=5) if frequency_columns else None
        if "standard" in due:
            presentation = capture_profile_presentation(profile, scope=scope, dry_run=not plan.permits_persistence)
            if presentation:
                presentation["title"] += " · File selection (session only)"
                presentations.append(presentation)
        for activity in due:
            history[activity] = {"last_success": datetime.now(UTC).isoformat()}
        return {"status": "completed", "source_id": source_id, "profile": profile, "row_count": row_count,
                "results_persisted": False, **scope, "grain_candidates": candidates, "frequency_profile": frequency,
                "activities": sorted(due)}
    finally:
        profile.unpersist()


def file_participant_source(identity):
    """Extract the exact PR #1818 source descriptor for approval comparison."""
    return {key: identity[key] for key in ("source_type", "source_id", "workspace_id", "item_id",
                                         "relative_path", "file_format", "reader_options")}


def file_binding_source(binding):
    """Decode the explicit reader-options JSON in a persisted file destination."""
    if "reader_options_json" not in binding:
        return dict(binding)
    return {**{key: value for key, value in binding.items() if key != "reader_options_json"},
            "reader_options": json.loads(binding["reader_options_json"])}


def pipeline_physical_bindings(identities, *, config, workspace_id):
    """Capture each participant's configured physical destination independently of execution scope."""
    bindings = {}
    for table_id, item in identities.items():
        store = get_store(config, workspace_id, item["store"])
        if item.get("source_type") == "file":
            source = file_participant_source(item)
            bindings[table_id] = {**{key: value for key, value in source.items() if key != "reader_options"},
                                  "reader_options_json": canonical_pipeline_json(source["reader_options"])}
            continue
        bindings[table_id] = {"workspace_id": store.workspace_id, "item_id": store.item_id,
                              "kind": store.kind, "schema": item.get("schema"), "table_name": item["table_name"]}
    return bindings


def build_pipeline_execution_plan(*, execution_mode, sources, targets, selections=None, context=None, spark_session=None, pipeline_id=None):
    """Freeze dynamic Dry Run or Ungoverned participants under one execution."""
    if execution_mode == "governed":
        raise ValueError("Governed requires Pipeline Promotion authority; use setup_pipeline to resolve it.")
    from types import MappingProxyType

    if execution_mode not in {"dry_run", "ungoverned"}:
        raise ValueError("execution_mode must be dry_run, ungoverned or governed.")
    from fabricops_kit.data_contract.shared import validate_contract_definitions

    config, active_workspace_id, runtime = resolve_fabric_context(context=context)
    notebook_id = str(runtime.get("notebook_id") or "").strip()
    identities = resolve_pipeline_participants(
        config, active_workspace_id, sources=sources, targets=targets, context=runtime, spark_session=spark_session,
    )
    pipeline_id = validate_pipeline_id(pipeline_id)
    if selections is None:
        selections = {table_id: {"no_contract": True} for table_id in identities}
    if not isinstance(selections, dict) or set(selections) != set(identities):
        raise ValueError("Supply an explicit contract or No Contract choice for every participating table only.")
    contracts = {}
    for table_id, choice in selections.items():
        if not isinstance(choice, dict):
            raise ValueError("Every contract selection must be an explicit mapping.")
        if choice == {"no_contract": True}:
            contracts[table_id] = None
            continue
        if execution_mode == "ungoverned":
            raise ValueError("Ungoverned does not select or enforce Data Contracts.")
        if set(choice) != {"contract_id", "contract_version"}:
            raise ValueError("Select exact contract_id/contract_version or explicit no_contract=True.")
        selected = resolve_data_contract_version(
            config, active_workspace_id, table_id, choice["contract_id"], choice["contract_version"],
            spark_session=spark_session, context=runtime,
        )
        validate_contract_definitions(selected["contract_payload"])
        contract_guardrail_rows(selected, workspace_id=active_workspace_id, table_id=table_id)
        contracts[table_id] = selected
    plan_id = str(uuid4())
    run_context = {**runtime, "config": config, "scope_workspace_id": active_workspace_id, "_pipeline_spark": spark_session,
                   "_pipeline_bindings": pipeline_physical_bindings(identities, config=config, workspace_id=active_workspace_id)}
    plan = PipelineExecutionPlan(
        execution_mode, active_workspace_id, notebook_id, plan_id,
        json.dumps(identities, default=str, sort_keys=True),
        json.dumps(selections, sort_keys=True), json.dumps(contracts, default=str, sort_keys=True),
        MappingProxyType(run_context),
        pipeline_id=pipeline_id,
    )
    persist_pipeline_run(plan, spark_session=spark_session)
    return plan


def resolve_pipeline_participants(config, active_workspace_id, *, sources, targets, context=None, spark_session=None):
    """Resolve configured participants once under the shared identity validation rules."""
    identities = {}
    for role, participants in (("source", sources), ("target", targets)):
        for participant in participants:
            if participant.get("relative_path") is not None:
                if role != "source":
                    raise ValueError("Files participate only as Read sources.")
                identity = resolve_file_participant(**{key: participant.get(key) for key in
                    ("store", "relative_path", "file_format", "read_options")}, context={**(context or {}), "config": config, "scope_workspace_id": active_workspace_id})
            elif "store" in participant:
                identity = resolve_physical_table_identity(config, active_workspace_id, **{
                    key: participant[key] for key in ("store", "schema", "table_name")
                })
                if participant.get("table_id") not in (None, identity["table_id"]):
                    raise ValueError("Configured participant does not match its canonical table_id.")
            else:
                identity = resolve_catalogue_table_identity(
                    config, active_workspace_id, participant["table_id"], context=context, spark_session=spark_session,
                )
            identity = {**identity, "store_type": identity.get("store_type") or identity.get("store_kind")}
            table_id = participant_id(identity)
            logical_id = participant.get("logical_id") or identity.get("logical_id") or f"{identity['store']}/{identity['table_name']}"
            if table_id in identities and identities[table_id].get("logical_id") != logical_id:
                raise ValueError("A participant must use the same logical_id in every role.")
            roles = list(identities.get(table_id, {}).get("roles", []))
            if role in roles:
                raise ValueError(f"Duplicate {role} participant {table_id!r}.")
            identities[table_id] = {**identity, "logical_id": logical_id, "roles": [*roles, role]}
    if not identities:
        raise ValueError("Configure at least one actual source or target.")
    return identities


def _pipeline_json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def canonical_pipeline_json(value):
    """Serialize pipeline metadata strictly, with ISO date and timestamp values."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False, default=_pipeline_json_default)


def _metadata_hash(value):
    return hashlib.sha256(canonical_pipeline_json(value).encode("utf-8")).hexdigest()


def pipeline_record_content(value):
    """Normalize native timestamp instants for exact Spark commit read-back."""
    if isinstance(value, datetime):
        return (value.astimezone(UTC).replace(tzinfo=None) if value.tzinfo else value).isoformat()
    if isinstance(value, dict):
        return {key: pipeline_record_content(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [pipeline_record_content(item) for item in value]
    return value


def validate_pipeline_run(row):
    """Validate native operation facts without a configuration snapshot or definition join."""
    row = decode_metadata_row("METADATA_PIPELINE_RUN", row)
    provenance = ("pipeline_version", "promotion_id", "governed_notebook_id", "execution_identity", "run_schema_version")
    if row.get("run_schema_version") is None:
        if any(row.get(key) is not None for key in provenance):
            raise ValueError("Legacy Run has unexpected new provenance; retained evidence cannot be reinterpreted.")
        row = {key: value for key, value in row.items() if key not in provenance}
    elif row["run_schema_version"] != 3:
        raise ValueError("Unsupported Pipeline Run schema version.")
    elif row.get("execution_mode") == "governed" and any(row.get(key) in (None, "") for key in provenance):
        raise ValueError("Governed Run requires exact Pipeline Promotion and execution identity provenance.")
    operations = row["operations"]
    keys = [(participant_id(item), item["pipeline_role"]) for item in operations]
    if len(keys) != len(set(keys)) or len({item["operation_key"] for item in operations}) != len(keys):
        raise ValueError("Duplicate Pipeline Run operation membership.")
    for item in operations:
        if item["pipeline_role"] not in {"source", "target"} or not participant_id(item) or not item["destination"]:
            raise ValueError("Pipeline Run requires exact participant roles and destinations.")
        if item.get("source_type") == "file":
            from fabricops_kit.data_contract.shared import validate_contract_source
            source = file_binding_source(item["destination"])
            validate_contract_source({"source": source, "table": {}})
            if item.get("table_id") or item["source_id"] != source["source_id"] or item["pipeline_role"] != "source" or (item["read_mode"] != "full" and item["status"] != "not_started"):
                raise ValueError("File operations require a full source Read without a Table ID.")
        elif item.get("source_id") is not None or str(item["table_id"]).startswith("file:"):
            raise ValueError("Table operations cannot use a file Source ID as a Table ID.")
        refs = [item.get(key) for key in ("contract_id", "contract_version", "payload_sha256")]
        if any(value is not None for value in refs) and not all(value is not None for value in refs):
            raise ValueError("Incomplete Pipeline Run contract reference.")
        if len(set(item["source_table_ids"])) != len(item["source_table_ids"]):
            raise ValueError("Duplicate Pipeline Run source association.")
        if item["status"] == "succeeded":
            mode = item["read_mode"] if item["pipeline_role"] == "source" else item["write_mode"]
            # Run records retain historical strategy facts; execution validates the five current choices.
            allowed = {"full", "incremental"} if item["pipeline_role"] == "source" else {"overwrite", "append", "append_all", "append_new_only", "scd1", "scd2"}
            if mode not in allowed:
                raise ValueError("Successful Pipeline Run operation requires its execution mode.")
    if row["status"] == "succeeded" and (not row.get("completed_at") or row["boundary_completed"] is not True
            or row["failures"] or not operations or any(item["status"] != "succeeded" or not item["stages"]
            or len({stage["stage"] for stage in item["stages"]}) != len(item["stages"])
            or any(stage.get("status") not in {"passed", "warning", "skipped"}
                   or stage.get("evaluation_status") == "not_fully_evaluated" for stage in item["stages"])
            for item in operations)):
        raise ValueError("Pipeline Run success requires complete whole-run operation results.")
    return row


def pipeline_run_row(plan, *, status, completed_at=None, durable=False):
    """Capture actual table/contract participation and governed settings."""
    identities, contracts = json.loads(plan.participants_json), json.loads(plan.contracts_json)
    operations = []
    for table_id, identity in identities.items():
        contract = contracts.get(table_id)
        for role in identity["roles"]:
            key = f"{role}:{identity.get('logical_id') or identity['store'] + '/' + identity['table_name']}"
            actual = plan.evidence["operations"][key]
            operations.append({"operation_key": key,
                **({"source_type": "file", "source_id": table_id, "table_id": None} if identity.get("source_type") == "file" else {"table_id": table_id}),
                **({"source_ids": actual["source_ids"]} if actual.get("source_ids") else {}), "pipeline_role": role,
                "contract_id": contract["contract_id"] if contract else None,
                "contract_version": contract["contract_version"] if contract else None,
                "payload_sha256": hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest() if contract else None,
                "destination": plan.runtime_context["_pipeline_bindings"][table_id],
                **{name: actual.get(name) for name in ("read_parameters", "write_parameters", "repartition_by", "read_mode", "write_mode", "query_sha256", "incremental_target_table_id",
                    "started_at", "completed_at", "rows_read", "rows_written", "observed_columns_json")},
                "metrics": dict(actual.get("metrics") or {}),
                "source_table_ids": actual.get("source_table_ids", []),
                "status": actual["status"], "stages": actual["stages"]})
    config = plan.runtime_context["config"]
    row = {"run_id": plan.plan_id, "pipeline_id": plan.pipeline_id, "approval_id": plan.evidence.get("promotion", {}).get("approval_id") if plan.execution_mode == "governed" else None,
        "execution_mode": plan.execution_mode, "workspace_id": plan.workspace_id,
        "started_at": plan.evidence["started_at"], "completed_at": completed_at, "status": status,
        "activation_revision": str(plan.evidence["governance_approval"]["revision"]) if plan.execution_mode == "governed" and plan.evidence.get("governance_approval") else None,
        "pipeline_version": plan.pipeline_version,
        "promotion_id": plan.promotion_id or None, "governed_notebook_id": plan.governed_notebook_id or None,
        "execution_identity": plan.runtime_context.get("user_id") or plan.runtime_context.get("user_name") or None,
        "run_schema_version": 3,
        "boundary_completed": plan.evidence.get("boundary_completed", False),
        "operations": sorted(operations, key=lambda item: item["operation_key"]),
        "profiling": plan.evidence.get("profiling", []), "failures": plan.evidence["failures"],
        "warnings_json": canonical_pipeline_json(plan.evidence.get("warnings", [])),
        **(build_runtime_audit_fields(config=config, active_workspace_id=plan.workspace_id, runtime_context=plan.runtime_context) if durable else {})}
    validate_pipeline_run(row)
    return coerce_metadata_row_types("METADATA_PIPELINE_RUN", row)


def _read_pipeline_run_rows(plan, *, spark_session=None):
    frame = read_lakehouse_table("METADATA_PIPELINE_RUN", store="Metadata",
        schema=metadata_table_physical_schema(plan.runtime_context["config"], "METADATA_PIPELINE_RUN"),
        context={**(plan.runtime_context or {}), "_spark_session": spark_session, "_fabricops_suppress_io_log": True})
    return [_row_to_dict(row) for row in frame.filter(
        "`run_id` = '" + plan.plan_id.replace("'", "''") + "'").limit(2).collect()]


def _merge_pipeline_run_row(plan, row, *, spark_session=None):
    from delta.tables import DeltaTable
    from pyspark.sql.types import StructField, StructType

    spark = get_spark_session(spark_session, context=plan.runtime_context)
    table = "METADATA_PIPELINE_RUN"
    schema = metadata_table_schema_registry()[table]
    physical = encode_metadata_row(table, validate_pipeline_run(row))
    expected = plan.evidence.get("persisted_run_row")
    if expected is not None:
        expected = encode_metadata_row(table, expected)
    frame = spark.createDataFrame([{**physical, "_expected": expected}], StructType([
        *schema.fields, StructField("_expected", schema, True)]))
    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        "Metadata", table, metadata_table_physical_schema(plan.runtime_context["config"], table), context=plan.runtime_context)
    if expected is None:
        if _read_pipeline_run_rows(plan, spark_session=spark_session):
            raise RuntimeError("Pipeline Run identity already exists; create a new plan.")
        properties = DeltaTable.forPath(spark, path).detail().select("properties").first()["properties"]
        if "delta.setTransactionRetentionDuration" in properties:
            raise RuntimeError("Pipeline Run requires unbounded Delta transaction identity retention.")
        retry_delta_metadata(lambda: frame.drop("_expected").write.format("delta").mode("append")
         .option("txnAppId", "fabricops-pipeline-run:" + plan.plan_id).option("txnVersion", 0).save(path))
    else:
        # Compare the complete previous row inside the transaction. No physical
        # token column or per-update table metadata mutation is needed.
        previous = "struct(" + ",".join("target.`" + name + "`" for name in schema.fieldNames()) + ")"
        changes = {name: "source.`" + name + "`" for name in schema.fieldNames()}
        changes["run_id"] = ("CASE WHEN target.completed_at IS NULL AND "
            "(target.status <> 'failed' OR source.status = 'failed') AND (" + previous + " <=> source._expected) "
            "THEN source.run_id ELSE CAST(raise_error('Stale or terminal Pipeline Run') AS STRING) END")
        retry_delta_metadata(lambda: DeltaTable.forPath(spark, path).alias("target")
            .merge(frame.alias("source"), "target.run_id = source.run_id").whenMatchedUpdate(set=changes).execute())
    stored = _read_pipeline_run_rows(plan, spark_session=spark_session)
    observed = validate_pipeline_run(stored[0]) if len(stored) == 1 else {}
    wanted = validate_pipeline_run(physical)
    if not observed or pipeline_record_content(observed) != pipeline_record_content(wanted):
        raise RuntimeError("Pipeline Run publication was not confirmed.")
    plan.evidence["persisted_run_row"] = stored[0]


def persist_pipeline_run(plan, *, spark_session=None, status="incomplete", completed_at=None):
    """Persist one authoritative Delta snapshot; confirm lost acknowledgements by read-back."""
    durable = plan.permits_persistence
    row = None
    try:
        if plan.evidence["failures"] or any(item["status"] == "failed" for item in plan.evidence["operations"].values()) or any(
            result.get("can_continue") is False for result in plan.results):
            status = "failed"
        row = pipeline_run_row(plan, status=status, completed_at=completed_at, durable=durable)
        if durable:
            _merge_pipeline_run_row(plan, row, spark_session=spark_session)
        return row
    except Exception as exc:
        if row is not None:
            try:
                matches = _read_pipeline_run_rows(plan, spark_session=spark_session)
                if len(matches) == 1:
                    observed = validate_pipeline_run(matches[0])
                    if pipeline_record_content(observed) == pipeline_record_content(row):
                        plan.evidence["persisted_run_row"] = matches[0]
                        return row
            except Exception:
                plan.evidence["persistence_failed"] = True
                plan.evidence["failures"].append({"code": "evidence_commit_unknown"})
                raise RuntimeError(
                    "Pipeline run evidence persistence outcome is unknown; inspect the committed Delta snapshot. "
                    "A committed complete snapshot is authoritative; do not replay this plan. Create a new plan for a retry."
                ) from exc
        plan.evidence["persistence_failed"] = True
        # Connector exception messages can contain credentials or business values.
        plan.evidence["failures"].append({"code": "evidence_persistence_failed", "exception_type": type(exc).__name__})
        raise RuntimeError("Pipeline run evidence persistence failed; create a new plan.") from exc


class PipelineOperation:
    """Serialize a plan's operations and finalization, including rejected retries."""

    def __init__(self, plan, role, arguments):
        """Capture bound parameters without retaining data or credentials in metadata."""
        self.plan, self.role, self.arguments = plan, role, arguments
        self.record = None

    def __enter__(self):
        """Reserve the operation before iterating inputs or executing any stage."""
        plan = self.plan
        if not isinstance(plan, PipelineExecutionPlan):
            raise ValueError("An explicit PipelineExecutionPlan is required.")
        plan.lock.acquire()
        args = self.arguments
        try:
            if plan.evidence.get("sealed") or plan.evidence.get("persistence_failed"):
                raise RuntimeError("Execution plan is closed or evidence persistence failed; create a new plan.")
            if plan.evidence["failures"] and plan.permits_persistence:
                raise RuntimeError("Pipeline run previously failed; create a new plan.")
            physical_identity = (resolve_file_participant(**{key: args.get(key) for key in
                ("store", "relative_path", "file_format", "read_options")}, context=plan.runtime_context)
                if self.role == "source" and args.get("relative_path") is not None else
                resolve_physical_table_identity(plan.runtime_context["config"], plan.workspace_id,
                    **{key: args[key] for key in ("store", "schema", "table_name")}))
            table_id = participant_id(physical_identity)
            identities = json.loads(plan.participants_json)
            identity = identities.get(table_id)
            if identity is None or self.role not in identity["roles"]:
                raise ValueError("Operation must match a declared pipeline participant and role.")
            actual_binding = pipeline_physical_bindings(
                {table_id: physical_identity}, config=plan.runtime_context["config"], workspace_id=plan.workspace_id,
            )[table_id]
            expected_binding = plan.runtime_context.get("_pipeline_bindings", {}).get(table_id)
            if actual_binding != expected_binding:
                raise ValueError("Operation physical destination differs from the execution plan's frozen binding.")
            logical = identity.get("logical_id") or f"{identity['store']}/{identity['table_name']}"
            key = f"{self.role}:{logical}"
            if plan.evidence["operations"][key]["status"] != "not_started":
                raise ValueError("Duplicate operation: retries require a new pipeline execution plan.")
            self.record = {"status": "incomplete", "stages": [],
                           "started_at": datetime.now(UTC).isoformat()}
            plan.evidence["operations"][key] = self.record
            # These are the notebook settings retained and compared in Governed mode.
            # Exact processing parameters are retained in the approved Pipeline Activation.
            processing_parameters = validated_pipeline_processing(role=self.role,
                read_mode=str(args.get("read_mode", "full") or "").strip().lower() if self.role == "source" else None,
                write_mode=str(args.get("write_mode", "overwrite") or "").strip().lower() if self.role == "target" else None,
                read_parameters=args.get("read_parameters") if self.role == "source" else None,
                write_parameters=args.get("write_parameters") if self.role == "target" else None,
                repartition_by=args.get("repartition_by") if self.role == "target" else None)
            self.record.update(
                store=str(identity["store"]),
                requested_schema=args.get("schema"),
                read_parameters=json.loads(canonical_pipeline_json(args.get("read_parameters") or {})) if self.role == "source" else None,
                repartition_by=args.get("repartition_by") if self.role == "target" else None,
                write_parameters=json.loads(canonical_pipeline_json(args.get("write_parameters") or {})) if self.role == "target" else None,
                read_mode=str(args.get("read_mode", "full") or "").strip().lower() if self.role == "source" else None,
                write_mode=str(args.get("write_mode", "overwrite") or "").strip().lower() if self.role == "target" else None,
                query_sha256=hashlib.sha256(args["query"].encode()).hexdigest() if args.get("query") else None,
                incremental_target_table_id=args.get("target_table_id"),
                rows_read=None,
                rows_written=None,
                metrics={},
                source_table_ids=[],
            )
            self.record.update(processing_parameters)
            if self.role == "target":
                args["sources"] = tuple(args["sources"])
                self.record["source_table_ids"] = sorted(source["table_id"] for source in args["sources"] if source.get("table_id"))
                file_ids = sorted(source["source_id"] for source in args["sources"] if source.get("source_type") == "file")
                if file_ids:
                    self.record["source_ids"] = file_ids
            if plan.execution_mode == "governed":
                from fabricops_kit.activated_pipeline.shared import verify_governed_plan
                verify_governed_plan(plan, spark_session=args.get("spark_session"))
                activated = {(participant_id(item), item["pipeline_role"]): item for item in json.loads(plan.activated_operations_json)}
                selected = activated.get((table_id, self.role))
                enforced = ("read_parameters", "repartition_by", "write_parameters", "read_mode", "write_mode", "query_sha256", "incremental_target_table_id", "source_table_ids", "source_ids")
                if not plan.promotion_id or selected is None or any(self.record.get(name) != selected.get(name) for name in enforced):
                    raise ValueError("Governed table or execution mode differs from activated authority.")
            elif plan.execution_mode == "ungoverned" and self.role == "target":
                from fabricops_kit.activated_pipeline.shared import guard_ungoverned_write
                guard_ungoverned_write(plan, table_id, actual_binding, spark_session=args.get("spark_session"))
            persist_pipeline_run(plan, spark_session=args.get("spark_session"))
            return self
        except BaseException as exc:
            try:
                if not plan.evidence.get("sealed") and not plan.evidence.get("persistence_failed"):
                    plan.evidence["failures"].append({"code": "operation_start_failed", "exception_type": type(exc).__name__})
                    if self.record is not None:
                        self.record["status"] = "failed"
                        self.record["completed_at"] = datetime.now(UTC).isoformat()
                    persist_pipeline_run(plan, spark_session=args.get("spark_session"), status="failed")
            finally:
                plan.lock.release()
                session = plan.evidence.get("session")
                if session is not None:
                    session.close(failed=True)
            raise

    def capture_metrics(self, metrics):
        """Retain already-measured operation facts without evaluating data."""
        self.record["metrics"] = {
            str(name): (int(value) if isinstance(value, int) and not isinstance(value, bool) else value)
            for name, value in dict(metrics or {}).items()
        }
        if self.role == "source" and self.record["metrics"].get("rows_read") is not None:
            self.record["rows_read"] = int(self.record["metrics"]["rows_read"])
        if self.role == "target" and self.record["metrics"].get("rows_committed") is not None:
            self.record["rows_written"] = int(self.record["metrics"]["rows_committed"])

    def complete(self, stages, *, rows_read=None, rows_written=None, metrics=None):
        """Keep safe stage outcomes and actual row metrics; never trigger Spark actions."""
        if metrics is not None:
            self.capture_metrics(metrics)
        if rows_read is not None:
            self.record["rows_read"] = int(rows_read)
        if rows_written is not None:
            self.record["rows_written"] = int(rows_written)
        self.record["completed_at"] = datetime.now(UTC).isoformat()
        self.record["stages"] = [{key: stage[key] for key in ("stage", "status", "evaluation_status") if key in stage}
                                 for stage in stages]
        self.record["status"] = "failed" if any(
            stage.get("status") in {"blocked", "failed"} or stage.get("evaluation_status") == "not_fully_evaluated"
            for stage in stages) else "succeeded"

    def __exit__(self, exc_type, exc, traceback):
        """Persist the outcome and release the plan even when storage fails."""
        plan = self.plan
        try:
            if exc is not None:
                self.record["status"] = "failed"
                self.record["completed_at"] = datetime.now(UTC).isoformat()
                if self.role == "target" and getattr(exc, "published", False):
                    write_metrics = getattr(exc, "write_metrics", {}) or {}
                    self.capture_metrics(write_metrics)
                plan.evidence["failures"].append({"code": "operation_failed", "exception_type": exc_type.__name__})
            try:
                persist_pipeline_run(plan, spark_session=self.arguments.get("spark_session"))
            except RuntimeError as persistence_error:
                for name in ("published", "table_id", "write_metrics", "failed_stage", "persistence_status"):
                    if exc is not None and hasattr(exc, name):
                        setattr(persistence_error, name, getattr(exc, name))
                if self.role == "target" and any(stage.get("stage") == "Write" and stage.get("status") == "passed"
                                                  for stage in self.record["stages"]):
                    persistence_error.published = True
                    persistence_error.failed_stage = "Run evidence"
                raise
        finally:
            plan.lock.release()
            session = plan.evidence.get("session")
            if session is not None:
                session.refresh()
                if exc is not None:
                    session.close(failed=True)
        return False


def finalize_pipeline_run(plan, *, spark_session=None, failed=False):
    """Seal a run after every declared operation; never race an in-flight operation."""
    if not isinstance(plan, PipelineExecutionPlan):
        raise ValueError("An explicit PipelineExecutionPlan is required.")
    with plan.lock:
        if plan.evidence.get("persistence_failed"):
            raise RuntimeError("Evidence persistence failed; create a new plan.")
        if plan.evidence.get("sealed"):
            return plan.evidence["final_result"]
        if failed:
            plan.evidence["failures"].append({"code": "project_execution_failed"})
        if plan.evidence.get("boundary_completed") and not failed and not plan.evidence["failures"]:
            try:
                evaluate_pipeline_source_drift(plan, spark_session=spark_session)
            except RuntimeError:
                plan.evidence["failures"].append({"code": "source_drift_blocked"})
        operations = plan.evidence["operations"]
        blocked = failed or bool(plan.evidence["failures"]) or any(
            row.get("can_continue") is False for row in plan.results) or any(
            operation["status"] == "failed" for operation in operations.values())
        expected = {f"{role}:{identity.get('logical_id') or identity['store'] + '/' + identity['table_name']}"
                    for identity in json.loads(plan.participants_json).values() for role in identity["roles"]}
        complete = bool(expected) and set(operations) == expected and all(operation["status"] == "succeeded" for operation in operations.values())
        complete = complete and bool(plan.evidence.get("boundary_completed"))
        status = "failed" if blocked else "succeeded" if complete else "incomplete"
        if status == "succeeded" and plan.execution_mode == "dry_run":
            status = "dry_run_completed"
        elif status == "succeeded" and plan.execution_mode == "ungoverned":
            status = "ungoverned_completed"
        row = persist_pipeline_run(plan, spark_session=spark_session, status=status, completed_at=datetime.now(UTC))
        plan.evidence["final_result"] = row
        if status in {"succeeded", "ungoverned_completed", "dry_run_completed"} and plan.evidence.get("source_drift_policy", {}).get("source_drift_enabled"):
            if not plan.permits_persistence:
                plan.evidence["source_snapshot_acceptance"] = {"status": "diagnostic_only"}
            else:
                try:
                    accept_pipeline_source_snapshots(plan, spark_session=spark_session)
                except Exception as exc:
                    unknown = bool(getattr(exc, "outcome_unknown", False))
                    reason = ("Baseline acceptance outcome is unknown; inspect shared heads and immutable acceptance records before retrying. Do not assume rollback."
                        if unknown else "Baseline acceptance was not confirmed; inspect snapshot integrity and concurrent acceptance before a new execution from Read.")
                    plan.evidence["source_snapshot_acceptance"] = {"status": "acceptance_unknown" if unknown else "acceptance_failed",
                        "error_type": type(exc).__name__, "reason": reason}
                    try:
                        _record_source_drift_result({"status": "warning", "can_continue": True, "action": "Warn", "severity": "warning",
                            "pipeline_id": plan.pipeline_id, "reason": reason},
                            context={**plan.runtime_context, "execution_plan": plan, "_spark_session": spark_session}, rule_type="baseline_acceptance")
                    except Exception:
                        plan.evidence["source_snapshot_acceptance"]["diagnostics_persisted"] = False
        plan.evidence.update(sealed=True, final_result=row)
        if plan.execution_mode == "dry_run" and status == "dry_run_completed" and plan.evidence.get("notebook_snapshot") is not None:
            from fabricops_kit.activated_pipeline.shared import persist_engineering_dry_run
            try:
                plan.evidence["dry_run_evidence_uri"] = persist_engineering_dry_run(plan, spark_session=spark_session)
            except Exception:
                plan.evidence["submission_persistence_failed"] = True
                raise
        return row


def _pipeline_execution_owner():
    from threading import get_ident
    from asyncio import current_task
    try:
        task = current_task()
    except RuntimeError:
        task = None
    return get_ident(), task


# Each Python context owns an execution instance; names are never used as keys.
from contextvars import ContextVar

_ACTIVE_PIPELINE = ContextVar("fabricops_pipeline_execution", default=None)


class PipelineSession:
    """Own one notebook execution, contract choices and pipeline source association."""

    def __init__(self, plan, spark, *, inspector=None):
        """Bind immutable authority separately from the execution's mutable journal."""
        self.plan, self.spark, self.inspector = plan, spark, inspector
        self.sources = []
        self.choices = {}
        self.selected_contracts = {}
        self.frozen_rows = []
        self.controls = []
        self.reviews = {}
        self.report = None
        self.shell = None
        self.closed = False
        self.owner = _pipeline_execution_owner()
        plan.evidence["session"] = self

    @property
    def pipeline_id(self):
        """Return the permanent registered UUID independently of this run ID."""
        return self.plan.pipeline_id

    def owns_current_execution(self):
        """Reject inherited bindings in concurrent tasks or threads."""
        current = _pipeline_execution_owner()
        if current == self.owner:
            return True
        if (self.shell is not None and current[0] == self.owner[0]
                and self.owner[1] is not None and self.owner[1].done()):
            self.owner = current
            return True
        return False

    def validate_current_context(self):
        """Reject changed notebook setup before operating or completing an open run."""
        try:
            runtime = get_default_fabric_context(require_notebook_setup=True)
            if runtime.get("_notebook_setup") is not self.plan.runtime_context.get("_notebook_setup"):
                raise RuntimeError("Notebook configuration changed. Call setup_pipeline() again after setup_notebook().")
        except RuntimeError:
            self.close()
            raise

    def select_contract(self, table_id, contract_id=None, contract_version=None, *, no_contract=False):
        """Freeze explicit exact contract choices before data operations start."""
        if self.closed or self.plan.evidence["operations"] or self.plan.execution_mode not in {"dry_run"}:
            raise RuntimeError("Contract choices are locked; they are available only before a Dry Run starts.")
        if no_contract:
            if contract_id is not None or contract_version is not None:
                raise ValueError("No Contract cannot include a contract identity.")
            self.selected_contracts.pop(table_id, None)
            self.choices[table_id] = {"no_contract": True}
        else:
            matches = [row for row in self.frozen_rows if participant_id(row) == table_id
                       and row["contract_id"] == contract_id and row["contract_version"] == contract_version]
            if not matches and self.shell is None:
                matches = [resolve_data_contract_version(self.plan.runtime_context["config"], self.plan.workspace_id,
                    table_id, contract_id, contract_version, spark_session=self.spark, context=self.plan.runtime_context)]
            if len(matches) != 1:
                raise ValueError("Select an available exact frozen contract version.")
            self.selected_contracts[table_id] = dict(matches[0])
            self.choices[table_id] = {"contract_id": contract_id, "contract_version": contract_version}
        self.refresh()

    def operation_plan(self, role, arguments):
        """Discover dynamic participants; Governed stays activation-bound."""
        from dataclasses import replace
        if self.closed:
            raise RuntimeError("Pipeline execution is closed; run Setup Pipeline again.")
        with self.plan.lock:
            if role == "source" and self.plan.evidence.get("source_drift_reads_closed"):
                raise RuntimeError("Source Drift requires all Reads before any Write. Start a new pipeline and read every source first.")
            if self.plan.execution_mode in {"dry_run", "ungoverned"}:
                identities = json.loads(self.plan.participants_json)
                identity = (resolve_file_participant(**{key: arguments.get(key) for key in
                    ("store", "relative_path", "file_format", "read_options")}, context=self.plan.runtime_context)
                    if role == "source" and arguments.get("relative_path") is not None else
                    resolve_physical_table_identity(self.plan.runtime_context["config"], self.plan.workspace_id,
                        **{key: arguments[key] for key in ("store", "schema", "table_name")}))
                requested = [(role, identity)]
                if role == "source" and arguments.get("target_store") is not None:
                    requested.append(("target", resolve_physical_table_identity(
                        self.plan.runtime_context["config"], self.plan.workspace_id,
                        store=arguments["target_store"], schema=arguments.get("target_schema"),
                        table_name=arguments["target_table_name"])))
                selections = json.loads(self.plan.selections_json)
                contracts = json.loads(self.plan.contracts_json)
                for participant_role, identity in requested:
                    table_id = participant_id(identity)
                    if (self.plan.execution_mode == "ungoverned" and participant_role == "target"
                            and table_id in self.plan.runtime_context.get("_governed_table_ids", ())):
                        raise ValueError(f"Ungoverned cannot write governed table {table_id!r}; use Governed mode with its activated Data Contract.")
                    roles = list(identities.get(table_id, {}).get("roles", []))
                    if participant_role not in roles:
                        logical = identity.get("logical_id") or f"{identity['store']}/{identity['table_name']}"
                        identities[table_id] = {**identity, "logical_id": logical, "roles": [*roles, participant_role]}
                        choice = (self.choices.get(table_id, {"no_contract": True})
                                  if self.plan.execution_mode == "dry_run" else {"no_contract": True})
                        selections[table_id] = choice
                        if choice == {"no_contract": True}:
                            contracts[table_id] = None
                        else:
                            selected = resolve_data_contract_version(self.plan.runtime_context["config"], self.plan.workspace_id,
                                table_id, choice["contract_id"], choice["contract_version"],
                                spark_session=self.spark, context=self.plan.runtime_context)
                            reviewed = self.selected_contracts.get(table_id, {})
                            if reviewed.get("contract_payload_json") is not None and reviewed["contract_payload_json"] != selected["contract_payload_json"]:
                                raise RuntimeError("Frozen contract changed since selection; start a new execution.")
                            from fabricops_kit.data_contract.shared import validate_contract_definitions
                            validate_contract_definitions(selected["contract_payload"])
                            contract_guardrail_rows(selected, workspace_id=self.plan.workspace_id, table_id=table_id)
                            contracts[table_id] = selected
                        self.plan.evidence["operations"][f"{participant_role}:{logical}"] = {
                            "status": "not_started", "stages": []}
                context = {**self.plan.runtime_context, "_pipeline_bindings": pipeline_physical_bindings(
                    identities, config=self.plan.runtime_context["config"], workspace_id=self.plan.workspace_id)}
                from types import MappingProxyType
                self.plan = replace(self.plan, participants_json=canonical_pipeline_json(identities),
                    selections_json=canonical_pipeline_json(selections), contracts_json=canonical_pipeline_json(contracts),
                    runtime_context=MappingProxyType(context))
            return self.plan

    def register_source(self, result):
        """Associate a successful Read with this execution, without claiming exact lineage."""
        with self.plan.lock:
            if result.get("execution_plan_id") != self.plan.plan_id:
                raise ValueError("Read belongs to another execution.")
            self.sources.append(result)
        self.refresh()
        return result

    def refresh(self):
        """Refresh a compact report using status text as well as mode color."""
        if self.report is None:
            return
        import html
        mode = PIPELINE_MODE_NAMES[self.plan.execution_mode]
        color = {"Dry Run": "#986f0b", "Ungoverned": "#0078d4", "Governed": "#107c10"}[mode]
        result = self.plan.evidence.get("final_result", {})
        status = result.get("status") or ("failed" if self.plan.evidence["failures"] else "incomplete")
        operations = "".join(f"<li>{html.escape(key)}: {html.escape(item['status'])}</li>"
                             for key, item in self.plan.evidence["operations"].items())
        checks = "".join(f"<li>{html.escape(str(row.get('guardrail_type', 'Guardrail')))}: "
                         f"{html.escape(str(row.get('status', 'unknown')))}</li>" for row in self.plan.results)
        failures = "".join(f"<li>{html.escape(str(row.get('code', 'execution_failed')))}</li>"
                           for row in self.plan.evidence["failures"])
        self.report.value = (f'<div style="font:13px Segoe UI, sans-serif;color:#243449;border-left:4px solid {color};padding:10px 14px">'
            f'<b>{html.escape(self.plan.pipeline_id)}</b> · {mode} · {html.escape(status)}'
            '<p>Source associations describe pipeline participation.</p>'
            f'<ul>{operations}</ul><details><summary>Guardrail results and diagnostics</summary><ul>{checks}{failures}</ul></details></div>')
        for table_id, (detail, row) in self.reviews.items():
            detail.value = self.inspector(row, ("source", "target"), self.plan.results)
        for control in self.controls:
            control.disabled = self.closed or bool(self.plan.evidence["operations"])

    def cell_completed(self, result):
        """Use IPython's supported error signal, never its per-cell success as run success."""
        if not self.owns_current_execution():
            return
        if getattr(result, "error_before_exec", None) is not None or getattr(result, "error_in_exec", None) is not None:
            self.close(failed=True)
        else:
            self.refresh()

    def close(self, *, failed=False):
        """Seal failure or an incomplete boundary and discard source references."""
        if self.closed:
            return
        try:
            finalize_pipeline_run(self.plan, spark_session=self.spark, failed=failed)
        finally:
            import atexit
            atexit.unregister(self.close)
            for frame in self.plan.evidence.pop("source_observation_caches", []):
                frame.unpersist()
            self.closed = True
            if failed or not self.plan.evidence.get("boundary_completed") or self.plan.evidence.get("final_result", {}).get("status") not in {"succeeded", "ungoverned_completed", "dry_run_completed"}:
                self.plan.evidence.pop("profile_observations", None)
            self.sources.clear()
            for cache in (_CURRENT_FRESHNESS_EVIDENCE,
                          _PENDING_SOURCE_OBSERVATIONS,
                          _INCREMENTAL_SOURCE_SCOPES, _ACTIVE_PUBLICATION_SOURCES):
                for key in list(cache):
                    if key[:2] == (self.plan.workspace_id, self.plan.plan_id):
                        cache.pop(key, None)
            if self.shell is not None:
                self.shell.events.unregister("post_run_cell", self.cell_completed)
            if _ACTIVE_PIPELINE.get() is self:
                _ACTIVE_PIPELINE.set(None)
            self.refresh()


def close_current_pipeline_session():
    """Close only the pipeline owned by this execution before replacing setup."""
    previous = _ACTIVE_PIPELINE.get()
    if previous is not None and previous.owns_current_execution():
        previous.close()


def current_pipeline_session():
    """Return only the execution bound to this Python context."""
    session = _ACTIVE_PIPELINE.get()
    if session is None or session.closed:
        raise RuntimeError("Run setup_pipeline(pipeline_mode=...) before Read or Write.")
    if not session.owns_current_execution():
        raise RuntimeError("This execution belongs to another task or thread; run setup_pipeline in this context.")
    session.validate_current_context()
    return session


def validate_pipeline_id(pipeline_id):
    """Return a canonical Fabric GUID used as an internal logical Pipeline ID."""
    from uuid import UUID
    try:
        identity = UUID(pipeline_id) if isinstance(pipeline_id, str) else None
    except ValueError:
        identity = None
    if identity is None or str(identity) != pipeline_id.lower():
        raise ValueError("Pipeline identity must be a canonical Fabric Notebook ID GUID.")
    return str(identity)


def start_pipeline_session(pipeline_mode, *, inspector=None):
    """Resolve runtime services and install conservative notebook lifecycle reporting."""
    import atexit
    from contextlib import nullcontext
    try:
        from IPython import get_ipython
    except ModuleNotFoundError as exc:
        if exc.name != "IPython":
            raise
        shell = None
    else:
        shell = get_ipython()
    startup = None
    if shell is not None:
        from fabricops_kit.widgets.shared import WidgetStartup
        startup = WidgetStartup("Pipeline execution", tone="engineering", reserved_height="360px")
    from types import MappingProxyType
    from fabricops_kit.config.shared import resolve_runtime_context
    close_current_pipeline_session()
    with startup.phase("initialization", "Reusing notebook configuration…") if startup else nullcontext():
        runtime = get_default_fabric_context(require_notebook_setup=True)
        config, active_workspace_id = runtime["config"], runtime["scope_workspace_id"]
        runtime = {**runtime, **{key: value for key, value in resolve_runtime_context(context=runtime).items() if value is not None},
                   "config": config, "scope_workspace_id": active_workspace_id}
    with startup.phase("spark_loading", "Resolving the Spark session…") if startup else nullcontext():
        spark = get_spark_session()
    with startup.phase("metadata_loading", "Resolving the execution plan…") if startup else nullcontext():
        notebook_id = runtime.get("notebook_id")
        identity_row = None
        if notebook_id:
            from fabricops_kit.activated_pipeline.shared import resolve_pipeline_identity
            pipeline_id, identity_row = resolve_pipeline_identity(context=runtime, spark_session=spark)
        elif pipeline_mode == "Dry Run":
            # Headless diagnostics may run without Fabric identity, but cannot be promoted.
            pipeline_id = str(uuid4())
        else:
            raise RuntimeError("Persistent pipeline execution requires Fabric currentNotebookId; no manual Pipeline ID is accepted.")
        if identity_row is not None and identity_row["role"] == "governed" and pipeline_mode != "Governed":
            raise RuntimeError("This notebook is a promoted implementation. Run it in Governed mode; do not execute a promoted snapshot as Ungoverned.")
        print(f"FabricOps Pipeline\nPipeline ID: {pipeline_id}\nNotebook ID: {notebook_id or 'Unavailable'}\nMode: {pipeline_mode}")
        if pipeline_mode == "Governed":
            from fabricops_kit.activated_pipeline.shared import build_governed_pipeline_plan
            plan = build_governed_pipeline_plan(pipeline_id=pipeline_id, context=runtime, spark_session=spark)
        else:
            execution_mode = "dry_run" if pipeline_mode == "Dry Run" else "ungoverned"
            plan = PipelineExecutionPlan(execution_mode, active_workspace_id, str(notebook_id or ""), str(uuid4()),
                "{}", "{}", "{}", MappingProxyType({**runtime, "_pipeline_spark": spark, "_pipeline_bindings": {}}),
                pipeline_id=pipeline_id)
            plan.evidence["dynamic_participants"] = True
            if pipeline_mode == "Dry Run" and notebook_id:
                try:
                    from fabricops_kit.activated_pipeline.shared import FabricNotebookClient
                    plan.evidence["notebook_snapshot"] = FabricNotebookClient().definition(active_workspace_id, notebook_id)
                except Exception:
                    plan.evidence["notebook_snapshot_unavailable"] = True
    session = PipelineSession(plan, spark, inspector=inspector)
    try:
        if shell is not None:
            with startup.phase("form_loading", "Loading optional frozen Data Contracts…" if pipeline_mode == "Dry Run" else "Preparing pipeline controls…"):
                from fabricops_kit.widgets.shared import require_ipywidgets, form_page
                widgets = require_ipywidgets()
                session.report = widgets.HTML()
                children = [session.report]
                if pipeline_mode == "Dry Run":
                    rows = read_lakehouse_table("METADATA_DATA_CONTRACT", store="Metadata",
                        schema=metadata_table_physical_schema(config, "METADATA_DATA_CONTRACT"),
                        context={**(runtime or {}), "_spark_session": spark}).collect()
                    session.frozen_rows = [_row_to_dict(row) for row in rows if str(_row_to_dict(row).get("status", "")).lower() == "frozen"]
                    for table_id in sorted({participant_id(row) for row in session.frozen_rows}):
                        versions = [row for row in session.frozen_rows if participant_id(row) == table_id]
                        options = [("No Contract", "")] + [(f"{row.get('contract_name') or row['contract_id']} · v{row['contract_version']}",
                            f"{row['contract_id']}\n{row['contract_version']}") for row in versions]
                        payload = _contract_payload(versions[0])
                        label = payload.get("source", {}).get("relative_path") or payload.get("table", {}).get("table_name") or versions[0].get("contract_name") or "Dataset"
                        import html
                        dataset_label = widgets.HTML("<b>" + html.escape(str(label)) + "</b>")
                        control = widgets.Dropdown(options=options, description="Contract", layout=widgets.Layout(width="100%"))
                        detail = widgets.HTML("<p>No Contract selected.</p>")
                        def change(event, table_id=table_id, detail=detail, versions=versions):
                            value = event["new"]
                            if not value:
                                session.select_contract(table_id, no_contract=True)
                                session.reviews.pop(table_id, None)
                                detail.value = "<p>No Contract selected.</p>"
                            else:
                                contract_id, version = value.split("\n")
                                session.select_contract(table_id, contract_id, int(version))
                                row = next(row for row in versions if row["contract_id"] == contract_id and row["contract_version"] == int(version))
                                session.reviews[table_id] = (detail, row)
                                detail.value = inspector(row, ("source", "target"), session.plan.results) if inspector else ""
                        control.observe(change, names="value")
                        session.controls.append(control)
                        children.extend([dataset_label, control, detail])
                root = form_page(widgets, title="Pipeline execution", description="", children=children)
                session.refresh()
                startup.display(root)
            session.shell = shell
            shell.events.register("post_run_cell", session.cell_completed)
        _ACTIVE_PIPELINE.set(session)
        atexit.register(session.close)
        session.refresh()
        if startup:
            session.startup_timings = startup.timings
        return session
    except BaseException:
        session.close(failed=True)
        raise



def build_pipeline_audit_fields(*, config=None, active_workspace_id=None, runtime_context=None):
    """Allow absent notebook audit fields only for nonpersisting Dry Run diagnostics."""
    return build_runtime_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=runtime_context,
        require_notebook_identity=persistence_permitted(runtime_context))



PROFILING_ACTIVITIES = ("standard", "grain", "frequency")


def validate_pipeline_profiling(configuration=None):
    """Validate Engineering-owned profiling settings without bool-as-int coercion."""
    result = {"profiling_enabled": True, "profiling_interval_days": 1,
              "profiling_max_rows": None, "grain_discovery_enabled": False, "frequency_enabled": False}
    if configuration is not None:
        if not isinstance(configuration, dict) or set(configuration) - set(result):
            raise ValueError("Invalid pipeline profiling configuration.")
        result.update(configuration)
    for name in ("profiling_enabled", "grain_discovery_enabled", "frequency_enabled"):
        if not isinstance(result[name], bool):
            raise ValueError(f"{name} must be a boolean.")
    for name in ("profiling_interval_days", "profiling_max_rows"):
        value = result[name]
        if name == "profiling_max_rows" and value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer" + (" or None." if name == "profiling_max_rows" else "."))
    return result


def pipeline_profiling_policy(*, context):
    """Read only the active pipeline session's independent activity configuration."""
    configuration = validate_pipeline_profiling(context["execution_plan"].evidence.get("profiling_configuration"))
    return {
        activity: {"enabled": configuration[flag], "frequency": frequency, "trigger": "read_or_write",
                   **({"days": configuration["profiling_interval_days"]} if activity == "standard" else {})}
        for activity, flag, frequency in (("standard", "profiling_enabled", "interval"),
            ("grain", "grain_discovery_enabled", "first"), ("frequency", "frequency_enabled", "first"))
    }


def profiling_due(settings, history, operation, now):
    """Use successful completion, never an attempt, to determine eligibility."""
    if operation not in {"read", "write"}:
        raise ValueError("Profiling operation must be read or write.")
    if not settings.get("enabled", True) or settings["trigger"] not in {operation, "read_or_write"}:
        return False
    last = history.get("last_success")
    if not last or settings["frequency"] == "every":
        return True
    if settings["frequency"] == "first":
        return False
    return (now - datetime.fromisoformat(last)).total_seconds() >= settings["days"] * 86400


def profiling_context_key(table_id, *, context, spark_session=None):
    """Separate physical table bindings and workspaces while retaining global Table ID."""
    config, active_workspace_id, runtime = resolve_fabric_context(context=context)
    identities = context.get("_pipeline_identities") or {}
    identity = identities.get(table_id) or resolve_catalogue_table_identity(
        config, active_workspace_id, table_id, context=runtime, spark_session=spark_session)
    physical = pipeline_physical_bindings({table_id: identity}, config=config, workspace_id=active_workspace_id)[table_id]
    descriptor = {"table_id": table_id, "workspace_id": active_workspace_id, "physical": physical}
    return _metadata_hash(descriptor), descriptor


def profiling_completion_history(table_id, *, context, spark_session=None, activity=None):
    """Aggregate confirmed physical-context completions in Spark before collecting."""
    from pyspark.sql import functions as F

    config, active_workspace_id, _runtime = resolve_fabric_context(context=context)
    key, _descriptor = profiling_context_key(table_id, context=context, spark_session=spark_session)
    def frame(table):
        return read_lakehouse_table(table, store="Metadata",
            schema=metadata_table_physical_schema(config, table),
            context={**(context or {}), "_spark_session": spark_session, "_fabricops_suppress_io_log": True}).filter(F.col("workspace_id") == active_workspace_id)
    events = (decode_metadata_dataframe("METADATA_PIPELINE_RUN", frame("METADATA_PIPELINE_RUN"))
        .filter(F.col("execution_mode").isin("ungoverned", "governed", "live"))
        .select(F.explode("profiling").alias("event"))
        .select("event.*")
        .filter((F.col("context_key") == key) & (F.col("status") == "passed")
                & F.col("results_persisted") & F.col("completed_at").isNotNull()))
    requested_limit = validate_pipeline_profiling(context["execution_plan"].evidence.get("profiling_configuration"))["profiling_max_rows"]
    # Historical scheduler completions predate bounded profiling and covered full
    # physical tables. Supplied DataFrames never establish physical coverage.
    sufficient_scope = F.col("profile_scope").isNull() | (F.col("profile_scope") == "full_table")
    if requested_limit is not None:
        sufficient_scope = sufficient_scope | ((F.col("profile_scope") == "bounded_selection")
            & (F.col("profiling_max_rows") >= requested_limit))
    events = events.filter(sufficient_scope)
    if activity is not None:
        events = events.filter(F.col("activity") == activity)
    markers = events.filter((F.col("activity") == "grain") |
        ((F.col("activity") == "frequency") & F.col("empty_result"))).select("activity", "completed_at")
    completed = markers
    for kind, table in (("standard", "METADATA_DATA_PROFILED"), ("frequency", "METADATA_DATA_PROFILED_FREQUENCY")):
        if activity is not None and activity != kind:
            continue
        snapshots = frame(table).filter(F.col("table_id") == table_id).select("profile_snapshot_id").dropDuplicates()
        matched = events.filter(F.col("activity") == kind).join(snapshots, "profile_snapshot_id", "left_semi")
        completed = completed.unionByName(matched.select("activity", "completed_at"))
    return {row["activity"]: {"last_success": row["last_success"]}
            for row in completed.groupBy("activity").agg(F.max("completed_at").alias("last_success")).collect()}


def record_profiling_outcome(outcome, *, context, spark_session=None):
    """Persist activity status without changing logical pipeline completion status."""
    plan = context["execution_plan"]
    journal = plan.evidence.setdefault("profiling", [])
    event = dict(outcome)
    journal.append(event)
    try:
        persist_pipeline_run(plan, spark_session=spark_session)
    except BaseException:
        # A later operation-exit snapshot must not publish an unconfirmed event.
        journal.remove(event)
        raise


def skip_table_profiling(table_id, operation, reason, *, context, spark_session=None):
    """Journal all activities when a target has no successful publication."""
    key, descriptor = profiling_context_key(table_id, context=context, spark_session=spark_session)
    activities = {}
    for activity in PROFILING_ACTIVITIES:
        outcome = {"status": "skipped", "reason": reason}
        record_profiling_outcome({**descriptor, **outcome, "context_key": key, "activity": activity,
            "trigger": operation, "pipeline_run_id": context["execution_plan"].plan_id,
            "executed_at": datetime.now(UTC).isoformat()}, context=context, spark_session=spark_session)
        activities[activity] = outcome
    return {"status": "skipped", "reason": reason, "activities": activities}


# Preview bounds apply to column-level aggregates, never to source profiling.
_PREVIEW_COLUMNS = 100
_CELL_CHARACTERS = 120
_METRICS = (
    ("COLUMN_NAME", "column_name", "Column", "text"),
    ("DATA_TYPE", "data_type", "Type", "text"),
    ("ROW_COUNT", "row_count", "Rows", "count"),
    ("NON_NULL_COUNT", "non_null_count", "Non-null", "count"),
    ("NULL_COUNT", "null_count", "Nulls", "count"),
    ("NULL_PERCENT", "null_percent", "Null %", "percent"),
    ("DISTINCT_COUNT", "distinct_count", "Distinct", "count"),
    ("DISTINCT_PERCENT", "distinct_percent", "Distinct % (all rows)", "percent"),
    ("MEAN", "mean_value", "Mean", "number"),
    ("STDDEV", "stddev_value", "Std. deviation", "number"),
    ("MIN_VALUE", "min_value", "Minimum", "text"),
    ("PERCENTILE_25", "percentile_25_value", "25th percentile", "number"),
    ("MEDIAN", "median_value", "Median", "number"),
    ("PERCENTILE_75", "percentile_75_value", "75th percentile", "number"),
    ("MAX_VALUE", "max_value", "Maximum", "text"),
)


def _format_value(value, kind):
    """Format a preview cell without changing the statistical result."""
    if value is None:
        return "—"
    if kind == "count":
        return f"{value:,}"
    if kind == "percent":
        return f"{value:,.2f}%"
    if kind == "number":
        return f"{value:,.4g}"
    return str(value).replace("\n", " ").replace("\r", " ").replace("\t", " ")


def capture_profile_presentation(profile, *, scope, dry_run=False, table=None):
    """Detach at most 101 compact aggregate rows while their cache is owned.

    One row per profiled column is read, with one sentinel to detect truncation.
    String projection is bounded in Spark before collection. No source rows,
    frequency values, count action, pandas conversion or metadata read is needed.
    Presentation errors never change the profiling outcome.
    """
    try:
        from pyspark.sql import functions as F

        columns = set(profile.columns)
        selected = []
        for raw, persisted, label, kind in _METRICS:
            name = raw if raw in columns else persisted
            expression = F.col(name)
            if kind == "text":
                expression = F.substring(expression.cast("string"), 1, _CELL_CHARACTERS)
            selected.append(expression.alias(label))
        rows = profile.select(*selected).limit(_PREVIEW_COLUMNS + 1).collect()
        formatted = [tuple(_format_value(row[label], kind) for _, _, label, kind in _METRICS)
                     for row in rows[:_PREVIEW_COLUMNS]]
        if scope["profile_scope"] == "bounded_selection":
            coverage = f"Bounded selection (at most {scope['profiling_max_rows']:,} rows); not the entire table"
        elif scope["profile_scope"] == "full_table":
            coverage = "Complete table"
        else:
            coverage = "Supplied DataFrame; complete-table coverage not asserted"
        title = f"Statistical profile · {coverage}"
        if table:
            title += f" · {table}"
        if dry_run:
            title += " · Dry Run (not persisted)"
        if len(rows) > _PREVIEW_COLUMNS:
            title += f" · First {_PREVIEW_COLUMNS} columns shown (presentation limit only)"
        title += f" · Text cells limited to {_CELL_CHARACTERS} characters"
        return {"title": title, "headers": [item[2] for item in _METRICS], "rows": formatted,
                "spark_session": profile.sparkSession}
    except Exception:
        return None


def display_profile_presentations(presentations):
    """Display profile previews as Fabric-native Spark tables, not ASCII tables."""
    import builtins
    import inspect

    for presentation in presentations:
        if presentation is None:
            continue
        try:
            print(presentation["title"])
            if not presentation["rows"]:
                print("No statistical profile rows.")
                continue

            from pyspark.sql.types import StringType, StructField, StructType

            schema = StructType([
                StructField(name, StringType(), False)
                for name in presentation["headers"]
            ])
            preview = presentation["spark_session"].createDataFrame(
                presentation["rows"], schema
            )
            native_display = None
            try:
                from IPython import get_ipython
                from IPython.display import display as generic_display

                shell = get_ipython()
                candidates = []
                if shell is not None:
                    candidates.append((getattr(shell, "user_ns", None) or {}).get("display"))
                    candidates.append((getattr(shell, "user_global_ns", None) or {}).get("display"))
                candidates.append(getattr(builtins, "display", None))
                # The notebook may inject display only into its calling frame.
                frame = inspect.currentframe()
                try:
                    while frame is not None:
                        candidates.append(frame.f_globals.get("display"))
                        frame = frame.f_back
                finally:
                    del frame
                native_display = next(
                    (fn for fn in candidates if callable(fn) and fn is not generic_display),
                    None,
                )
            except ImportError:
                pass

            if native_display is not None:
                try:
                    native_display(preview)
                    continue
                except Exception:
                    # The Fabric renderer may exist but be unavailable at runtime.
                    # Fall through to a bounded, notebook-readable HTML table.
                    pass

            # Portable notebook fallback: scrollable HTML, never wrapped ASCII.
            from html import escape
            from IPython.display import HTML, display as ipython_display

            headers = "".join(
                "<th style='text-align:left;padding:6px 10px;"
                "border-bottom:1px solid #bbb;white-space:nowrap'>"
                + escape(str(value)) + "</th>"
                for value in presentation["headers"]
            )
            rows = "".join(
                "<tr>" + "".join(
                    "<td style='padding:6px 10px;border-bottom:1px solid #eee;"
                    "white-space:nowrap'>" + escape(str(value)) + "</td>"
                    for value in row
                ) + "</tr>"
                for row in presentation["rows"]
            )
            ipython_display(HTML(
                "<div style='max-width:100%;overflow-x:auto'>"
                "<table style='border-collapse:collapse;font-size:13px'>"
                f"<thead><tr>{headers}</tr></thead><tbody>{rows}</tbody>"
                "</table></div>"
            ))
        except Exception as exc:
            # Rendering must not invalidate a successful Read or Write.
            try:
                print(f"Statistical profile display unavailable: {type(exc).__name__}: {exc}")
            except Exception:
                pass


def schedule_table_profiling(table_id, operation, *, context, spark_session=None, dataframe=None, verbose=False, presentations=None):
    """Profile due work using successful completion history as the schedule."""
    if operation not in {"read", "write"}:
        raise ValueError("Profiling operation must be read or write.")
    configuration = validate_pipeline_profiling(context["execution_plan"].evidence.get("profiling_configuration"))
    max_rows = configuration["profiling_max_rows"]
    scope = "bounded_selection" if max_rows is not None else ("supplied_dataframe" if dataframe is not None and operation == "write" and not persistence_permitted(context) else "full_table")
    profile_scope = {"profile_scope": scope, "profiling_max_rows": max_rows}
    scope_message = (f"bounded selection of at most {max_rows} rows; physical reads may exceed the limit."
        if max_rows is not None else "prepared Dry Run DataFrame; no physical target publication or complete-table coverage asserted."
        if scope == "supplied_dataframe" else "complete physical table when due; may scan all physical source rows, including rows outside the SQL query.")
    scope_reported = False
    outcomes = {}
    if not persistence_permitted(context):
        # Dry Run can inspect due work, but never consumes successful intervals.
        policy = pipeline_profiling_policy(context=context)
        history = profiling_completion_history(table_id, context=context, spark_session=spark_session)
        key, descriptor = profiling_context_key(table_id, context=context, spark_session=spark_session)
        due = {activity for activity in PROFILING_ACTIVITIES
               if profiling_due(policy[activity], history.get(activity, {}), operation, datetime.now(UTC))}
        if due and verbose:
            print("Profiling scope → " + scope_message)
        profile = (execute_table_profile(table_id=table_id, dataframe=dataframe,
            context={**context, "_profile_trigger": operation, "_profile_scope": profile_scope}, spark_session=spark_session,
            verbose=False, activities=due, presentations=presentations) if due else {})
        for activity in PROFILING_ACTIVITIES:
            if activity in due:
                outcomes[activity] = dict(profile)
                if activity != "frequency" and "frequency_profile" in profile:
                    outcomes[activity]["frequency_profile"] = None
                if activity != "grain" and "grain_candidates" in profile:
                    outcomes[activity]["grain_candidates"] = []
                diagnostic = {"status": "passed", "results_persisted": False, "reason": "read_only_diagnostic",
                              **profile_scope, "row_count": profile.get("row_count")}
            else:
                outcomes[activity] = {"status": "skipped", "reason": "Not due for this operation"}
                diagnostic = outcomes[activity]
            record_profiling_outcome({**descriptor, **diagnostic, "context_key": key, "activity": activity,
                "trigger": operation, "pipeline_run_id": context["execution_plan"].plan_id,
                "executed_at": datetime.now(UTC).isoformat()}, context=context, spark_session=spark_session)
        return {**profile, "status": "passed", "activities": outcomes, "persistence_status": "disabled",
                "row_count": profile.get("row_count") if scope != "bounded_selection" else None, **profile_scope,
                "profiled_row_count": profile.get("row_count")}
    key, descriptor = profiling_context_key(table_id, context=context, spark_session=spark_session)
    policy = pipeline_profiling_policy(context=context)
    for activity in PROFILING_ACTIVITIES:
        base = {**descriptor, "context_key": key, "activity": activity, "trigger": operation,
                "pipeline_run_id": context["execution_plan"].plan_id, "executed_at": datetime.now(UTC).isoformat()}
        settings = policy[activity]
        if not settings.get("enabled", True) or settings["trigger"] not in {operation, "read_or_write"}:
            skipped = {"status": "skipped", "reason": "disabled"}
            outcomes[activity] = skipped
            record_profiling_outcome({**base, **skipped}, context=context, spark_session=spark_session)
            continue
        history = profiling_completion_history(
            table_id, context=context, spark_session=spark_session, activity=activity)
        if not profiling_due(settings, history.get(activity, {}), operation, datetime.now(UTC)):
            skipped = {"status": "skipped", "reason": (
                "already_completed" if settings["frequency"] == "first" else "interval_not_elapsed")}
            outcomes[activity] = skipped
            record_profiling_outcome({**base, **skipped}, context=context, spark_session=spark_session)
            continue
        if verbose and not scope_reported:
            print("Profiling scope → " + scope_message)
            scope_reported = True
        profile_snapshot_id = str(uuid4())
        outcome = None
        completion_recorded = False
        try:
            record_profiling_outcome({**base, "status": "running", "profile_snapshot_id": profile_snapshot_id,
                "results_persisted": False}, context=context, spark_session=spark_session)
            profile_context = {**context, "activity_id": profile_snapshot_id,
                               "_profile_snapshot_id": profile_snapshot_id, "_profile_scope": profile_scope}
            outcome = execute_table_profile(table_id=table_id, dataframe=dataframe, context=profile_context,
                spark_session=spark_session, verbose=False, activities={activity}, presentations=presentations)
            completed_at = datetime.now(UTC).isoformat()
            outcomes[activity] = {"status": "passed", "profile_snapshot_id": profile_snapshot_id if activity != "grain" and not outcome.get("empty_result") else None,
                                  "row_count": outcome.get("row_count"), **profile_scope, "results_persisted": True,
                                  "empty_result": outcome.get("empty_result", False),
                                  "completed_at": completed_at}
            record_profiling_outcome({**base, **outcomes[activity]}, context=context, spark_session=spark_session)
            completion_recorded = True
        except BaseException as exc:
            # Retain the attempted/failed activity even when orchestration raises.
            if not completion_recorded and not context["execution_plan"].evidence.get("persistence_failed"):
                record_profiling_outcome({**base, "status": "failed", "reason": type(exc).__name__,
                    "profile_snapshot_id": profile_snapshot_id if activity != "grain" else None,
                    "results_persisted": True if outcome is not None else None}, context=context, spark_session=spark_session)
            raise
        finally:
            profile = outcome.get("profile") if outcome is not None else None
            if profile is not None and hasattr(profile, "unpersist"):
                profile.unpersist()
    counts = [outcome.get("row_count") for outcome in outcomes.values() if outcome.get("row_count") is not None]
    return {"status": "passed", "activities": outcomes, "row_count": counts[0] if counts and scope == "full_table" else None, **profile_scope,
            "profiled_row_count": counts[0] if counts else None}


# Persisted-table profiling implementation shared by standalone and scheduled calls.
import math
from itertools import combinations
from typing import Sequence
from uuid import NAMESPACE_URL, uuid5


PROFILED_FREQUENCY_TABLE = "METADATA_DATA_PROFILED_FREQUENCY"


PROFILED_COLUMNS = metadata_table_schema_registry()[PROFILED_TABLE].fieldNames()


PROFILED_FREQUENCY_COLUMNS = metadata_table_schema_registry()[PROFILED_FREQUENCY_TABLE].fieldNames()


CATALOGUE_COLUMNS = metadata_table_schema_registry()[CATALOGUE_TABLE].fieldNames()


LOAD_STRATEGIES = {"overwrite", "append_all", "append_new_only", "scd1", "scd2"}


_PROFILE_EXCLUDED_NAMES = {
    "_pipeline_run_id", "_pipeline_name", "_pipeline_workspace_id", "_source_table",
    "_record_loaded_timestamp", "_notebook_name", "_loaded_by", "_dq_check_status",
    "_dq_failed_rules", "_source_system", "_source_extract_timestamp", "_watermark_value",
    "_sample_bucket", "_row_ingest_id", "_business_key_hash",
    "_row_hash", "pipeline_ts", "ingested_at_utc", "notebook_name", "loaded_by",
    "p_bucket", "sample_bucket", "row_ingest_id", "ingest_run_id", "pipeline_run_id",
    "loaded_at", "run_ingest_id", "_fabricops_run_id", "_fabricops_pipeline_name",
    "_fabricops_created_at", "_activity_id", "_committed_at", "_committed_by",
    "_notebook_id", "_workspace_id", "_workspace_name", "_metadata_lakehouse_name",
}


_PROFILE_EXCLUDED_PREFIXES = ("_fabricops_", "_dq_")


_KEY_CANDIDATE_MAX_SIZE = 3


_KEY_CANDIDATE_MAX_RESULTS = 8


_WAREHOUSE_NUMERIC_TYPES = {
    "bigint", "decimal", "float", "int", "money", "numeric", "real",
    "smallint", "smallmoney", "tinyint",
}


_WAREHOUSE_MIN_MAX_TYPES = _WAREHOUSE_NUMERIC_TYPES | {
    "char", "date", "datetime", "datetime2", "datetimeoffset", "nchar",
    "nvarchar", "smalldatetime", "time", "varchar",
}


_WAREHOUSE_NON_SCALAR_TYPES = {"binary", "image", "varbinary", "xml"}


def _sql_identifier(value: str) -> str:
    """Quote one resolved SQL Server identifier."""
    return f"[{str(value).replace(']', ']]')}]"


def _sql_string(value: str) -> str:
    """Quote one internal SQL string literal."""
    return "N'" + str(value).replace("'", "''") + "'"


def _warehouse_type_name(row: Mapping[str, Any]) -> str:
    """Return the canonical PySpark type name for Warehouse metadata.

    Warehouse profiling may calculate statistics with SQL pushdown, but FabricOps
    stores schema metadata in the same type vocabulary produced by PySpark
    DataFrame schemas because downstream schema and Guardrail checks run in
    PySpark.
    """
    name = str(row["DATA_TYPE"]).lower()
    if name in {"decimal", "numeric", "money", "smallmoney"}:
        return f"decimal({int(row['NUMERIC_PRECISION'])},{int(row['NUMERIC_SCALE'])})"
    return {
        "bigint": "bigint",
        "binary": "binary",
        "bit": "boolean",
        "char": "string",
        "date": "date",
        "datetime": "timestamp",
        "datetime2": "timestamp",
        "datetimeoffset": "timestamp",
        "float": "double",
        "image": "binary",
        "int": "int",
        "nchar": "string",
        "nvarchar": "string",
        "real": "float",
        "smalldatetime": "timestamp",
        "smallint": "smallint",
        "time": "string",
        "tinyint": "smallint",
        "uniqueidentifier": "binary",
        "varbinary": "binary",
        "varchar": "string",
        "xml": "string",
    }.get(name, "string")


def _warehouse_columns(identity: Mapping[str, Any], *, spark_session: Any, context: dict[str, Any]):
    """Read Warehouse columns and normalize their types to PySpark names."""
    schema = _sql_string(str(identity["schema"]))
    table = _sql_string(str(identity["table_name"]))
    query = (
        "SELECT COLUMN_NAME, DATA_TYPE, NUMERIC_PRECISION, NUMERIC_SCALE "
        "FROM INFORMATION_SCHEMA.COLUMNS "
        f"WHERE TABLE_SCHEMA = {schema} AND TABLE_NAME = {table}"
    )
    rows = []
    for row in read_warehouse_query(
        query, store=str(identity["store"]), context={**(context or {}), "_spark_session": spark_session}
    ).collect():
        value = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        normalized = {str(key).upper(): item for key, item in value.items()}
        rows.append((str(normalized["COLUMN_NAME"]), _warehouse_type_name(normalized), str(normalized["DATA_TYPE"]).lower()))
    return rows


def _warehouse_statistical_query(identity: Mapping[str, Any], columns: Sequence[tuple[str, str, str]]) -> str:
    """Build one wide aggregate pass for exact Warehouse statistics."""
    source = f"{_sql_identifier(str(identity['schema']))}.{_sql_identifier(str(identity['table_name']))}"
    expressions = ["COUNT_BIG(*) AS ROW_COUNT"]
    for index, (name, _canonical_type, sql_type) in enumerate(columns):
        column = _sql_identifier(name)
        numeric = sql_type in _WAREHOUSE_NUMERIC_TYPES
        min_max = sql_type in _WAREHOUSE_MIN_MAX_TYPES
        prefix = f"C{index}"
        expressions.extend(
            [
                f"COUNT_BIG({column}) AS {prefix}_NON_NULL_COUNT",
                f"COUNT_BIG(DISTINCT {column}) AS {prefix}_DISTINCT_COUNT",
                (
                    f"AVG(CONVERT(float, {column})) AS {prefix}_MEAN"
                    if numeric else f"CAST(NULL AS float) AS {prefix}_MEAN"
                ),
                (
                    f"STDEV(CONVERT(float, {column})) AS {prefix}_STDDEV"
                    if numeric else f"CAST(NULL AS float) AS {prefix}_STDDEV"
                ),
                (
                    f"CONVERT(varchar(max), MIN({column})) AS {prefix}_MIN_VALUE"
                    if min_max else f"CAST(NULL AS varchar(max)) AS {prefix}_MIN_VALUE"
                ),
                (
                    f"CONVERT(varchar(max), MAX({column})) AS {prefix}_MAX_VALUE"
                    if min_max else f"CAST(NULL AS varchar(max)) AS {prefix}_MAX_VALUE"
                ),
            ]
        )
    return "SELECT\n  " + ",\n  ".join(expressions) + f"\nFROM {source}"


def _warehouse_percentile_query(identity: Mapping[str, Any], *, column_name: str, prefix: str) -> str:
    """Build one compact exact percentile query for one Warehouse numeric column."""
    source = f"{_sql_identifier(str(identity['schema']))}.{_sql_identifier(str(identity['table_name']))}"
    column = _sql_identifier(column_name)
    return (
        "SELECT TOP (1)\n"
        f"  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY CONVERT(float, {column})) OVER () AS {prefix}_P25,\n"
        f"  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CONVERT(float, {column})) OVER () AS {prefix}_P50,\n"
        f"  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY CONVERT(float, {column})) OVER () AS {prefix}_P75\n"
        f"FROM {source}"
    )


def _warehouse_statistical_dataframe(
    wide_frame: Any, columns, *, spark_session: Any, percentile_values: Mapping[str, Any] | None = None, metrics=None
):
    """Reshape compact Warehouse aggregates and percentiles into canonical profile rows."""
    from pyspark.sql import types as T

    collected = wide_frame.collect()
    if len(collected) != 1:
        raise RuntimeError("Warehouse statistical profiling must return exactly one compact aggregate row.")
    raw = collected[0].asDict(recursive=True) if hasattr(collected[0], "asDict") else dict(collected[0])
    values = {str(key).upper(): value for key, value in raw.items()}
    if percentile_values:
        values.update({str(key).upper(): value for key, value in percentile_values.items()})
    row_count = int(values.get("ROW_COUNT") or 0)
    if metrics is not None:
        metrics["row_count"] = row_count

    def percent(numerator: int) -> float:
        return 0.0 if row_count == 0 else round((numerator / row_count) * 100.0, 3)

    rows = []
    for index, (name, canonical_type, sql_type) in enumerate(columns):
        prefix = f"C{index}"
        non_null_count = int(values.get(f"{prefix}_NON_NULL_COUNT") or 0)
        distinct_count = int(values.get(f"{prefix}_DISTINCT_COUNT") or 0)
        numeric = sql_type in _WAREHOUSE_NUMERIC_TYPES
        rows.append(
            (
                name, canonical_type, row_count, non_null_count, row_count - non_null_count,
                percent(row_count - non_null_count), distinct_count, percent(distinct_count),
                values.get(f"{prefix}_MEAN") if numeric else None,
                values.get(f"{prefix}_STDDEV") if numeric else None,
                values.get(f"{prefix}_MIN_VALUE"), values.get(f"{prefix}_P25") if numeric else None,
                values.get(f"{prefix}_P50") if numeric else None,
                values.get(f"{prefix}_P75") if numeric else None, values.get(f"{prefix}_MAX_VALUE"),
            )
        )
    schema = T.StructType(
        [
            T.StructField("COLUMN_NAME", T.StringType(), False), T.StructField("DATA_TYPE", T.StringType(), False),
            T.StructField("ROW_COUNT", T.LongType(), False), T.StructField("NON_NULL_COUNT", T.LongType(), False),
            T.StructField("NULL_COUNT", T.LongType(), False), T.StructField("NULL_PERCENT", T.DoubleType(), False),
            T.StructField("DISTINCT_COUNT", T.LongType(), False), T.StructField("DISTINCT_PERCENT", T.DoubleType(), False),
            T.StructField("MEAN", T.DoubleType(), True), T.StructField("STDDEV", T.DoubleType(), True),
            T.StructField("MIN_VALUE", T.StringType(), True), T.StructField("PERCENTILE_25", T.DoubleType(), True),
            T.StructField("MEDIAN", T.DoubleType(), True), T.StructField("PERCENTILE_75", T.DoubleType(), True),
            T.StructField("MAX_VALUE", T.StringType(), True),
        ]
    )
    return spark_session.createDataFrame(rows, schema=schema)


def _warehouse_frequency_query(
    identity: Mapping[str, Any], columns: Sequence[tuple[str, str, str]], *, top_n: int | None
) -> str:
    """Build Warehouse-native exact frequency queries with per-column ranking."""
    source = f"{_sql_identifier(str(identity['schema']))}.{_sql_identifier(str(identity['table_name']))}"
    branches = []
    for name, canonical_type, _sql_type in columns:
        column = _sql_identifier(name)
        limit = f"WHERE FREQUENCY_RANK <= {int(top_n)}" if top_n is not None else ""
        branches.append(
            "SELECT COLUMN_NAME, DATA_TYPE, VALUE, FREQUENCY_COUNT, FREQUENCY_PERCENT, FREQUENCY_RANK, "
            f"PROFILED_ROW_COUNT, PROFILED_NON_NULL_COUNT FROM (SELECT {_sql_string(name)} AS COLUMN_NAME, "
            f"{_sql_string(canonical_type)} AS DATA_TYPE, CONVERT(varchar(max), {column}) AS VALUE, COUNT_BIG(*) AS FREQUENCY_COUNT, "
            f"CAST(ROUND(100.0 * COUNT_BIG(*) / NULLIF(SUM(COUNT_BIG(*)) OVER (), 0), 3) AS float) AS FREQUENCY_PERCENT, "
            f"ROW_NUMBER() OVER (ORDER BY COUNT_BIG(*) DESC, CASE WHEN {column} IS NULL THEN 0 ELSE 1 END, CONVERT(varchar(max), {column})) AS FREQUENCY_RANK, "
            f"SUM(COUNT_BIG(*)) OVER () AS PROFILED_ROW_COUNT, SUM(COUNT_BIG({column})) OVER () AS PROFILED_NON_NULL_COUNT "
            f"FROM {source} GROUP BY {column}) AS ranked {limit}"
        )
    return "\nUNION ALL\n".join(branches)


def _warehouse_profile_dataframes(identity, *, spark_session, context, frequency_columns, threshold_percent, top_n, metrics=None):
    """Calculate compact canonical profile outputs in Fabric Warehouse."""
    from fabricops_kit.pipeline.shared import FREQUENCY_PROFILE_COLUMNS, PROFILE_DATAFRAME_COLUMNS

    io_context = {**(context or {}), "_fabricops_suppress_io_log": True}
    all_columns = _warehouse_columns(identity, spark_session=spark_session, context=io_context)
    profile_columns = [
        column for column in all_columns
        if column[0] not in _PROFILE_EXCLUDED_NAMES
        and not any(column[0].startswith(prefix) for prefix in _PROFILE_EXCLUDED_PREFIXES)
    ]
    if not profile_columns:
        raise ValueError("No eligible non-technical columns found for metadata profiling.")
    wide_profile = read_warehouse_query(
        _warehouse_statistical_query(identity, profile_columns),
        store=str(identity["store"]), context={**(io_context or {}), "_spark_session": spark_session},
    )
    percentile_values = {}
    for index, (name, _canonical_type, sql_type) in enumerate(profile_columns):
        if sql_type not in _WAREHOUSE_NUMERIC_TYPES:
            continue
        percentile_rows = read_warehouse_query(
            _warehouse_percentile_query(identity, column_name=name, prefix=f"C{index}"),
            store=str(identity["store"]), context={**(io_context or {}), "_spark_session": spark_session},
        ).collect()
        if percentile_rows:
            row = percentile_rows[0]
            values = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
            percentile_values.update(values)
    profile = _warehouse_statistical_dataframe(
        wide_profile,
        profile_columns,
        spark_session=spark_session,
        percentile_values=percentile_values,
        metrics=metrics,
    ).select(*PROFILE_DATAFRAME_COLUMNS)
    if frequency_columns is None:
        scalar = {name for name, _canonical, sql_type in profile_columns if sql_type not in _WAREHOUSE_NON_SCALAR_TYPES}
        selected = _automatic_frequency_columns(
            profile, scalar_columns=list(scalar), threshold_percent=threshold_percent
        )
    else:
        selected = list(frequency_columns)
        available = {name for name, _canonical, _sql_type in all_columns}
        missing = [name for name in selected if name not in available]
        if missing:
            raise ValueError(f"Requested columns do not exist: {', '.join(missing)}")
    frequency = None
    if selected:
        selected_set = set(selected)
        selected_metadata = [column for column in all_columns if column[0] in selected_set]
        frequency = read_warehouse_query(
            _warehouse_frequency_query(identity, selected_metadata, top_n=top_n),
            store=str(identity["store"]), context={**(io_context or {}), "_spark_session": spark_session},
        ).select(*FREQUENCY_PROFILE_COLUMNS)
    return profile, frequency, all_columns


def _key_candidate_evidence(
    candidates: Sequence[Mapping[str, Any]], *, evaluated: bool = True,
    max_columns: int = _KEY_CANDIDATE_MAX_SIZE, scope=None
) -> dict[str, Any]:
    """Return one explicit table-level key-discovery evidence envelope."""
    values = [dict(candidate) for candidate in candidates]
    return {
        "status": "resolved" if values else ("unresolved" if evaluated else "not_evaluated"),
        "max_combination_width": max_columns if evaluated else 0,
        "candidates": values,
        **(scope or {}),
    }


def _key_candidate_payload(columns: Sequence[str], *, row_count: int) -> dict[str, Any]:
    """Return one deterministic proven key-candidate evidence record."""
    return {
        "columns": [str(column) for column in columns],
        "column_count": len(columns),
        "row_count": int(row_count),
        "distinct_count": int(row_count),
        "uniqueness_percent": 100.0,
        "null_count": 0,
    }


def _spark_profile_key_candidates(
    dataframe: Any, statistical_profile: Any, *, metrics=None,
    max_columns: int = _KEY_CANDIDATE_MAX_SIZE, max_candidates: int = _KEY_CANDIDATE_MAX_RESULTS
) -> list[dict[str, Any]]:
    """Discover the smallest null-free unique keys from all scalar Spark columns."""
    del statistical_profile
    from pyspark.sql import functions as F
    from pyspark.sql.types import ArrayType, MapType, StructType

    fields = [
        field for field in dataframe.schema.fields
        if not isinstance(field.dataType, ArrayType | MapType | StructType)
    ]
    if not fields:
        return []

    expressions = [F.count(F.lit(1)).cast("long").alias("__ROW_COUNT")]
    for index, field in enumerate(fields):
        column = F.col(f"`{field.name.replace('`', '``')}`")
        expressions.extend([
            F.count(column).cast("long").alias(f"C{index}_NON_NULL_COUNT"),
            F.count_distinct(column).cast("long").alias(f"C{index}_DISTINCT_COUNT"),
        ])
    values = dataframe.agg(*expressions).first()
    if values is None:
        return []
    row_count = int(values["__ROW_COUNT"] or 0)
    if metrics is not None:
        metrics["row_count"] = row_count
    if row_count <= 0:
        return []

    rows = [
        {
            "column_name": field.name,
            "row_count": row_count,
            "distinct_count": int(values[f"C{index}_DISTINCT_COUNT"] or 0),
        }
        for index, field in enumerate(fields)
        if int(values[f"C{index}_NON_NULL_COUNT"] or 0) == row_count
    ]
    rows.sort(
        key=lambda item: (
            -int(item["distinct_count"]),
            str(item["column_name"]).casefold(),
        )
    )
    singles = [
        _key_candidate_payload([row["column_name"]], row_count=row_count)
        for row in rows
        if int(row["distinct_count"]) == row_count
    ]
    if singles:
        return singles[:max_candidates]

    candidate_columns = [str(row["column_name"]) for row in rows]
    for size in range(2, min(max_columns, len(candidate_columns)) + 1):
        matches = []
        for columns in combinations(candidate_columns, size):
            if int(dataframe.select(*columns).dropDuplicates().count()) == row_count:
                matches.append(_key_candidate_payload(columns, row_count=row_count))
                if len(matches) >= max_candidates:
                    break
        if matches:
            return matches
    return []


def _warehouse_profile_key_candidates(
    identity: Mapping[str, Any],
    statistical_profile: Any,
    *,
    spark_session: Any,
    context: dict[str, Any],
    warehouse_columns: Sequence[tuple[str, str, str]] | None = None,
    max_columns: int = _KEY_CANDIDATE_MAX_SIZE,
    max_candidates: int = _KEY_CANDIDATE_MAX_RESULTS,
) -> list[dict[str, Any]]:
    """Discover the smallest null-free unique keys from all scalar Warehouse columns."""
    del statistical_profile
    discovered_columns = (
        list(warehouse_columns)
        if warehouse_columns is not None
        else _warehouse_columns(
            identity,
            spark_session=spark_session,
            context={**(context or {}), "_fabricops_suppress_io_log": True},
        )
    )
    all_columns = [
        column for column in discovered_columns
        if column[2] not in _WAREHOUSE_NON_SCALAR_TYPES
    ]
    if not all_columns:
        return []

    source = (
        f"{_sql_identifier(str(identity['schema']))}."
        f"{_sql_identifier(str(identity['table_name']))}"
    )
    expressions = ["COUNT_BIG(*) AS ROW_COUNT"]
    for index, (name, _canonical_type, _sql_type) in enumerate(all_columns):
        column = _sql_identifier(name)
        expressions.extend([
            f"COUNT_BIG({column}) AS C{index}_NON_NULL_COUNT",
            f"COUNT_BIG(DISTINCT {column}) AS C{index}_DISTINCT_COUNT",
        ])
    evidence_query = "SELECT " + ", ".join(expressions) + f" FROM {source}"
    io_context = {**(context or {}), "_fabricops_suppress_io_log": True}
    values = read_warehouse_query(
        evidence_query,
        store=str(identity["store"]),
        context={**(io_context or {}), "_spark_session": spark_session},
    ).collect()
    if not values:
        return []
    mapped = (
        values[0].asDict(recursive=True)
        if hasattr(values[0], "asDict")
        else dict(values[0])
    )
    normalized = {str(key).upper(): value for key, value in mapped.items()}
    row_count = int(normalized.get("ROW_COUNT") or 0)
    if row_count <= 0:
        return []

    rows = [
        {
            "column_name": name,
            "row_count": row_count,
            "distinct_count": int(normalized.get(f"C{index}_DISTINCT_COUNT") or 0),
        }
        for index, (name, _canonical_type, _sql_type) in enumerate(all_columns)
        if int(normalized.get(f"C{index}_NON_NULL_COUNT") or 0) == row_count
    ]
    rows.sort(
        key=lambda item: (
            -int(item["distinct_count"]),
            str(item["column_name"]).casefold(),
        )
    )
    singles = [
        _key_candidate_payload([row["column_name"]], row_count=row_count)
        for row in rows
        if int(row["distinct_count"]) == row_count
    ]
    if singles:
        return singles[:max_candidates]

    candidate_columns = [str(row["column_name"]) for row in rows]
    for size in range(2, min(max_columns, len(candidate_columns)) + 1):
        matches = []
        for columns in combinations(candidate_columns, size):
            projected = ", ".join(_sql_identifier(column) for column in columns)
            query = (
                "SELECT COUNT_BIG(*) AS DISTINCT_COUNT FROM "
                f"(SELECT DISTINCT {projected} FROM {source}) AS fabricops_key_candidate"
            )
            values = read_warehouse_query(
                query,
                store=str(identity["store"]),
                context={**(io_context or {}), "_spark_session": spark_session},
            ).collect()
            if values:
                value = values[0]
                mapped = value.asDict(recursive=True) if hasattr(value, "asDict") else dict(value)
                distinct_count = int(
                    next(
                        (item for key, item in mapped.items() if str(key).upper() == "DISTINCT_COUNT"),
                        0,
                    ) or 0
                )
                if distinct_count == row_count:
                    matches.append(_key_candidate_payload(columns, row_count=row_count))
                    if len(matches) >= max_candidates:
                        break
        if matches:
            return matches
    return []


def _require_non_empty_string(value: Any, name: str) -> str:
    """Return a stripped required string or raise a clear validation error."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value.strip()


def _normalize_choice(value: Any, name: str, allowed: set[str]) -> str:
    """Return a normalized allowed choice or raise a clear validation error."""
    normalized = _require_non_empty_string(value, name).lower()
    if normalized not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {choices}.")
    return normalized


def _processing_definition(
    profile_role: str,
    load_strategy: Any,
    load_strategy_parameters: Any,
) -> tuple[str | None, str | None]:
    """Validate and canonically serialize one table-owned processing definition."""
    supplied = load_strategy is not None or load_strategy_parameters is not None
    if profile_role == "source":
        if supplied:
            raise ValueError("Source registration does not accept target processing arguments.")
        return None, None
    if load_strategy is None:
        if load_strategy_parameters is not None:
            raise ValueError("load_strategy is required when load_strategy_parameters is supplied.")
        return None, None
    strategy = _normalize_choice(load_strategy, "load_strategy", LOAD_STRATEGIES)
    if load_strategy_parameters is None:
        parameters: dict[str, Any] = {}
    elif not isinstance(load_strategy_parameters, dict):
        raise ValueError("load_strategy_parameters must be a mapping when supplied.")
    else:
        parameters = dict(load_strategy_parameters)
    allowed = {
        "overwrite": {"watermark_column"},
        "append_all": {"watermark_column"},
        "append_new_only": {"watermark_column"},
        "scd1": {"key_columns", "watermark_column"},
        "scd2": {"key_columns", "effective_column", "tracked_columns", "watermark_column"},
    }[strategy]
    unexpected = sorted(set(parameters) - allowed)
    if unexpected:
        raise ValueError(f"{strategy} does not accept processing parameters: {', '.join(unexpected)}.")
    for name in ("key_columns", "tracked_columns"):
        if name in parameters:
            values = parameters[name]
            if not isinstance(values, (list, tuple)) or not values:
                raise ValueError(f"{name} must be a non-empty sequence of column names.")
            parameters[name] = [_require_non_empty_string(value, name) for value in values]
    for name in ("effective_column", "watermark_column"):
        if name in parameters:
            parameters[name] = _require_non_empty_string(parameters[name], name)
    if strategy in {"scd1", "scd2"} and "key_columns" not in parameters:
        raise ValueError(f"{strategy} requires key_columns.")
    if strategy == "scd2" and "effective_column" not in parameters:
        raise ValueError("scd2 requires effective_column.")
    return strategy, json.dumps(parameters, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate_processing_columns(df: Any, parameters_json: str | None) -> None:
    """Require every authored processing column name to exist in the target schema."""
    if parameters_json is None:
        return
    parameters = json.loads(parameters_json)
    available = {str(field.name) for field in df.schema.fields}
    referenced = []
    for name in ("effective_column", "watermark_column"):
        if parameters.get(name):
            referenced.append(str(parameters[name]))
    for name in ("key_columns", "tracked_columns"):
        referenced.extend(str(value) for value in parameters.get(name, []))
    missing = sorted(set(referenced) - available)
    if missing:
        raise ValueError(f"Processing definition references columns not present in df: {', '.join(missing)}.")


def _validate_resolved_identity(table: Any, *, config: Any, active_workspace_id: str) -> dict[str, str | None]:
    """Validate a caller-supplied identity against the active Fabric config."""
    if not isinstance(table, Mapping):
        raise ValueError("table must be a canonical table identity mapping.")
    required = {"table_id", "store", "schema", "table_name", "store_kind"}
    missing = sorted(required - set(table))
    if missing:
        raise ValueError(f"table identity is missing required fields: {', '.join(missing)}.")
    resolved = resolve_physical_table_identity(
        config,
        active_workspace_id,
        store=table["store"],
        schema=table["schema"],
        table_name=table["table_name"],
    )
    supplied = {name: table[name] for name in required}
    if supplied != resolved:
        raise ValueError(
            "table identity is inconsistent with the canonical identity resolved from the active Fabric config."
        )
    return resolved


def _validate_frequency_profile_dataframe(source_df, frequency_profile_df, selected_columns: Sequence[str]):
    """Return the frequency DataFrame after validating caller-provided scope."""
    if frequency_profile_df is None:
        return source_df, "full_source"
    source_session = getattr(source_df, "sparkSession", None)
    frequency_session = getattr(frequency_profile_df, "sparkSession", None)
    if source_session is not None and frequency_session is not None and source_session is not frequency_session:
        raise ValueError("frequency_profile_df must use the same Spark session as df.")
    fields = getattr(getattr(frequency_profile_df, "schema", None), "fields", None)
    if fields is None:
        raise ValueError("frequency_profile_df must be a Spark DataFrame-like object with a schema.")
    available_columns = {field.name for field in fields}
    missing_columns = [column for column in selected_columns if column not in available_columns]
    if missing_columns:
        raise ValueError(f"frequency_profile_df is missing selected frequency columns: {', '.join(missing_columns)}")
    return frequency_profile_df, "caller_provided"


def _scalar_frequency_columns(df, candidate_columns: Sequence[str]) -> list[str]:
    """Return candidate columns whose Spark types are scalar frequency types."""
    from pyspark.sql.types import ArrayType, BinaryType, MapType, StructType

    fields = {field.name: field for field in df.schema.fields}
    return [
        name
        for name in candidate_columns
        if name in fields and not isinstance(fields[name].dataType, ArrayType | MapType | StructType | BinaryType)
    ]


def _automatic_frequency_columns(
    profile_df, *, scalar_columns: Sequence[str], threshold_percent: float | None
) -> list[str]:
    """Return automatic scalar columns that pass the frequency cardinality guard."""
    from pyspark.sql import functions as F

    non_null_count = F.col("NON_NULL_COUNT").cast("double")
    distinct_count = F.col("DISTINCT_COUNT").cast("double")
    raw_cardinality_percent = (distinct_count / non_null_count) * 100
    eligible = profile_df.where(F.col("COLUMN_NAME").isin(list(scalar_columns))).where(
        F.col("NON_NULL_COUNT").cast("long") > 0
    )
    if threshold_percent is not None:
        eligible = eligible.where(raw_cardinality_percent <= F.lit(float(threshold_percent)))
    return [row.COLUMN_NAME for row in eligible.select("COLUMN_NAME").collect()]


def _selected_frequency_columns(
    source_df, profile_df, frequency_columns: Sequence[str] | None, threshold_percent: float | None
) -> list[str]:
    """Return explicitly requested or automatically eligible frequency columns."""
    if frequency_columns is not None:
        return list(frequency_columns)
    profiled_columns = [row.COLUMN_NAME for row in profile_df.select("COLUMN_NAME").collect()]
    scalar_columns = _scalar_frequency_columns(source_df, profiled_columns)
    return _automatic_frequency_columns(profile_df, scalar_columns=scalar_columns, threshold_percent=threshold_percent)


def _audit_literal_columns(*, config: Any, active_workspace_id: str, runtime_context: dict[str, Any]) -> dict[str, Any]:
    """Return Spark literals for the canonical runtime audit field set."""
    from pyspark.sql import functions as F

    audit = build_runtime_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=runtime_context)
    return {
        "_committed_by": F.lit(audit["_committed_by"]).cast("string"),
        "_committed_at": F.lit(audit["_committed_at"]).cast("timestamp_ltz"),
        "_workspace_id": F.lit(audit["_workspace_id"]).cast("string"),
        "_workspace_name": F.lit(audit["_workspace_name"]).cast("string"),
        "_notebook_id": F.lit(audit["_notebook_id"]).cast("string"),
        "_notebook_name": F.lit(audit["_notebook_name"]).cast("string"),
        "_metadata_lakehouse_name": F.lit(audit["_metadata_lakehouse_name"]).cast("string"),
        "_activity_id": F.lit(audit["_activity_id"]).cast("string"),
    }


def _canonical_profiled_dataframe(
    profile_df,
    *,
    config: Any,
    active_workspace_id: str,
    runtime_context: dict[str, Any],
    workspace_id: str,
    table_id: str,
    profile_snapshot_id: str,
):
    """Map statistical profiler output to the normalized Profile schema."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    column_id_udf = F.udf(lambda column_name: build_column_id(table_id, column_name), T.StringType())
    profile_id_udf = F.udf(
        lambda column_name: str(uuid5(NAMESPACE_URL, f"{profile_snapshot_id}|{build_column_id(table_id, column_name)}")),
        T.StringType(),
    )
    audit_columns = _audit_literal_columns(config=config, active_workspace_id=active_workspace_id, runtime_context=runtime_context)
    base = profile_df.select(
        F.col("COLUMN_NAME").alias("_column_name"),
        F.col("DATA_TYPE").alias("data_type"),
        F.col("ROW_COUNT").cast("long").alias("row_count"),
        F.col("NON_NULL_COUNT").cast("long").alias("non_null_count"),
        F.col("NULL_COUNT").cast("long").alias("null_count"),
        F.col("NULL_PERCENT").cast("double").alias("null_percent"),
        F.col("DISTINCT_COUNT").cast("long").alias("distinct_count"),
        F.col("DISTINCT_PERCENT").cast("double").alias("distinct_percent"),
        F.col("MEAN").cast("double").alias("mean_value"),
        F.col("STDDEV").cast("double").alias("stddev_value"),
        F.col("MIN_VALUE").cast("string").alias("min_value"),
        F.col("PERCENTILE_25").cast("double").alias("percentile_25_value"),
        F.col("MEDIAN").cast("double").alias("median_value"),
        F.col("PERCENTILE_75").cast("double").alias("percentile_75_value"),
        F.col("MAX_VALUE").cast("string").alias("max_value"),
    )
    return base.select(
        profile_id_udf(F.col("_column_name")).alias("profile_id"),
        F.lit(profile_snapshot_id).cast("string").alias("profile_snapshot_id"),
        F.lit(table_id).cast("string").alias("table_id"),
        column_id_udf(F.col("_column_name")).alias("column_id"),
        F.lit(workspace_id).cast("string").alias("workspace_id"),
        F.col("data_type").cast("string"),
        F.lit(str(runtime_context.get("table_name") or "")).cast("string").alias("table_name"),
        F.col("_column_name").cast("string").alias("column_name"),
        F.lit((runtime_context.get("_profile_scope") or {}).get("profile_scope", "full_table")).alias("profile_scope"),
        F.lit((runtime_context.get("_profile_scope") or {}).get("profiling_max_rows")).cast("long").alias("profiling_max_rows"),
        "row_count",
        "non_null_count",
        "null_count",
        "null_percent",
        "distinct_count",
        "distinct_percent",
        "mean_value",
        "stddev_value",
        "min_value",
        "percentile_25_value",
        "median_value",
        "percentile_75_value",
        "max_value",
        *[column.alias(name) for name, column in audit_columns.items()],
    ).select(*PROFILED_COLUMNS)


def _frequency_metadata_dataframe(
    frequency_df,
    *,
    profiled_df,
    table_id: str,
    config: Any,
    active_workspace_id: str,
    runtime_context: dict[str, Any],
):
    """Map flattened frequency output to the same logical column profile."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    column_id_udf = F.udf(lambda column_name: build_column_id(table_id, column_name), T.StringType())
    identities = profiled_df.select(
        "column_id", "column_name", "table_id", "table_name", "data_type",
        "workspace_id", "profile_id", "profile_snapshot_id",
    )
    joined = frequency_df.withColumn("_column_id", column_id_udf(F.col("COLUMN_NAME"))).join(
        identities,
        (F.col("_column_id") == identities.column_id) & (frequency_df.DATA_TYPE == identities.data_type),
        "inner",
    )
    audit_columns = _audit_literal_columns(config=config, active_workspace_id=active_workspace_id, runtime_context=runtime_context)
    frequency_id_udf = F.udf(
        lambda profile_id, rank: str(uuid5(NAMESPACE_URL, f"{profile_id}|{rank}")),
        T.StringType(),
    )
    return joined.select(
        frequency_id_udf(identities.profile_id, F.col("FREQUENCY_RANK")).alias("frequency_id"),
        identities.profile_id.cast("string").alias("profile_id"),
        identities.profile_snapshot_id.cast("string").alias("profile_snapshot_id"),
        identities.table_id.cast("string").alias("table_id"),
        identities.column_id.cast("string").alias("column_id"),
        identities.table_name.cast("string").alias("table_name"),
        identities.column_name.cast("string").alias("column_name"),
        identities.data_type.cast("string").alias("data_type"),
        identities.workspace_id.cast("string").alias("workspace_id"),
        F.lit((runtime_context.get("_profile_scope") or {}).get("profile_scope", "full_table")).alias("profile_scope"),
        F.lit((runtime_context.get("_profile_scope") or {}).get("profiling_max_rows")).cast("long").alias("profiling_max_rows"),
        F.col("VALUE").cast("string").alias("value"),
        F.col("FREQUENCY_COUNT").cast("long").alias("frequency_count"),
        F.col("FREQUENCY_PERCENT").cast("double").alias("frequency_percent"),
        F.col("FREQUENCY_RANK").cast("integer").alias("frequency_rank"),
        F.col("PROFILED_ROW_COUNT").cast("long").alias("profiled_row_count"),
        F.col("PROFILED_NON_NULL_COUNT").cast("long").alias("profiled_non_null_count"),
        *[column.alias(name) for name, column in audit_columns.items()],
    ).select(*PROFILED_FREQUENCY_COLUMNS)


def _replace_snapshot_rows(
    *, dataframe: Any, table_name: str, row_id: str, config: Any, active_workspace_id: str, spark_session: Any
) -> None:
    """Atomically replace one snapshot's rows using their deterministic row identities."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(f"Delta Lake support is required for replacement {table_name} writes.") from exc
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "Metadata", table_name, metadata_table_physical_schema(config, table_name),
        context={"config": config, "scope_workspace_id": active_workspace_id},
    )
    snapshot = dataframe.select("profile_snapshot_id").dropDuplicates().first()
    if snapshot is None:
        return
    snapshot_id = str(snapshot["profile_snapshot_id"]).replace("'", "''")
    (
        retry_delta_metadata(lambda: DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(dataframe.alias("source"), f"target.{row_id} = source.{row_id}")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .whenNotMatchedBySourceDelete(
            condition=f"target.profile_snapshot_id = '{snapshot_id}'"
        )
        .execute())
    )


def _replace_frequency_rows(
    *, frequency_df: Any | None, profiled_df: Any, config: Any, active_workspace_id: str, spark_session: Any
) -> None:
    """Replace flattened Frequency rows only for the current profiling snapshot."""
    if frequency_df is not None:
        _replace_snapshot_rows(
            dataframe=frequency_df, table_name=PROFILED_FREQUENCY_TABLE,
            row_id="frequency_id", config=config, active_workspace_id=active_workspace_id, spark_session=spark_session,
        )
        return
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake support is required for replacement METADATA_DATA_PROFILED_FREQUENCY writes."
        ) from exc
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "Metadata",
        PROFILED_FREQUENCY_TABLE,
        metadata_table_physical_schema(config, PROFILED_FREQUENCY_TABLE),
        context={"config": config, "scope_workspace_id": active_workspace_id},
    )
    snapshots = profiled_df.select("profile_snapshot_id").dropDuplicates()
    (retry_delta_metadata(lambda: DeltaTable.forPath(spark_session, path).alias("target")
     .merge(snapshots.alias("source"), "target.profile_snapshot_id = source.profile_snapshot_id")
     .whenMatchedDelete().execute()))


def _delete_profile_snapshot(
    *, profiled_df: Any, config: Any, active_workspace_id: str, spark_session: Any
) -> None:
    """Remove an uncommitted snapshot, deleting summary rows before orphan frequencies."""
    from delta.tables import DeltaTable

    snapshots = profiled_df.select("profile_snapshot_id").dropDuplicates()
    for table_name in (PROFILED_TABLE, PROFILED_FREQUENCY_TABLE):
        _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
            "Metadata", table_name, metadata_table_physical_schema(config, table_name),
            context={"config": config, "scope_workspace_id": active_workspace_id},
        )
        (retry_delta_metadata(lambda: DeltaTable.forPath(spark_session, path).alias("target")
         .merge(snapshots.alias("source"), "target.profile_snapshot_id = source.profile_snapshot_id")
         .whenMatchedDelete().execute()))


def _stage_catalogue_profile_retry(
    *, profiled_df: Any, config: Any, active_workspace_id: str, spark_session: Any
) -> bool:
    """Return whether this activity is a retry and hide its prior completion marker."""
    from delta.tables import DeltaTable

    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "Metadata", CATALOGUE_TABLE, metadata_table_physical_schema(config, CATALOGUE_TABLE),
        context={"config": config, "scope_workspace_id": active_workspace_id},
    )
    activities = profiled_df.select(
        "workspace_id", "table_id", "_activity_id"
    ).dropDuplicates()
    target = DeltaTable.forPath(spark_session, path)
    same_activity_retry = bool(
        target.toDF()
        .select("workspace_id", "table_id", "_activity_id")
        .join(
            activities,
            on=["workspace_id", "table_id", "_activity_id"],
            how="inner",
        )
        .limit(1)
        .count()
    )
    (
        retry_delta_metadata(lambda: target.alias("target")
        .merge(
            activities.alias("source"),
            "target.workspace_id = source.workspace_id "
            "AND target.table_id = source.table_id "
            "AND target._activity_id = source._activity_id",
        )
        .whenMatchedUpdate(set={"last_profiled_at": "CAST(NULL AS TIMESTAMP)"})
        .execute())
    )
    return same_activity_retry


def _profile_snapshot_id(*, config: Any, active_workspace_id: str, context: dict[str, Any], table_id: str) -> str:
    """Return the stable snapshot identity for one table and Fabric activity."""
    if context.get("_profile_snapshot_id"):
        return str(context["_profile_snapshot_id"])
    activity_id = build_runtime_audit_fields(
        config=config, active_workspace_id=active_workspace_id, runtime_context=context
    )["_activity_id"]
    return str(uuid5(NAMESPACE_URL, f"fabricops-profile|{active_workspace_id}|{table_id}|{activity_id}"))


def _catalogue_dataframe_from_profiled(
    profiled_df,
    *,
    source_df: Any,
    store_type: str,
    layer: str,
    schema_name: str | None,
    table_name: str,
    load_strategy: str | None = None,
    load_strategy_parameters_json: dict[str, Any] | None = None,
    writer_workspace_id: str | None = None,
    writer_notebook_id: str | None = None,
    writer_notebook_name: str | None = None,
    scheduled_refresh_json: dict[str, Any] | None = None,
    profile_key_candidates_json: dict[str, Any] | None = None,
    source_fields: Sequence[tuple[str, str]] | None = None,
):
    """Return one table row and one row for each observed column asset."""
    from pyspark.sql import functions as F

    first = profiled_df.select(
        "table_id",
        "workspace_id",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ).first()
    if first is None:
        return profiled_df.sparkSession.createDataFrame([], schema=metadata_table_schema_registry()[CATALOGUE_TABLE])
    audit = {name: first[name] for name in CATALOGUE_COLUMNS if name.startswith("_")}
    common = {
        "table_id": first["table_id"],
        "workspace_id": first["workspace_id"],
        "store_type": store_type,
        "layer": layer,
        "schema_name": schema_name,
        "table_name": table_name,
        "first_profiled_at": first["_committed_at"],
        "last_profiled_at": first["_committed_at"],
        "is_active": True,
        **audit,
    }
    rows = [
        coerce_metadata_row_types(
            CATALOGUE_TABLE,
            {
                **common,
                "metadata_level": "table",
                "column_id": None,
                "column_name": None,
                "data_type": None,
                "load_strategy": load_strategy,
                "load_strategy_parameters_json": load_strategy_parameters_json,
                "writer_workspace_id": writer_workspace_id,
                "writer_notebook_id": writer_notebook_id,
                "writer_notebook_name": writer_notebook_name,
                "scheduled_refresh_json": scheduled_refresh_json,
                "profile_key_candidates_json": profile_key_candidates_json,
            },
        )
    ]
    fields = source_fields or [(field.name, field.dataType.simpleString()) for field in source_df.schema.fields]
    for column_name, data_type in fields:
        column_id = build_column_id(first["table_id"], column_name)
        rows.append(
            coerce_metadata_row_types(
                CATALOGUE_TABLE,
                {
                    **common,
                    "metadata_level": "column",
                    "column_id": column_id,
                    "column_name": column_name,
                    "data_type": data_type,
                    "load_strategy": None,
                    "load_strategy_parameters_json": None,
                    "writer_workspace_id": None,
                    "writer_notebook_id": None,
                    "writer_notebook_name": None,
                    "scheduled_refresh_json": None,
                    "profile_key_candidates_json": None,
                },
            )
        )
    return profiled_df.sparkSession.createDataFrame(
        [encode_metadata_row(CATALOGUE_TABLE, row) for row in rows],
        schema=metadata_table_schema_registry()[CATALOGUE_TABLE])


def _upsert_catalogue_identities(*, catalogue_df: Any, config: Any, active_workspace_id: str, spark_session: Any) -> None:
    """Upsert Catalogue rows by workspace-aware asset grain and deactivate missing columns."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake merge support is required for idempotent METADATA_DATA_CATALOGUE writes."
        ) from exc
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "Metadata",
        CATALOGUE_TABLE,
        metadata_table_physical_schema(config, CATALOGUE_TABLE),
        context={"config": config, "scope_workspace_id": active_workspace_id},
    )
    first = catalogue_df.select("workspace_id", "table_id").first()
    if first is None:
        return
    workspace_id = str(first["workspace_id"]).replace("'", "''")
    table_id = str(first["table_id"]).replace("'", "''")
    target = DeltaTable.forPath(spark_session, path)
    (
        retry_delta_metadata(lambda: target.alias("target")
        .merge(
            catalogue_df.alias("source"),
            "target.workspace_id = source.workspace_id "
            "AND target.metadata_level = source.metadata_level "
            "AND target.table_id = source.table_id "
            "AND coalesce(target.column_id, '') = coalesce(source.column_id, '')",
        )
        .whenMatchedUpdate(
            set={
                "store_type": "source.store_type",
                "layer": "source.layer",
                "schema_name": "source.schema_name",
                "table_name": "source.table_name",
                "column_name": "source.column_name",
                "data_type": "source.data_type",
                "load_strategy": "coalesce(source.load_strategy, target.load_strategy)",
                "load_strategy_parameters_json": (
                    "coalesce(source.load_strategy_parameters_json, target.load_strategy_parameters_json)"
                ),
                "writer_workspace_id": (
                    "coalesce(source.writer_workspace_id, target.writer_workspace_id)"
                ),
                "writer_notebook_id": (
                    "coalesce(source.writer_notebook_id, target.writer_notebook_id)"
                ),
                "writer_notebook_name": (
                    "coalesce(source.writer_notebook_name, target.writer_notebook_name)"
                ),
                "scheduled_refresh_json": (
                    "coalesce(source.scheduled_refresh_json, target.scheduled_refresh_json)"
                ),
                "profile_key_candidates_json": (
                    "coalesce(source.profile_key_candidates_json, target.profile_key_candidates_json)"
                ),
                "last_profiled_at": "source.last_profiled_at",
                "is_active": "true",
                "_committed_by": "source._committed_by",
                "_committed_at": "source._committed_at",
                "_workspace_id": "source._workspace_id",
                "_workspace_name": "source._workspace_name",
                "_notebook_id": "source._notebook_id",
                "_notebook_name": "source._notebook_name",
                "_metadata_lakehouse_name": "source._metadata_lakehouse_name",
                "_activity_id": "source._activity_id",
            }
        )
        .whenNotMatchedInsert(values={
            field.name: f"source.{field.name}"
            for field in metadata_table_schema_registry()[CATALOGUE_TABLE].fields
        })
        .whenNotMatchedBySourceUpdate(
            condition=(
                f"target.workspace_id = '{workspace_id}' AND target.table_id = '{table_id}' "
                "AND target.metadata_level = 'column' AND target.is_active = true"
            ),
            set={"is_active": "false"},
        )
        .execute())
    )


def execute_table_profile(
    *,
    dataframe=None,
    store: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    table_id: str | None = None,
    grain_discovery_enabled: bool = False,
    grain_discovery_max_columns: int = 3,
    grain_discovery_max_candidates: int = 8,
    frequency_columns=None,
    frequency_enabled: bool = False, frequency_top_n: int | None = 5,
    frequency_max_distinct_percent: float | None = 80.0,
    context=None,
    spark_session=None,
    verbose: bool = True,
    activities=None,
    presentations=None,
):
    """Execute selected persisted-table profiling activities without public workflow calls."""
    for name, value in (
        ("grain_discovery_max_columns", grain_discovery_max_columns),
        ("grain_discovery_max_candidates", grain_discovery_max_candidates),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer.")
    for name, value in (("grain_discovery_enabled", grain_discovery_enabled), ("frequency_enabled", frequency_enabled)):
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be a boolean.")
    coordinates = (store, schema, table_name)
    has_coordinates = any(value is not None for value in coordinates)
    if table_id is not None and has_coordinates:
        raise ValueError("table_id cannot be combined with store, schema, or table_name.")
    if has_coordinates and (store is None or table_name is None):
        raise ValueError("Provide both store and table_name when using physical identity.")
    if dataframe is None and table_id is None and not has_coordinates:
        raise ValueError("Provide dataframe, table_id, or both store and table_name.")
    if frequency_max_distinct_percent is not None and (
        not math.isfinite(frequency_max_distinct_percent)
        or not 0.0 <= frequency_max_distinct_percent <= 100.0
    ):
        raise ValueError("frequency_max_distinct_percent must be finite and between 0.0 and 100.0 when supplied.")

    emit = print if verbose else lambda *args, **kwargs: None
    selected_activities = set(activities) if activities is not None else {"standard", *({"grain"} if grain_discovery_enabled else set()), *({"frequency"} if frequency_enabled else set())}
    if not selected_activities or selected_activities - {"standard", "grain", "frequency"}:
        raise ValueError("Select standard, grain or frequency profiling activities.")
    grain_discovery_enabled = "grain" in selected_activities
    frequency_enabled = "frequency" in selected_activities
    selected_frequency_columns = [] if not frequency_enabled else (None if frequency_columns is None else list(frequency_columns))
    if frequency_top_n is not None and frequency_top_n <= 0:
        raise ValueError("frequency_top_n must be greater than zero when supplied.")
    spark_session = get_spark_session(spark_session, dataframe=dataframe, context=context)
    identity = None
    config = active_workspace_id = None
    warehouse_fields = None
    warehouse_physical = False
    profile_input_label = "supplied DataFrame"
    backend_label = "PySpark"

    if table_id is not None or has_coordinates:
        config, active_workspace_id, context = resolve_fabric_context() if context is None else (context["config"], context["scope_workspace_id"], context)
        if table_id is not None:
            identity = resolve_catalogue_table_identity(config, active_workspace_id, table_id, spark_session=spark_session, context=context)
        else:
            identity = resolve_physical_table_identity(
                config, active_workspace_id, store=store, schema=schema, table_name=table_name
            )
        store_kind = str(identity.get("store_kind") or identity.get("store_type") or "").lower()
        if store_kind not in {"lakehouse", "warehouse"}:
            raise ValueError(f"Configured table has unsupported store kind {store_kind or '<blank>'!r}.")
        identity["store_kind"] = store_kind
        physical_identity = ".".join(
            str(value)
            for value in (identity.get("store"), identity.get("schema"), identity.get("table_name"))
            if value
        )
        if dataframe is None:
            if store_kind == "lakehouse":
                dataframe = read_lakehouse_table(table_id=str(identity["table_id"]), context={**(context or {}), "_spark_session": spark_session})
                profile_input_label = "complete persisted Lakehouse table"
            else:
                warehouse_physical = True
                backend_label = "Warehouse SQL pushdown"
                profile_input_label = "complete persisted Warehouse table"
        else:
            profile_input_label = "supplied DataFrame"

        emit("FabricOps Profile")
        emit(f"1. Table → {physical_identity}")
        emit(f"   Input → {profile_input_label}")
        emit(f"2. Profiling backend → {backend_label}")
    else:
        emit("FabricOps Profile")
        emit("1. Identity → DataFrame only; no governed table_id")
        emit("2. Profiling backend → PySpark")

    scope = dict((context or {}).get("_profile_scope") or {
        "profile_scope": "supplied_dataframe" if profile_input_label == "supplied DataFrame" else "full_table",
        "profiling_max_rows": None,
    })
    max_rows = scope["profiling_max_rows"]
    if max_rows is not None:
        if warehouse_physical:
            dataframe = read_warehouse_query(
                f"SELECT TOP ({max_rows}) * FROM {_sql_identifier(identity['schema'])}.{_sql_identifier(identity['table_name'])}",
                store=identity["store"], context={**context, "_spark_session": spark_session})
            warehouse_physical = False
        dataframe = dataframe.limit(max_rows).cache()
    context = {**(context or {}), "_profile_scope": scope}
    transient_profile = None
    try:
        profile_metrics = {"row_count": None}
        profile_key_candidates: list[dict[str, Any]] = []
        if warehouse_physical:
            statistical_profile, frequency_profile, warehouse_columns = _warehouse_profile_dataframes(
                identity, spark_session=spark_session, context=context,
                frequency_columns=selected_frequency_columns,
                threshold_percent=frequency_max_distinct_percent, top_n=frequency_top_n, metrics=profile_metrics,
            )
            warehouse_fields = [(name, canonical) for name, canonical, _sql_type in warehouse_columns]
            if identity is not None and grain_discovery_enabled:
                profile_key_candidates = _warehouse_profile_key_candidates(
                    identity,
                    statistical_profile,
                    spark_session=spark_session,
                    context=context,
                    warehouse_columns=warehouse_columns,
                    max_columns=grain_discovery_max_columns,
                    max_candidates=grain_discovery_max_candidates,
                )
        else:
            statistical_profile = build_profile_dataframe(dataframe)
            if "standard" in selected_activities and (identity is None or not persistence_permitted(context)):
                # Share the lazy aggregates across diagnostics and presentation;
                # release only our cache after the bounded preview is detached.
                transient_profile = statistical_profile.cache()
                statistical_profile = transient_profile
            selected_columns = _selected_frequency_columns(
                dataframe, statistical_profile, selected_frequency_columns, frequency_max_distinct_percent
            )
            frequency_profile = None
            if selected_columns:
                frequency_profile = build_frequency_distribution_dataframe(
                    dataframe, columns=selected_columns, top_n=frequency_top_n
                )
            if identity is not None and grain_discovery_enabled:
                profile_key_candidates = _spark_profile_key_candidates(
                    dataframe, statistical_profile, metrics=profile_metrics,
                    max_columns=grain_discovery_max_columns, max_candidates=grain_discovery_max_candidates,
                )

        if identity is not None:
            emit("   Grain discovery → " + ("calculated" if grain_discovery_enabled else "disabled; saved candidates preserved"))
        frequency_label = "calculated" if frequency_profile is not None else "skipped; no eligible/requested columns"
        emit("3. Statistical profile → calculated")
        emit(f"4. Frequency profile → {frequency_label}")


        if identity is None or not persistence_permitted(context):
            emit("5. Metadata persistence → disabled by Dry Run policy" if identity is not None else
                  "5. Metadata persistence → skipped; DataFrame-only profiling does not invent a table_id")
            emit("Result → profile outputs returned; no Catalogue or profiling metadata was written.")
            result = {"profile": statistical_profile, "frequency_profile": frequency_profile, **({"grain_candidates": profile_key_candidates} if activities is not None else {}), **profile_metrics}
        else:
            observation = {
                "identity": identity, "profile": statistical_profile, "frequency_profile": frequency_profile,
                "grain_candidates": profile_key_candidates, "row_count": profile_metrics["row_count"],
                "activities": selected_activities, "grain_discovery_max_columns": grain_discovery_max_columns,
                "replace_frequency": frequency_enabled or activities is None,
                "source_fields": warehouse_fields, "source_df": dataframe,
            }
            result = _persist_profile_observation(observation,
                context={**context, "config": config, "scope_workspace_id": active_workspace_id},
                spark_session=spark_session, emit=emit)
        if "standard" in selected_activities and result.get("profile") is not None:
            presentation = capture_profile_presentation(result["profile"], scope=scope,
                dry_run=not persistence_permitted(context), table=physical_identity if identity is not None else None)
            if presentations is None:
                display_profile_presentations([presentation])
            elif presentation is not None:
                presentations.append(presentation)
        return result
    finally:
        if transient_profile is not None:
            transient_profile.unpersist()
        if max_rows is not None:
            dataframe.unpersist()


def _persist_profile_observation(observation, *, context, spark_session, emit):
    """Publish already calculated aggregates through the existing metadata boundaries."""
    config, active_workspace_id = context["config"], context["scope_workspace_id"]
    identity = observation["identity"]
    statistical_profile, frequency_profile = observation["profile"], observation["frequency_profile"]
    profile_key_candidates = observation["grain_candidates"]
    profile_metrics = {"row_count": observation["row_count"]}
    selected_activities = observation["activities"]
    grain_discovery_enabled = "grain" in selected_activities
    grain_discovery_max_columns = observation["grain_discovery_max_columns"]
    if selected_activities == {"grain"}:
        _persist_grain_candidates(identity, profile_key_candidates, max_columns=grain_discovery_max_columns,
            config=config, active_workspace_id=active_workspace_id, context=context, spark_session=spark_session)
        return {"grain_candidates": profile_key_candidates, **profile_metrics}

    profile_snapshot_id = _profile_snapshot_id(
        config=config, active_workspace_id=active_workspace_id, context=context, table_id=identity["table_id"]
    )
    profiled_df = _canonical_profiled_dataframe(
        statistical_profile,
        config=config,
        active_workspace_id=active_workspace_id,
        runtime_context={**context, "table_name": identity.get("table_name")},
        workspace_id=active_workspace_id,
        table_id=identity["table_id"],
        profile_snapshot_id=profile_snapshot_id,
    ).cache()
    try:
        profiled_df.count()
        if profile_metrics["row_count"] is None:
            measured = profiled_df.select("row_count").first()
            profile_metrics["row_count"] = measured["row_count"] if measured is not None else 0
        frequency_metadata_df = None
        if frequency_profile is not None:
            frequency_metadata_df = _frequency_metadata_dataframe(
                frequency_profile,
                profiled_df=profiled_df,
                table_id=identity["table_id"],
                config=config,
                active_workspace_id=active_workspace_id,
                runtime_context=context,
            )
        if "standard" not in selected_activities:
            if "grain" in selected_activities:
                _persist_grain_candidates(identity, profile_key_candidates, max_columns=grain_discovery_max_columns,
                    config=config, active_workspace_id=active_workspace_id, context=context, spark_session=spark_session)
            from pyspark.sql import functions as F
            # Independent Frequency snapshots have no statistical-profile foreign key.
            # Table ID, Column ID and the activity snapshot retain complete identity.
            if frequency_metadata_df is not None:
                frequency_metadata_df = frequency_metadata_df.withColumn("profile_id", F.lit(None).cast("string"))
            try:
                _replace_frequency_rows(frequency_df=frequency_metadata_df, profiled_df=profiled_df,
                    config=config, active_workspace_id=active_workspace_id, spark_session=spark_session)
                return {"frequency_profile": frequency_profile, "empty_result": frequency_metadata_df is None or frequency_metadata_df.isEmpty(), **profile_metrics}
            finally:
                profiled_df.unpersist()

        summary_persisted = False
        try:
            same_activity_retry = _stage_catalogue_profile_retry(
                profiled_df=profiled_df, config=config, active_workspace_id=active_workspace_id, spark_session=spark_session
            )
            _replace_snapshot_rows(
                dataframe=profiled_df, table_name=PROFILED_TABLE, row_id="profile_id",
                config=config, active_workspace_id=active_workspace_id, spark_session=spark_session,
            )
            summary_persisted = True
            profile_action = "refreshed existing activity snapshot" if same_activity_retry else "created new activity snapshot"
            emit(f"5. Profile snapshot → {profile_action}")
            if observation["replace_frequency"]:
                _replace_frequency_rows(
                    frequency_df=frequency_metadata_df, profiled_df=profiled_df,
                    config=config, active_workspace_id=active_workspace_id, spark_session=spark_session,
                )
            if frequency_metadata_df is not None:
                frequency_action = (
                    "refreshed existing activity rows"
                    if same_activity_retry
                    else "created new activity rows"
                )
            elif same_activity_retry:
                frequency_action = "cleared existing activity rows; no frequency profile generated"
            else:
                frequency_action = "skipped; no frequency profile generated"
            emit(f"6. Frequency profile metadata → {frequency_action}")
            catalogue_df = _catalogue_dataframe_from_profiled(
                profiled_df, source_df=observation.get("source_df"), store_type=identity["store_kind"],
                layer=identity["store"], schema_name=identity["schema"],
                table_name=identity["table_name"], load_strategy=None,
                load_strategy_parameters_json=None,
                writer_workspace_id=None,
                writer_notebook_id=None,
                writer_notebook_name=None,
                scheduled_refresh_json=None,
                profile_key_candidates_json=_key_candidate_evidence(
                    profile_key_candidates, max_columns=grain_discovery_max_columns, scope=context.get("_profile_scope")
                ) if grain_discovery_enabled else None,
                source_fields=observation["source_fields"],
            )
            _upsert_catalogue_identities(
                catalogue_df=catalogue_df, config=config, active_workspace_id=active_workspace_id, spark_session=spark_session,
            )
        except Exception:
            if summary_persisted:
                try:
                    _delete_profile_snapshot(
                        profiled_df=profiled_df, config=config, active_workspace_id=active_workspace_id, spark_session=spark_session
                    )
                except Exception as cleanup_error:
                    emit(
                        "Warning: incomplete profiling snapshot cleanup failed; "
                        "Catalogue completion state remains authoritative. "
                        f"Cleanup error: {cleanup_error}"
                    )
            raise
        catalogue_action = "updated" if same_activity_retry else "registered or updated"
        emit(
            f"7. Catalogue → {catalogue_action} table and column metadata; "
            "existing load strategy and parameters preserved"
        )
        emit("Result → Profile completed and metadata saved.")
        return {"profile": profiled_df, "frequency_profile": frequency_profile, **profile_metrics}
    except BaseException:
        profiled_df.unpersist()
        raise


def _persist_grain_candidates(identity, candidates, *, max_columns, config, active_workspace_id, context, spark_session):
    """Update only discovered candidates on an existing Catalogue table identity."""
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F
    _store, _table, _schema, path = resolve_configured_lakehouse_table("Metadata", CATALOGUE_TABLE,
        metadata_table_physical_schema(config, CATALOGUE_TABLE), context=context)
    table = DeltaTable.forPath(spark_session, path)
    condition = ((F.col("table_id") == identity["table_id"]) & (F.col("workspace_id") == active_workspace_id)
                 & (F.col("metadata_level") == "table"))
    if table.toDF().where(condition).limit(2).count() != 1:
        raise RuntimeError("Grain Discovery requires one registered Catalogue table in this workspace_id.")
    audit = build_runtime_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=context)
    candidate_value = F.lit(encode_metadata_row(CATALOGUE_TABLE, {
        "profile_key_candidates_json": _key_candidate_evidence(candidates, max_columns=max_columns, scope=context.get("_profile_scope")),
    })["profile_key_candidates_json"])
    updates = {"profile_key_candidates_json": candidate_value,
        **{name: F.lit(value) for name, value in audit.items()}}
    retry_delta_metadata(lambda: DeltaTable.forPath(spark_session, path).update(condition=condition, set=updates))
