"""Tests for shared Spark-session resolution."""

import inspect
from types import SimpleNamespace

import pytest

from fabricops_kit import profile_table, scan_sql_access, orchestrate_read, orchestrate_write
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_freshness import check_freshness
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.check_sensitive_data import check_sensitive_data
from fabricops_kit.pipeline.check_source_drift import check_source_drift
from fabricops_kit.pipeline.pipeline_read import pipeline_read
from fabricops_kit.pipeline.pipeline_write import pipeline_write
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
        lambda name: SimpleNamespace(SparkSession=SparkSession) if name == "pyspark.sql" else SimpleNamespace(get_ipython=lambda: None),
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
        lambda name: SimpleNamespace(SparkSession=SparkSession) if name == "pyspark.sql" else SimpleNamespace(get_ipython=lambda: None),
    )

    with pytest.raises(RuntimeError, match="No active Spark session"):
        shared.get_spark_session()


@pytest.mark.parametrize(
    "function",
    [
        check_freshness,
        check_schema,
        check_source_drift,
        check_dq,
        check_sensitive_data,
        profile_table,
        pipeline_read,
        pipeline_write,
        scan_sql_access,
        orchestrate_read,
        orchestrate_write,
    ],
)
def test_pipeline_stages_and_public_orchestrators_resolve_session_automatically(function):
    """Notebook entrypoints no longer expose session injection."""
    assert "spark_session" not in inspect.signature(function).parameters
    assert "spark" not in inspect.signature(function).parameters


def test_fabric_namespace_session_when_active_api_returns_none(monkeypatch):
    """Discover Fabric's notebook Spark even when PySpark has no active session."""
    spark = SimpleNamespace(sql=lambda query: query, conf=object())
    def import_module(name):
        if name == "pyspark.sql":
            return SimpleNamespace(SparkSession=SimpleNamespace(getActiveSession=lambda: None))
        return SimpleNamespace(get_ipython=lambda: SimpleNamespace(user_ns={"spark": spark}))
    monkeypatch.setattr(shared, "import_module", import_module)
    assert shared.get_spark_session() is spark


def test_dataframe_session_precedes_injection_and_execution_context(monkeypatch):
    """Use DataFrame ownership even if the active execution uses another session."""
    owned = object()
    monkeypatch.setattr(shared, "import_module", lambda name: pytest.fail("Must not discover another session"))
    assert shared.get_spark_session(object(), dataframe=SimpleNamespace(sparkSession=owned),
                                    context={"_pipeline_spark": object()}) is owned


def test_resolver_does_not_reuse_module_globals_or_cache(monkeypatch):
    """Never mistake library globals for the calling notebook or retain a session."""
    current = [object()]
    monkeypatch.setattr(shared, "spark", object(), raising=False)
    monkeypatch.setattr(shared, "import_module", lambda name: SimpleNamespace(
        SparkSession=SimpleNamespace(getActiveSession=lambda: current[0])))
    first = shared.get_spark_session()
    current[0] = object()
    assert shared.get_spark_session() is current[0]
    assert shared.get_spark_session() is not first



def test_local_configuration_warns_accurately_without_spark(monkeypatch):
    """Local configuration checks remain available without claiming Spark readiness."""
    from fabricops_kit import setup_notebook
    from tests.unit.test_setup_notebook_store_keys import _config
    monkeypatch.setattr(shared, "get_spark_session", lambda *_args: (_ for _ in ()).throw(RuntimeError('No active Spark session')))
    result = setup_notebook(_config(), env="dev", required_targets=["Metadata"])
    check = next(c for c in result.validation_results if c.name == "spark_session")
    assert check.status == "warn"
    assert "Spark-dependent operations are unavailable" in check.message
    assert result.paths["Metadata"].kind == "lakehouse"


def test_every_root_public_function_resolves_spark_without_parameters():
    """Audit the complete package export surface, including lazily loaded widgets."""
    import fabricops_kit
    for name in fabricops_kit.__all__:
        function = getattr(fabricops_kit, name)
        if inspect.isfunction(function):
            assert not {"spark", "spark_session"}.intersection(inspect.signature(function).parameters), name



def test_guardrail_uses_dataframe_session_without_discovery(monkeypatch):
    """A guardrail keeps DataFrame ownership even with no discoverable session."""
    from importlib import import_module
    owner = import_module("fabricops_kit.pipeline.check_dq")
    session = object()
    frame = SimpleNamespace(sparkSession=session)
    monkeypatch.setattr(owner, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(shared, "import_module", lambda name: pytest.fail("DataFrame session must be retained"))
    def contract(*args, **kwargs):
        assert kwargs["spark_session"] is session
        return None
    monkeypatch.setattr(owner, "resolve_pipeline_data_contract", contract)
    monkeypatch.setattr(owner, "print_guardrail_result", lambda *args, **kwargs: None)
    result = owner.check_dq(frame, table_id="orders", verbose=False)
    assert result["status"] == "skipped"
    assert result["can_continue"] is True
