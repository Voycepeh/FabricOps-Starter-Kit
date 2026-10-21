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


def test_keyboard_focus_is_preserved_and_styles_have_one_owner():
    """Pointer callbacks release Fabric focus without changing keyboard navigation or injecting layout CSS."""
    script = _FABRIC_NOTEBOOK_UX_JAVASCRIPT
    assert 'document.addEventListener("pointerdown"' in script
    assert 'document.addEventListener("keydown"' in script
    assert 'if (!pointerAction) return;' in script
    assert 'createElement("style")' not in script
    assert 'grid-template-columns' not in script
