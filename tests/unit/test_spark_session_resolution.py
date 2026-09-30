"""Tests for shared Spark-session resolution."""

import inspect
from types import SimpleNamespace

import pytest

from fabricops_kit import (
    check_dq,
    check_freshness,
    check_guardrail_coverage,
    check_schema,
    check_sensitive_data,
    check_source_drift,
    pipeline_read,
    pipeline_write,
    profile_table,
    scan_sql_access,
)
from fabricops_kit.io import shared


def test_get_spark_session_prefers_explicit_session(monkeypatch):
    """Prefer an explicitly supplied Spark session."""
    explicit = object()
    monkeypatch.setattr(
        shared,
        "import_module",
        lambda _name: pytest.fail("PySpark lookup should not run for an explicit session."),
    )

    assert shared.get_spark_session(explicit) is explicit


def test_get_spark_session_uses_active_pyspark_session(monkeypatch):
    """Fall back to PySpark's active session when needed."""
    active = object()

    class SparkSession:
        @staticmethod
        def getActiveSession():
            return active

    monkeypatch.delitem(shared.__dict__, "spark", raising=False)
    monkeypatch.setattr(
        shared,
        "import_module",
        lambda name: SimpleNamespace(SparkSession=SparkSession) if name == "pyspark.sql" else None,
    )

    assert shared.get_spark_session() is active


def test_get_spark_session_raises_when_no_session_is_available(monkeypatch):
    """Raise clearly when neither explicit nor active Spark exists."""
    class SparkSession:
        @staticmethod
        def getActiveSession():
            return None

    monkeypatch.delitem(shared.__dict__, "spark", raising=False)
    monkeypatch.setattr(
        shared,
        "import_module",
        lambda name: SimpleNamespace(SparkSession=SparkSession) if name == "pyspark.sql" else None,
    )

    with pytest.raises(RuntimeError, match="no active Spark session"):
        shared.get_spark_session()


@pytest.mark.parametrize(
    "function",
    [
        check_freshness,
        check_schema,
        check_source_drift,
        check_dq,
        check_sensitive_data,
        check_guardrail_coverage,
        profile_table,
        pipeline_read,
        pipeline_write,
        scan_sql_access,
    ],
)
def test_public_spark_dependent_orchestration_accepts_explicit_session(function):
    """Require explicit Spark injection across public Spark orchestration."""
    assert "spark_session" in inspect.signature(function).parameters
