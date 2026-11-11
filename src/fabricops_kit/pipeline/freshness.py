"""Explicit current-source Freshness evidence; profiles never authorize freshness."""
from datetime import UTC, date, datetime, timedelta
import hashlib
import json
import math


def validate_freshness_parameters(parameters):
    """Validate an explicit evidence method, scope, and positive age threshold."""
    if not isinstance(parameters, dict):
        raise ValueError("Freshness parameters must be an object.")
    method = parameters.get("evidence_method")
    if method not in {"metadata", "column"}:
        raise ValueError("Freshness requires evidence_method metadata or column; no fallback is permitted.")
    age = parameters.get("maximum_age")
    if type(age) not in {int, float} or not math.isfinite(age) or age <= 0:
        raise ValueError("Freshness maximum_age must be finite and positive.")
    if parameters.get("maximum_age_unit") not in {"minutes", "hours", "days"}:
        raise ValueError("Freshness maximum_age_unit must be minutes, hours, or days.")
    scope = parameters.get("evaluation_scope")
    if scope not in {"full_dataset", "incremental_batch"}:
        raise ValueError("Freshness requires an explicit evaluation_scope.")
    if method == "metadata" and scope != "full_dataset":
        raise ValueError("Metadata Freshness describes the full physical source.")
    if method == "column" and not str(parameters.get("freshness_column") or "").strip():
        raise ValueError("Column Freshness requires a timestamp column.")
    return dict(parameters)


def _timestamp(value):
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

    Column aggregation scans data. Delta history supplies supported physical-table
    modification metadata. Files use every resolved member's modification time;
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
        if params["evidence_method"] == "column":
            if dataframe is None:
                return {**evidence, "reason": "The configured dataset scope is unavailable."}
            column = params["freshness_column"]
            if hasattr(dataframe, "columns"):
                from pyspark.sql import functions as F
                if column not in dataframe.columns:
                    return {**evidence, "outcome": "invalid", "reason": "Configured timestamp column is missing."}
                value = F.col("`" + column.replace("`", "``") + "`")
                # Reject invalid non-null values as well as obtaining MAX. This is
                # deliberately a data action, never advertised as metadata-only.
                stamp = F.expr("try_cast(`" + column.replace("`", "``") + "` AS TIMESTAMP)")
                row = dataframe.agg(F.count(F.lit(1)).alias("rows"),
                    F.sum(F.when(value.isNotNull() & stamp.isNull(), 1).otherwise(0)).alias("invalid"),
                    F.max(stamp).alias("latest")).first()
                evidence.update(row_count=int(row["rows"]), invalid_count=int(row["invalid"] or 0), scan_required=True)
                if row["invalid"]:
                    return {**evidence, "outcome": "invalid", "reason": "Timestamp column contains invalid values."}
                latest = row["latest"]
            else:
                rows = list(dataframe)
                values = [row.get(column) for row in rows if row.get(column) is not None]
                evidence.update(row_count=len(rows), scan_required=True)
                latest = max((_timestamp(value) for value in values), default=None)
            if latest is None:
                return {**evidence, "reason": "Empty dataset or no non-null timestamp values."}
            evidence["freshness_column"] = column
        elif source.get("source_type") == "file":
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
        elif source.get("store_type") == "lakehouse":
            from delta.tables import DeltaTable
            path = source.get("resolved_path")
            if not path:
                return {**evidence, "reason": "Physical table path is unavailable."}
            from pyspark.sql import functions as F
            history = DeltaTable.forPath(spark_session, path).history()
            updates = history.filter(F.col("operation").isin("WRITE", "MERGE", "UPDATE", "DELETE", "STREAMING UPDATE", "CREATE TABLE AS SELECT", "CREATE OR REPLACE TABLE AS SELECT", "RESTORE"))
            row = updates.orderBy(F.col("version").desc()).first()
            if row is None:
                return {**evidence, "reason": "Reliable data update history is unavailable."}
            latest = row["timestamp"]
            evidence.update(table_version=int(row["version"]), operation=row["operation"], scan_required=False)
        else:
            return {**evidence, "reason": "Reliable physical-table update metadata is unsupported for this source."}
        evidence.update(outcome="available", latest_value=_timestamp(latest).isoformat())
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
    now = _timestamp(reference_time) if reference_time else datetime.now(UTC)
    age = params["maximum_age"] * {"minutes": 60, "hours": 3600, "days": 86400}[params["maximum_age_unit"]]
    minimum = now - timedelta(seconds=age)
    outcome = evidence.get("outcome", "unavailable")
    reason = evidence.get("reason", "")
    if any(evidence.get(key) != params[key] for key in ("evidence_method", "evaluation_scope")):
        outcome, reason = "invalid", "Evidence method or scope differs from the frozen rule."
    passed = False
    if outcome == "available":
        try:
            latest = _timestamp(evidence.get("latest_value"))
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
