"""Tests for Fabric notebook browser-side widget safeguards."""

from __future__ import annotations

import pytest

from fabricops_kit.widgets import _FABRIC_NOTEBOOK_UX_JAVASCRIPT

pytestmark = pytest.mark.unit


def test_focus_release_is_scoped_to_fabricops_forms():
    """Blur the active FabricOps control after completed value and button actions."""
    script = _FABRIC_NOTEBOOK_UX_JAVASCRIPT

    assert 'document.addEventListener("change"' in script
    assert 'target.closest(".fabricops-form")' in script
    assert 'document.addEventListener("click"' in script
    assert 'target.closest("button")' in script
    assert 'button.closest(".fabricops-form")' in script
    assert "window.__fabricopsFocusReleaseInstalled" in script
    assert "const active = document.activeElement" in script
    assert "form.contains(active)" in script
    assert "active.blur()" in script
    assert "document.activeElement === target" not in script
    assert "releaseFocus(form, 50)" in script
    assert "releaseFocus(form, 100)" in script


def test_fabric_form_css_uses_one_fixed_label_control_grid():
    """Keep every standard FabricOps field aligned to the same label and control columns."""
    script = _FABRIC_NOTEBOOK_UX_JAVASCRIPT

    assert ".fabricops-form .widget-inline-hbox:not(.widget-checkbox)" in script
    assert "display: grid !important" in script
    assert "grid-template-columns: 150px minmax(0, 560px) !important" in script
    assert "column-gap: 12px !important" in script
    assert "max-width: 722px !important" in script
    assert ".fabricops-form .widget-inline-hbox:not(.widget-checkbox) > .widget-label" in script
    assert "width: 150px !important" in script
    assert ".fabricops-form .widget-select-multiple select" in script
    assert "max-width: 560px !important" in script
    assert "box-sizing: border-box !important" in script
    assert 'STYLE_ID = "fabricops-widget-ux-style"' in script
