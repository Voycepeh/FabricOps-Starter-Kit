"""Native promotion controls preserve explicit review and disabled admission."""
import importlib
from copy import deepcopy
from types import SimpleNamespace
import pytest

from tests.unit.test_activated_pipeline import promotion
module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")


@pytest.fixture
def widget_runtime(monkeypatch):
    """Verify widget runtime."""
    rows = [promotion()]
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: ({}, "DEV", context or {}))
    monkeypatch.setattr(module, "get_spark_session", lambda **kw: object())
    monkeypatch.setattr(module, "read_registry", lambda **kw: deepcopy(rows))
    from IPython import display as ip
    monkeypatch.setattr(ip, "display", lambda *a, **kw: None)
    return rows


def test_inspection_has_no_mutation_or_authority(widget_runtime):
    """Verify inspection has no mutation or authority."""
    rendered = module.widget_activate_pipeline()
    assert rendered["records"] == widget_runtime
    assert rendered["ready"] is False and "signed-in Fabric" in rendered["reason"]
    assert rendered["controls"]["review"].disabled
    assert rendered["controls"]["promote"].disabled


def test_review_confirmation_and_destination_change_invalidation(widget_runtime, monkeypatch):
    """Verify review confirmation and destination change invalidation."""
    review = {"candidate": promotion(2), "contracts": {}, "snapshot": b'{}'}
    calls = []
    monkeypatch.setattr(module, "prepare_pipeline_promotion", lambda *a, **kw: calls.append(kw) or review)
    monkeypatch.setattr(module, "stage_pipeline_promotion", lambda *a, **kw: promotion(2))
    dry_run = SimpleNamespace(plan=SimpleNamespace(pipeline_id=widget_runtime[0]["pipeline_id"]))
    ui = module.widget_activate_pipeline(dry_run=dry_run)
    with pytest.raises(ValueError, match="confirm"):
        ui["actions"]["promote"]()
    ui["actions"]["review"]()
    assert calls[-1]["expected_active_version"] == 1
    ui["controls"]["confirm"].value = True
    assert not ui["controls"]["promote"].disabled
    ui["controls"]["destination"].value = "PROD"
    assert ui["state"]["review"] is None and ui["controls"]["promote"].disabled
