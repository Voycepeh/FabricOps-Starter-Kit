"""Tests for governed source-result orchestration."""

from importlib import import_module

import pytest


module = import_module("fabricops_kit.pipeline.check_and_profile_source")


class Frame:
    """Minimal DataFrame-shaped test value."""

    sparkSession = "spark"


def _prep(read_mode="full_dataset"):
    return {
        "source": {
            "table_id": "lakehouse||source||demo||orders",
            "table_name": "orders",
            "target": "source",
            "store_type": "lakehouse",
            "schema": "demo",
        },
        "read_mode": read_mode,
        "scope": {"type": read_mode},
    }


def _patch_governance(monkeypatch, *, can_continue=True):
    identity = _prep()["source"]
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: identity)
    monkeypatch.setattr(
        module,
        "check_dq_runtime",
        lambda *_args, **_kwargs: {"can_continue": can_continue, "summary": "dq"},
    )
    monkeypatch.setattr(
        module,
        "stop_if_failed",
        lambda result: (_ for _ in ()).throw(RuntimeError("blocked")) if not result["can_continue"] else None,
    )


def test_full_dataset_registers_canonical_profile(monkeypatch):
    """A complete registered source becomes canonical profiling evidence."""
    _patch_governance(monkeypatch)
    calls = []
    monkeypatch.setattr(
        module,
        "PROFILE_AND_REGISTER_TABLE_CORE",
        lambda frame, **kwargs: calls.append((frame, kwargs)) or "canonical-profile",
    )
    monkeypatch.setattr(module, "build_profile_dataframe", lambda _frame: pytest.fail("diagnostic profile"))

    result = module.check_and_profile_source(Frame(), source_prep=_prep())

    assert result == {
        "dq": {"can_continue": True, "summary": "dq"},
        "profile": "canonical-profile",
        "profile_kind": "canonical",
    }
    assert calls[0][1] == {"profile_role": "source", "table": _prep()["source"]}


@pytest.mark.parametrize(
    ("read_mode", "register_full_profile"),
    [("incremental_subset", True), ("full_dataset", False)],
)
def test_partial_or_query_result_is_diagnostic(monkeypatch, read_mode, register_full_profile):
    """Partial reads and query-shaped results cannot replace canonical profiles."""
    _patch_governance(monkeypatch)
    monkeypatch.setattr(
        module,
        "PROFILE_AND_REGISTER_TABLE_CORE",
        lambda *_args, **_kwargs: pytest.fail("canonical profile"),
    )
    monkeypatch.setattr(module, "build_profile_dataframe", lambda _frame: "diagnostic-profile")

    result = module.check_and_profile_source(
        Frame(), source_prep=_prep(read_mode), register_full_profile=register_full_profile,
    )

    assert result["profile"] == "diagnostic-profile"
    assert result["profile_kind"] == "diagnostic"


def test_blocking_dq_stops_before_profiling(monkeypatch):
    """A governed blocking DQ result prevents every profiling path."""
    _patch_governance(monkeypatch, can_continue=False)
    monkeypatch.setattr(module, "PROFILE_AND_REGISTER_TABLE_CORE", lambda *_args, **_kwargs: pytest.fail("profile"))
    monkeypatch.setattr(module, "build_profile_dataframe", lambda *_args, **_kwargs: pytest.fail("profile"))

    with pytest.raises(RuntimeError, match="blocked"):
        module.check_and_profile_source(Frame(), source_prep=_prep())


def test_skip_rejects_downstream_physical_result(monkeypatch):
    """Skipped preparation cannot be presented as a physically read source."""
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: pytest.fail("governance work"))

    with pytest.raises(ValueError, match="must not be read"):
        module.check_and_profile_source(Frame(), source_prep=_prep("skip"))
