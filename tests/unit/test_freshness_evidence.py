"""Freshness method, scope, current-source evidence and policy regressions."""
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline.shared import (
    collect_freshness_evidence, evaluate_freshness_evidence, validate_freshness_parameters,
)


def parameters(method="column", scope="full_dataset"):
    """Return one explicit frozen rule definition."""
    return {"evidence_method": method, "evaluation_scope": scope, "freshness_column": "modified_dt",
            "maximum_age": 2, "maximum_age_unit": "hours"}


@pytest.mark.parametrize("rows,outcome", [([], "unavailable"), ([{"modified_dt": None}], "unavailable"),
    ([{"modified_dt": "bad"}], "invalid"), ([{"modified_dt": "2026-11-11T10:00:00Z"}], "available")])
@pytest.mark.parametrize("action", ["Warn", "Block"])
def test_column_evidence_and_continuation(rows, outcome, action):
    """Empty/null/invalid observations are explicit and obey the authored policy."""
    params = parameters()
    evidence = collect_freshness_evidence(params, dataframe=rows)
    assert evidence["outcome"] == outcome
    result = evaluate_freshness_evidence(evidence, params, action=action, reference_time="2026-11-11T11:00:00Z")
    assert result["evidence_outcome"] == outcome
    assert result["can_continue"] is (outcome == "available" or action == "Warn")
    assert result["actual"] == evidence


def test_latest_timestamp_uses_instants_and_checks_every_nonnull_value():
    """Offsets are compared as instants and invalid rows cannot hide behind MAX."""
    params = parameters()
    evidence = collect_freshness_evidence(params, dataframe=[
        {"modified_dt": "2026-11-11T12:00:00+02:00"}, {"modified_dt": "2026-11-11T10:30:00Z"}])
    assert evidence["latest_value"] == "2026-11-11T10:30:00+00:00"
    invalid = collect_freshness_evidence(params, dataframe=[{"modified_dt": "bad"}, {"modified_dt": "2026-11-11"}])
    assert invalid["outcome"] == "invalid"


def test_methods_and_scopes_never_fall_back():
    """Unsupported metadata and mismatched batch evidence cannot authorize execution."""
    params = parameters("metadata")
    evidence = collect_freshness_evidence(params, source={"store_type": "warehouse"}, dataframe=[{"modified_dt": "2026-11-11"}])
    assert evidence["outcome"] == "unavailable"
    assert evaluate_freshness_evidence(evidence, parameters(), action="Block")["evidence_outcome"] == "invalid"
    batch = collect_freshness_evidence(parameters(scope="incremental_batch"), dataframe=[])
    assert batch["evaluation_scope"] == "incremental_batch" and batch["outcome"] == "unavailable"
    with pytest.raises(ValueError, match="full physical"):
        validate_freshness_parameters(parameters("metadata", "incremental_batch"))
    with pytest.raises(ValueError, match="evidence_method"):
        validate_freshness_parameters({"maximum_age": 1})


@pytest.mark.parametrize("stamp,outcome,status", [("2026-11-11T12:00:00Z", "invalid", "failed"),
    ("2026-11-10T10:00:00Z", "available", "failed"), ("2026-11-11T09:00:00Z", "available", "passed")])
def test_future_stale_and_exact_boundary(stamp, outcome, status):
    """Future values are invalid; the exact configured cutoff is inclusive."""
    params = parameters()
    evidence = collect_freshness_evidence(params, dataframe=[{"modified_dt": stamp}])
    result = evaluate_freshness_evidence(evidence, params, action="Block", reference_time="2026-11-11T11:00:00Z")
    assert (result["evidence_outcome"], result["status"]) == (outcome, status)


class FileEntry:
    """A Hadoop file status with auditable modification metadata."""

    def __init__(self, name, modified=0, directory=False):
        """Retain one resolved entry's type and timestamp."""
        self.name, self.modified, self.directory = name, modified, directory

    def getPath(self):
        """Represent the resolved Hadoop path."""
        return self

    def getName(self):
        """Return the final path component."""
        return self.name.rsplit("/", 1)[-1]

    def isDirectory(self):
        """Identify entries that require recursive expansion."""
        return self.directory

    def getModificationTime(self):
        """Return the physical modification time in milliseconds."""
        return self.modified

    def __str__(self):
        """Return the complete resolved member path for auditing."""
        return self.name


@pytest.mark.parametrize("selector", ["daily.csv", "folder", "folder/*.csv"])
def test_file_folder_and_wildcard_metadata(selector):
    """Folders expand recursively; the oldest matched data file governs the set."""
    now = int(datetime(2026, 11, 11, 10, tzinfo=UTC).timestamp() * 1000)
    files = [FileEntry("folder/old.csv", now-3600000), FileEntry("folder/new.csv", now), FileEntry("folder/_SUCCESS", 0)]
    fs = SimpleNamespace(globStatus=lambda path: files if "*" in selector or selector == "daily.csv" else [FileEntry("folder", directory=True)], listStatus=lambda path: files)
    root = SimpleNamespace(getFileSystem=lambda config: fs)
    jvm = SimpleNamespace(org=SimpleNamespace(apache=SimpleNamespace(hadoop=SimpleNamespace(fs=SimpleNamespace(Path=lambda path: root)))))
    spark = SimpleNamespace(_jvm=jvm, _jsc=SimpleNamespace(hadoopConfiguration=lambda: None))
    evidence = collect_freshness_evidence(parameters("metadata"), source={"source_type": "file", "resolved_path": selector}, spark_session=spark)
    assert evidence["outcome"] == "available"
    assert evidence["file_count"] == 2
    assert evidence["latest_value"] == "2026-11-11T09:00:00+00:00"
    assert evidence["aggregation"] == "oldest_member_modification"
    assert len(evidence["members_sha256"]) == 64


