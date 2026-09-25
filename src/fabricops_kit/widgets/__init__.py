"""Public widget entrypoints for FabricOps notebook workflows."""

__all__ = [
    "widget_view_catalogue",
    "widget_data_contract",
    "widget_activate_data_contract",
    "widget_select_data_contract",
    "widget_render_data_agreement",
    "widget_render_data_steward",
]

_WIDGET_MODULES = {name: f"fabricops_kit.widgets.{name}" for name in __all__}


def __getattr__(name: str):
    """Lazily load public widget callables."""
    if name not in _WIDGET_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    value = getattr(import_module(_WIDGET_MODULES[name]), name)
    globals()[name] = value
    return value


# Microsoft Fabric can restore browser focus to an interacted ipywidget after a
# value change or button callback. That focus restoration also scrolls the
# notebook back to the widget, fighting normal user scrolling. Install one
# form-scoped browser safeguard when the widgets package is imported. The CSS
# also gives every FabricOps form a stable two-column field grid so labels and
# controls align consistently instead of starting at the end of variable label text.
_FABRIC_NOTEBOOK_UX_JAVASCRIPT = r"""
(() => {
  const STYLE_ID = "fabricops-widget-ux-style";
  if (!document.getElementById(STYLE_ID)) {
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      .fabricops-form .widget-inline-hbox:not(.widget-checkbox) {
        display: grid !important;
        grid-template-columns: 150px minmax(0, 560px) !important;
        column-gap: 12px !important;
        align-items: start !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: 722px !important;
      }
      .fabricops-form .widget-inline-hbox:not(.widget-checkbox) > .widget-label {
        display: block !important;
        width: 150px !important;
        min-width: 150px !important;
        max-width: 150px !important;
        margin: 0 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
      }
      .fabricops-form .widget-text input,
      .fabricops-form .widget-textarea textarea,
      .fabricops-form .widget-dropdown select,
      .fabricops-form .widget-combobox input,
      .fabricops-form .widget-select select,
      .fabricops-form .widget-select-multiple select {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 560px !important;
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
    if (form) {
      releaseFocus(form, 50);
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
      releaseFocus(form, 100);
    }
  }, true);
})();
"""

try:
    from IPython import get_ipython

    if get_ipython() is not None:
        from IPython.display import Javascript, display

        display(Javascript(_FABRIC_NOTEBOOK_UX_JAVASCRIPT))
except (ImportError, ModuleNotFoundError):
    pass
