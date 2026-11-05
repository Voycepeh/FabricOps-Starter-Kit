"""Runtime 2.0 configuration, request and measured usage boundary tests."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit.config import GovernanceConfig

module = importlib.import_module("fabricops_kit.widgets.enrichment_shared")


@pytest.mark.parametrize("model", ["gpt-5-mini", "gpt-5.1"])
@pytest.mark.parametrize("reasoning", [None, "minimal", "low", "medium", "high"])
@pytest.mark.parametrize("verbosity", [None, "low", "medium", "high"])
def test_supported_settings(model, reasoning, verbosity):
    """Preserve every documented explicit choice, including provider-default None."""
    settings = GovernanceConfig(ai_enrichment={
        "model_deployment_name": model, "reasoning_effort": reasoning, "verbosity": verbosity,
    }).ai_enrichment
    assert (settings["model_deployment_name"], settings["reasoning_effort"], settings["verbosity"]) == (
        model, reasoning, verbosity,
    )


@pytest.mark.parametrize("settings", [
    {"model_deployment_name": "gpt-6.1"}, {"model_deployment_name": None},
    {"model_deployment_name": ""}, {"reasoning_effort": "extreme"},
    {"verbosity": "minimal"}, {"enabled": "False"}, {"enabled": 1},
    {"model_deployment_name": []}, {"table_description_prompt": None},
    {"column_description_prompt": ""}, {"custom_endpoint": "https://example.test"},
])
def test_invalid_configuration_is_rejected(settings):
    """Invalid explicit values cannot silently become defaults."""
    with pytest.raises(ValueError, match="ai_enrichment"):
        GovernanceConfig(ai_enrichment=settings)


def test_defaults():
    """Default settings select the smaller built-in model without enabling AI."""
    settings = GovernanceConfig().ai_enrichment
    assert settings["enabled"] is False
    assert settings["model_deployment_name"] == "gpt-5-mini"
    assert settings["reasoning_effort"] == "low"
    assert settings["verbosity"] is None


def _runtime(monkeypatch, *, response="description", error=None, stats=None, failure=None):
    conf = Mock()
    aifunc = SimpleNamespace(default_conf=conf)
    monkeypatch.setattr(module.importlib, "import_module", lambda name: aifunc)
    result = Mock()
    result.persist.return_value = result
    result.collect.side_effect = failure
    if failure is None:
        result.collect.return_value = [{"fabricops_response": response, "fabricops_ai_error": error}]
    if stats is None:
        result.ai.stats.collect.side_effect = AttributeError("Stats not exposed")
    else:
        result.ai.stats.collect.return_value = [SimpleNamespace(asDict=lambda: stats)]
    spark = Mock()
    spark.createDataFrame.return_value.ai.generate_response.return_value = result
    monkeypatch.setattr(module, "get_spark_session", lambda: pytest.fail("Use widget Spark"))
    return conf, spark, result


def test_every_request_reapplies_runtime_settings_and_reads_actual_stats(monkeypatch):
    """Session mutations cannot override settings; stats come from one persisted result."""
    stats = {"input_tokens": 31, "output_tokens": 7, "cached_tokens": 0, "reasoning_tokens": 4,
             "num_successful": 1, "model": "gpt-5.1", "prompt": "must not retain"}
    conf, spark, result = _runtime(monkeypatch, stats=stats)
    settings = {"model_deployment_name": "gpt-5.1", "reasoning_effort": "medium", "verbosity": "medium"}
    usage = []
    for _ in range(2):
        assert module._invoke_fabric_ai(
            "private context", ai_config=settings, spark_session=spark, usage=usage, operation="grain",
        ) == "description"
    assert conf.set_deployment_name.call_args_list == [(("gpt-5.1",),), (("gpt-5.1",),)]
    assert conf.set_reasoning_effort.call_count == conf.reset_temperature.call_count == 2
    conf.set_reasoning_effort.assert_called_with("medium")
    conf.set_verbosity.assert_called_with("medium")
    assert conf.reset_URL.call_count == conf.reset_subscription_key.call_count == 2
    assert result.persist.call_count == result.unpersist.call_count == 2
    assert result.collect.call_count == result.ai.stats.collect.call_count == 2
    assert spark.createDataFrame.return_value.ai.generate_response.call_count == 2
    kwargs = spark.createDataFrame.return_value.ai.generate_response.call_args.kwargs
    assert kwargs["prompt"] == "{fabricops_prompt}" and kwargs["is_prompt_template"] is True
    assert usage[0]["operation"] == "grain" and usage[0]["model"] == "gpt-5.1"
    assert usage[0]["statistics"][0]["reasoning_tokens"] == 4
    assert "prompt" not in usage[0]["statistics"][0]
    assert "cu" not in str(usage).lower()


def test_missing_stats_do_not_invent_usage_or_break_authoring(monkeypatch):
    """Optional telemetry has no fabricated token or CU values."""
    conf, spark, result = _runtime(monkeypatch)
    usage = []
    assert module._invoke_fabric_ai("prompt", spark_session=spark, usage=usage) == "description"
    conf.set_deployment_name.assert_called_once_with("gpt-5-mini")
    conf.set_reasoning_effort.assert_called_once_with("low")
    conf.reset_verbosity.assert_called_once_with()
    assert usage[0]["statistics"] is None
    assert usage[0]["statistics_status"] == "unavailable"
    result.unpersist.assert_called_once_with()


@pytest.mark.parametrize("response,error,message", [
    ("", None, "empty response"), ("unused", "capacity limit", "capacity limit"),
])
def test_provider_response_failures_keep_details(monkeypatch, response, error, message):
    """Empty and rejected responses are provider failures, preserving original details."""
    _, spark, result = _runtime(monkeypatch, response=response, error=error)
    with pytest.raises(module.AIProviderError, match=message):
        module._invoke_fabric_ai("prompt", spark_session=spark)
    result.unpersist.assert_called_once_with()


def test_execution_failure_preserves_cause_and_releases_cache(monkeypatch):
    """Spark execution errors retain their original cause without misclassifying it."""
    original = RuntimeError("Spark execution failed with private context")
    _, spark, result = _runtime(monkeypatch, failure=original)
    usage = []
    with pytest.raises(module.AIExecutionError) as error:
        module._invoke_fabric_ai("prompt", spark_session=spark, usage=usage)
    assert error.value.__cause__ is original
    assert module.ai_failure_diagnostic(error.value)["category"] == "execution"
    assert usage[0]["statistics_status"] == "unavailable"
    result.unpersist.assert_called_once_with()


def test_no_result_row_is_a_provider_failure(monkeypatch):
    """A zero-row response is distinct from a local Spark exception."""
    _, spark, result = _runtime(monkeypatch)
    result.collect.return_value = []
    with pytest.raises(module.AIProviderError, match="no result row"):
        module._invoke_fabric_ai("prompt", spark_session=spark)


def test_initialization_failure_retains_cause(monkeypatch):
    """Broken Runtime 2.0 configuration fails before submitting a model request."""
    conf, spark, _ = _runtime(monkeypatch)
    original = RuntimeError("missing Runtime 2.0 setter")
    conf.reset_temperature.side_effect = original
    with pytest.raises(module.AIConfigurationError) as error:
        module._invoke_fabric_ai("prompt", spark_session=spark)
    assert error.value.__cause__ is original
    spark.createDataFrame.assert_not_called()


@pytest.mark.parametrize("failure,expected", [
    (module.AIProviderError("unsupported_parameter: temperature SECRET"), "parameter"),
    (module.AIProviderError("429 capacity SECRET"), "capacity"),
    (module.AIProviderError("403 permission SECRET"), "access"),
    (ValueError("bad JSON SECRET"), "validation"),
    (module.AIExecutionError("Spark SECRET"), "execution"),
])
def test_diagnostics_show_safe_cause_categories(failure, expected):
    """Only raw maintainer diagnostics retain sensitive provider text."""
    diagnostic = module.ai_failure_diagnostic(failure)
    assert expected in diagnostic["message"].lower() or expected == diagnostic["category"]
    assert "SECRET" not in diagnostic["message"]
    assert "SECRET" in diagnostic["detail"]
