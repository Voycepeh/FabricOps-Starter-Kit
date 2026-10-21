"""Public widget entrypoints for FabricOps notebook workflows."""

__all__ = [
    "widget_view_catalogue",
    "widget_data_contract",
    "widget_activate_pipeline",
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


# Fabric can restore focus after a pointer callback and pull the notebook back
# to the widget. Keyboard interaction keeps focus for normal form navigation.
# Form styling belongs to shared.form_page, not a second injected stylesheet.
_FABRIC_NOTEBOOK_UX_JAVASCRIPT = r"""
(() => {
  if (window.__fabricopsFocusReleaseInstalled) {
    return;
  }
  window.__fabricopsFocusReleaseInstalled = true;

  let pointerAction = false;
  document.addEventListener("pointerdown", () => { pointerAction = true; }, true);
  document.addEventListener("keydown", () => { pointerAction = false; }, true);

  const releaseFocus = (form, delay) => {
    if (!pointerAction) return;
    window.setTimeout(() => {
      if (!pointerAction) return;
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
        from IPython import display as ip

        ip.display(ip.Javascript(_FABRIC_NOTEBOOK_UX_JAVASCRIPT))
except (ImportError, ModuleNotFoundError):
    pass
