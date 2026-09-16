"""Tests for Fabric notebook browser-side widget safeguards."""

from __future__ import annotations

import pytest

from fabricops_kit.widgets import _FABRIC_NOTEBOOK_UX_JAVASCRIPT

pytestmark = pytest.mark.unit


def test_focus_release_is_scoped_and_keeps_text_entry_focusable():
    """Release focus after completed actions without blurring newly focused fields."""
    script = _FABRIC_NOTEBOOK_UX_JAVASCRIPT

    assert 'document.addEventListener("change"' in script
    assert 'target.closest(".fabricops-form")' in script
    assert 'document.addEventListener("click"' in script
    assert 'target.closest("button")' in script
    assert 'button.closest(".fabricops-form")' in script
    assert "window.__fabricopsFocusReleaseInstalled" in script
    assert "document.activeElement === target" in script
    assert "target.blur()" in script
    assert "releaseFocus(form, button, 120)" in script
    assert 'target.closest("input")' not in script


def test_fabric_form_css_prevents_label_control_overlap():
    """Force Fabric form labels above controls and constrain controls to their cells."""
    script = _FABRIC_NOTEBOOK_UX_JAVASCRIPT

    assert ".fabricops-form .widget-inline-hbox" in script
    assert "flex-direction: column !important" in script
    assert ".fabricops-form .widget-inline-hbox > .widget-label" in script
    assert "white-space: normal !important" in script
    assert ".fabricops-form .widget-select-multiple" in script
    assert "box-sizing: border-box !important" in script
    assert 'STYLE_ID = "fabricops-widget-ux-style"' in script
