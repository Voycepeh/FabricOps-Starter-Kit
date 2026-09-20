"""Tests for shared Spark-session resolution."""

from types import SimpleNamespace

import pytest

from fabricops_kit.io import shared


def test_get_spark_session_prefers_explicit_session(monkeypatch):
    explicit = object()
    monkeypatch.setattr(
        shared,
        "import_module",
        lambda _name: pytest.fail("PySpark lookup should not run for an explicit session."),
    )

    assert shared.get_spark_session(explicit) is explicit


def test_get_spark_session_uses_active_pyspark_session(monkeypatch):
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
