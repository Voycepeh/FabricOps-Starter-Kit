"""Exercise the shared Fabric AI invocation in notebook runtimes."""

from __future__ import annotations

import warnings

import pytest

from fabricops_kit.data_contract import shared as module


def _aifunc():
    """Provide the documented Runtime 2.0 configuration boundary."""
    from unittest.mock import Mock
    return Mock()


def _spark_ai_runtime(calls, *, response=" generated response ", error=None):
    """Return a small Spark AI Functions boundary for invocation tests."""
    row = {"fabricops_response": response, "fabricops_ai_error": error}

    class Result:
        def persist(self):
            return self

        def unpersist(self):
            pass

        def collect(self):
            return [row]

        def select(self, *columns):
            calls.append(("select", columns))
            return self

        def first(self):
            calls.append(("first",))
            return row

    class AI:
        def generate_response(self, **kwargs):
            print("Calling getAccessToken from PyTridentTokenLibrary")
            print("ai.generate_response: 100%", file=__import__("sys").stderr)
            calls.append(("generate_response", kwargs))
            return Result()

    class Frame:
        ai = AI()

    class Spark:
        def createDataFrame(self, rows):
            calls.append(("createDataFrame", rows))
            return Frame()

    return Spark()


def test_fabric_ai_invocation_uses_spark_accessor_and_returns_response(monkeypatch, capsys):
    """Use Spark AI Functions and suppress its notebook console chatter."""
    calls = []

    def fake_import(name):
        calls.append(("import", name))
        if name == "synapse.ml.spark.aifunc":
            return _aifunc()
        raise AssertionError(name)

    monkeypatch.setattr(module.importlib, "import_module", fake_import)
    monkeypatch.setattr(module, "get_spark_session", lambda: _spark_ai_runtime(calls))

    assert module.invoke_fabric_ai("prompt text") == "generated response"
    assert calls[0] == ("import", "synapse.ml.spark.aifunc")
    assert calls[1] == ("createDataFrame", [{"fabricops_prompt": "prompt text"}])
    assert calls[2] == ("generate_response", {
        "prompt": "{fabricops_prompt}", "is_prompt_template": True,
        "output_col": "fabricops_response", "error_col": "fabricops_ai_error",
    })
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_fabric_ai_suppresses_only_synapseml_protobuf_service_warning(monkeypatch):
    """Ignore SynapseML's legacy protobuf warning without hiding other warnings."""
    calls = []

    def fake_import(name):
        if name == "synapse.ml.spark.aifunc":
            warnings.warn("google.protobuf.service module is deprecated", UserWarning)
            warnings.warn("another SynapseML dependency warning", UserWarning)
            return _aifunc()
        raise AssertionError(name)

    monkeypatch.setattr(module.importlib, "import_module", fake_import)
    monkeypatch.setattr(module, "get_spark_session", lambda: _spark_ai_runtime(calls))
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        assert module.invoke_fabric_ai("prompt") == "generated response"

    assert [str(item.message) for item in captured] == [
        "another SynapseML dependency warning"
    ]


def test_fabric_ai_keeps_synapseml_import_failures_visible(monkeypatch):
    """A missing or broken Fabric AI dependency remains a genuine failure."""
    def fail_import(name):
        if name == "synapse.ml.spark.aifunc":
            raise ImportError("SynapseML failed to load")
        raise AssertionError(name)

    monkeypatch.setattr(module.importlib, "import_module", fail_import)
    with pytest.raises(module.AIConfigurationError, match="PySpark AI Functions"):
        module.invoke_fabric_ai("prompt")


def test_fabric_ai_unavailable_has_clear_failure(monkeypatch):
    """Report an actionable error outside an AI-enabled Fabric runtime."""
    class Frame:
        ai = None

    def fake_import(name):
        if name == "synapse.ml.spark.aifunc":
            return _aifunc()
        raise AssertionError(name)

    monkeypatch.setattr(module.importlib, "import_module", fake_import)
    spark = type("Spark", (), {"createDataFrame": lambda *_args: Frame()})()
    monkeypatch.setattr(module, "get_spark_session", lambda: spark)
    with pytest.raises(RuntimeError, match="AI Functions are unavailable"):
        module.invoke_fabric_ai("prompt")


def test_fabric_ai_invocation_works_while_notebook_event_loop_is_running(monkeypatch):
    """A synchronous widget invocation must not nest the active notebook event loop."""
    import asyncio

    calls = []
    monkeypatch.setattr(module.importlib, "import_module", lambda _name: _aifunc())
    monkeypatch.setattr(module, "get_spark_session", lambda: _spark_ai_runtime(calls))

    async def invoke_from_notebook_loop():
        assert asyncio.get_running_loop().is_running()
        return module.invoke_fabric_ai("prompt")

    assert asyncio.run(invoke_from_notebook_loop()) == "generated response"


def test_fabric_ai_assessment_provider_error_drops_provider_input(monkeypatch):
    """The assessment operation excludes the provider's raw error from diagnostics."""
    calls = []
    monkeypatch.setattr(module.importlib, "import_module", lambda _name: _aifunc())
    monkeypatch.setattr(
        module, "get_spark_session",
        lambda: _spark_ai_runtime(calls, response=None, error="capacity unavailable"),
    )
    with pytest.raises(module.AIProviderError, match="provider error") as failure:
        module.invoke_fabric_ai("prompt", operation="sensitivity_assessment")
    diagnostic = module.ai_failure_diagnostic(failure.value)
    assert diagnostic["category"] == "provider"
    assert diagnostic["recoverable"] is True
    assert "capacity unavailable" not in diagnostic["detail"]
