"""Public widget entrypoints for FabricOps notebook workflows."""

__all__ = [
    "widget_data_contract",
    "widget_activate_pipeline",
    "widget_activate_data_contract",
    "widget_data_agreement",
    "widget_data_steward",
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
  if (window.__fabricopsNotebookUXVersion === 2) {
    return;
  }
  window.__fabricopsFocusReleaseInstalled = true;
  window.__fabricopsNotebookUXVersion = 2;

  let pointerAction = false;
  let scrollSnapshot = null;
  let restoreFrame = 0;

  const cancelScrollProtection = () => {
    scrollSnapshot = null;
  };
  const rememberNotebookScroll = (form) => {
    const ancestors = [];
    for (let node = form.parentElement; node; node = node.parentElement) {
      if (node === document.body || node === document.documentElement) break;
      ancestors.push({node, top:node.scrollTop, left:node.scrollLeft});
    }
    scrollSnapshot = {form, ancestors, top:window.scrollY, left:window.scrollX};
  };
  const restoreNotebookScroll = () => {
    if (!scrollSnapshot) return;
    if (!scrollSnapshot.form.isConnected) {
      cancelScrollProtection();
      return;
    }
    for (const position of scrollSnapshot.ancestors) {
      if (position.node.isConnected &&
          (position.node.scrollTop !== position.top || position.node.scrollLeft !== position.left)) {
        position.node.scrollTo({top:position.top, left:position.left, behavior:"instant"});
      }
    }
    if (window.scrollY !== scrollSnapshot.top || window.scrollX !== scrollSnapshot.left) {
      window.scrollTo({top:scrollSnapshot.top, left:scrollSnapshot.left, behavior:"instant"});
    }
  };
  const scheduleScrollRestore = () => {
    if (!scrollSnapshot) return;
    if (restoreFrame) return;
    restoreFrame = window.requestAnimationFrame(() => {
      restoreFrame = 0;
      restoreNotebookScroll();
      // Notebook managers may scroll or restore focus in the following frame.
      window.requestAnimationFrame(restoreNotebookScroll);
    });
  };

  document.addEventListener("pointerdown", (event) => {
    pointerAction = true;
    const form = event.target instanceof Element ? event.target.closest(".fabricops-form") : null;
    if (form) rememberNotebookScroll(form);
    else {
      pointerAction = false;
      cancelScrollProtection();
    }
  }, true);
  document.addEventListener("keydown", () => {
    pointerAction = false;
    cancelScrollProtection();
  }, true);
  for (const eventName of ["wheel", "touchmove"]) {
    document.addEventListener(eventName, () => {
      pointerAction = false;
      cancelScrollProtection();
    }, {capture:true, passive:true});
  }

  document.addEventListener("focusin", (event) => {
    if (scrollSnapshot && scrollSnapshot.form.contains(event.target)) {
      scheduleScrollRestore();
      releaseFocus(scrollSnapshot.form, 50);
    }
  }, true);
  document.addEventListener("scroll", (event) => {
    if (!scrollSnapshot) return;
    if (event.target === document || event.target === document.documentElement ||
        scrollSnapshot.ancestors.some(position => position.node === event.target)) {
      scheduleScrollRestore();
    }
  }, true);

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
