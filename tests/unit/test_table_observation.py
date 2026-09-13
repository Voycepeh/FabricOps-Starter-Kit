"""Tests for internal current-run Source Observation state."""
# ruff: noqa: D103
from __future__ import annotations

import fabricops_kit
import pytest

from fabricops_kit.pipeline import shared


def test_observe_table_is_not_public() -> None:
    assert not hasattr(fabricops_kit, "observe_table")
    assert "observe_table" not in fabricops_kit.__all__


def test_current_observations_are_tracked_independently_by_table_id() -> None:
    shared.set_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source-a", observation=[{"source": "a"}]
    )
    shared.set_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source-b", observation=[{"source": "b"}]
    )
    assert shared.get_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source-a"
    ) == [{"source": "a"}]
    assert shared.get_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source-b"
    ) == [{"source": "b"}]


def test_missing_current_observation_requires_pipeline_read() -> None:
    with pytest.raises(ValueError, match=r"call pipeline_read\(\) first"):
        shared.get_current_source_observation(
            environment_name="dev", activity_id="missing", table_id="source-a"
        )
