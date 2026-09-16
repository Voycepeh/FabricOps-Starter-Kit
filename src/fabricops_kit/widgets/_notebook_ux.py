"""Browser-side notebook UX safeguards for FabricOps widgets."""

from __future__ import annotations


FABRIC_NOTEBOOK_UX_JAVASCRIPT = r"""
(() => {
  const STYLE_ID = "fabricops-widget-ux-style";
  if (!document.getElementById(STYLE_ID)) {
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      .fabricops-form .widget-inline-hbox {
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
      }
      .fabricops-form .widget-inline-hbox > .widget-label,
      .fabricops-form .widget-label {
        display: block !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        flex: 0 0 auto !important;
        margin: 0 0 6px 0 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
      }
      .fabricops-form .widget-text,
      .fabricops-form .widget-textarea,
      .fabricops-form .widget-dropdown,
      .fabricops-form .widget-combobox,
      .fabricops-form .widget-select,
      .fabricops-form .widget-select-multiple,
      .fabricops-form .widget-toggle-buttons {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
      }
      .fabricops-form .widget-text input,
      .fabricops-form .widget-textarea textarea,
      .fabricops-form .widget-dropdown select,
      .fabricops-form .widget-combobox input,
      .fabricops-form .widget-select select,
      .fabricops-form .widget-select-multiple select {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
      }
      .fabricops-form .widget-hbox,
      .fabricops-form .widget-vbox,
      .fabricops-form .widget-gridbox {
        min-width: 0 !important;
        max-width: 100% !important;
      }
    `;
    document.head.appendChild(style);
  }

  if (window.__fabricopsFocusReleaseInstalled) {
    return;
  }
  window.__fabricopsFocusReleaseInstalled = true;

  const releaseFocus = (form, delay) => {
    window.setTimeout(() => {
      const active = document.activeElement;
      if (active && form.contains(active) && typeof active.blur === "function") {
        active.blur();
      }
    }, delay);
  };

  document.addEventListener("change", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) {
      return;
    }
    const form = target.closest(".fabricops-form");
    if (!form) {
      return;
    }
    if (target.matches("select, input[type='checkbox'], input[type='radio'], input[type='date'], input[type='number']")) {
      releaseFocus(form, 80);
    }
  }, true);

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) {
      return;
    }
    const button = target.closest("button");
    const form = button ? button.closest(".fabricops-form") : null;
    if (form) {
      releaseFocus(form, 120);
    }
  }, true);
})();
"""


def install_fabric_notebook_ux() -> bool:
    """Install Fabric-specific focus and layout safeguards in an active notebook.

    The browser listener is scoped to ``.fabricops-form`` so ordinary notebook
    controls are untouched. Text inputs retain focus while typing; focus is only
    released after select-like changes and button actions, preventing Microsoft
    Fabric from snapping the notebook viewport back to an interacted widget.
    """
    try:
        from IPython import get_ipython

        if get_ipython() is None:
            return False
        from IPython.display import Javascript, display
    except (ImportError, ModuleNotFoundError):
        return False

    display(Javascript(FABRIC_NOTEBOOK_UX_JAVASCRIPT))
    return True