def test_failed_file_access_remains_unavailable():
    """An unreadable resolved selector cannot silently use a column or old profile."""
    result = collect_freshness_evidence(parameters("metadata"), source={"source_type": "file", "resolved_path": "denied"}, spark_session=object())
    assert result["outcome"] == "unavailable"
    assert evaluate_freshness_evidence(result, parameters("metadata"), action="Block")["can_continue"] is False


def test_spark_column_aggregation_reports_invalid_and_empty(spark_session):
    """Real Spark timestamp conversion rejects bad input and reports empty scope."""
    params = parameters()
    for rows, expected in [([], "unavailable"), ([("bad",), ("2026-11-11T10:00:00Z",)], "invalid"), ([("2026-11-11T10:00:00Z",)], "available")]:
        frame = spark_session.createDataFrame(rows, "modified_dt string")
        assert collect_freshness_evidence(params, dataframe=frame)["outcome"] == expected


def test_no_resolved_files_is_unavailable():
    """A wildcard matching no files cannot pass Freshness."""
    fs = SimpleNamespace(globStatus=lambda path: [])
    root = SimpleNamespace(getFileSystem=lambda config: fs)
    jvm = SimpleNamespace(org=SimpleNamespace(apache=SimpleNamespace(hadoop=SimpleNamespace(fs=SimpleNamespace(Path=lambda path: root)))))
    spark = SimpleNamespace(_jvm=jvm, _jsc=SimpleNamespace(hadoopConfiguration=lambda: None))
    evidence = collect_freshness_evidence(parameters("metadata"), source={"source_type": "file", "resolved_path": "empty/*.csv"}, spark_session=spark)
    assert evidence["outcome"] == "unavailable" and "no data files" in evidence["reason"]


@pytest.mark.parametrize("store_type", ["lakehouse", "warehouse"])
def test_table_metadata_excludes_maintenance_updates(spark_session, monkeypatch, store_type):
    """Metadata Freshness uses a physical data update, never OPTIMIZE time."""
    import sys
    from types import ModuleType
    history = spark_session.createDataFrame([
        ("WRITE", 1, datetime(2026, 11, 10, 10)), ("OPTIMIZE", 2, datetime(2026, 11, 11, 10))],
        "operation string, version long, timestamp timestamp")
    tables = ModuleType("delta.tables")
    tables.DeltaTable = SimpleNamespace(forPath=lambda spark, path: SimpleNamespace(history=lambda: history))
    monkeypatch.setitem(sys.modules, "delta.tables", tables)
    evidence = collect_freshness_evidence(parameters("metadata"), source={"store_type": store_type, "resolved_path": "physical-table"}, spark_session=spark_session)
    assert evidence["outcome"] == "available" and evidence["table_version"] == 1
    result = evaluate_freshness_evidence(evidence, parameters("metadata"), action="Block", reference_time="2026-11-11T11:00:00Z")
    assert result["status"] == "failed"


def test_file_metadata_does_not_ignore_reader_selection_options():
    """An unresolved reader filter cannot silently broaden metadata evidence scope."""
    evidence = collect_freshness_evidence(parameters("metadata"), source={"source_type": "file", "resolved_path": "folder",
        "reader_options": {"pathGlobFilter": "*.csv"}}, spark_session=object())
    assert evidence["outcome"] == "unavailable" and "reader-resolved" in evidence["reason"]


def test_evidence_for_another_timestamp_column_cannot_pass():
    """A fresh value from a different column is not evidence for the frozen rule."""
    params = parameters()
    evidence = collect_freshness_evidence(params, dataframe=[{"modified_dt": "2026-11-11T10:00:00Z"}])
    changed = {**params, "freshness_column": "snapshot_dt"}
    result = evaluate_freshness_evidence(evidence, changed, action="Block", reference_time="2026-11-11T11:00:00Z")
    assert result["evidence_outcome"] == "invalid" and result["can_continue"] is False


def test_fresh_oldest_member_cannot_hide_a_future_file_timestamp():
    """Collection age uses the oldest member but every member must be valid."""
    params = parameters("metadata")
    future = datetime(2026, 11, 11, 12, tzinfo=UTC).timestamp() * 1000
    evidence = {"evidence_method": "metadata", "evaluation_scope": "full_dataset", "outcome": "available",
        "latest_value": "2026-11-11T10:00:00Z", "aggregation": "oldest_member_modification",
        "members": [("old.csv", future-7200000), ("future.csv", future)]}
    result = evaluate_freshness_evidence(evidence, params, action="Block", reference_time="2026-11-11T11:00:00Z")
    assert result["evidence_outcome"] == "invalid" and result["can_continue"] is False


@pytest.mark.parametrize("column", [1, True, [], {}, None, ""])
def test_freshness_requires_a_real_timestamp_column_name(column):
    """Malformed column configuration is rejected before saving or physical access."""
    with pytest.raises(ValueError, match="timestamp column"):
        validate_freshness_parameters({**parameters(), "freshness_column": column})
