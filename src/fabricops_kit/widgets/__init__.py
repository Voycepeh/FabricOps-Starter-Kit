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
  if (window.__fabricopsNotebookUXVersion === 4) {
    return;
  }
  window.__fabricopsFocusReleaseInstalled = true;
  window.__fabricopsNotebookUXVersion = 4;

  // A single-line input cannot wrap its selected value. A grid overlay supplies
  // the readable resting label and sizes the field; focus reveals native search.
  const wrapSelector = (input) => {
    const owner = input.closest(".fabricops-searchable-selector");
    if (!owner || owner.classList.contains("fabricops-selector-wrapped")) return;
    const label = document.createElement("div");
    label.className = "fabricops-selector-value";
    label.setAttribute("aria-hidden", "true");
    const sync = () => {
      label.textContent = input.value || input.placeholder;
      label.dataset.empty = String(!input.value);
    };
    // ComboboxView assigns .value directly when Python changes the selection.
    const valueProperty = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    Object.defineProperty(input, "value", {
      configurable:true,
      get() { return valueProperty.get.call(this); },
      set(value) { valueProperty.set.call(this, value); sync(); }
    });
    input.addEventListener("input", sync);
    input.addEventListener("change", sync);
    input.parentElement.append(label);
    owner.classList.add("fabricops-selector-wrapped");
    sync();
  };
  const wrapSelectors = (root) => {
    if (!(root instanceof Element || root instanceof Document)) return;
    if (root.matches?.(".fabricops-form .fabricops-searchable-selector input")) wrapSelector(root);
    root.querySelectorAll(".fabricops-form .fabricops-searchable-selector input").forEach(wrapSelector);
  };
  wrapSelectors(document);
  new MutationObserver(records => {
    for (const record of records) for (const node of record.addedNodes) wrapSelectors(node);
  }).observe(document.documentElement, {childList:true, subtree:true});

  // Native datalist popups truncate long dataset labels independently of the
  // input width. Keep the widget's datalist/model, but own its visible popup.
  const selectors = new WeakMap();
  let activeSelector = null;
  let popupSequence = 0;
  const closeSelector = () => {
    if (!activeSelector) return;
    const {input, popup, observer} = activeSelector;
    observer.disconnect();
    popup.remove();
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
    input.removeAttribute("aria-controls");
    activeSelector = null;
  };
  const positionSelector = () => {
    if (!activeSelector) return;
    const {input, popup} = activeSelector;
    if (!input.isConnected || input.disabled) { closeSelector(); return; }
    const rect = input.getBoundingClientRect();
    const below = innerHeight - rect.bottom - 8;
    const above = rect.top - 8;
    const upwards = below < 200 && above > below;
    popup.style.left = `${Math.max(4, Math.min(rect.left, innerWidth - rect.width - 4))}px`;
    popup.style.width = `${Math.min(rect.width, innerWidth - 8)}px`;
    popup.style.maxHeight = `${Math.max(0, Math.min(320, upwards ? above : below))}px`;
    popup.style.top = upwards ? "auto" : `${rect.bottom + 2}px`;
    popup.style.bottom = upwards ? `${innerHeight - rect.top + 2}px` : "auto";
  };
  const highlightSelector = (index) => {
    const state = activeSelector;
    if (!state || !state.popup.children.length) return;
    state.index = Math.max(0, Math.min(index, state.popup.children.length - 1));
    [...state.popup.children].forEach((option, i) => option.setAttribute("aria-selected", String(i === state.index)));
    const option = state.popup.children[state.index];
    state.input.setAttribute("aria-activedescendant", option.id);
    option.scrollIntoView({block:"nearest"});
  };
  const chooseSelector = (option) => {
    if (!activeSelector) return;
    const input = activeSelector.input;
    input.value = option.textContent;
    closeSelector();
    // Use the real ComboboxView handlers so ensure_option and stable values
    // continue to be synchronized by ipywidgets.
    input.dispatchEvent(new Event("change", {bubbles:true}));
  };
  const renderSelector = (filter) => {
    if (!activeSelector) return;
    const {input, popup, datalist} = activeSelector;
    activeSelector.index = -1;
    input.removeAttribute("aria-activedescendant");
    const query = filter ? input.value.toLocaleLowerCase() : "";
    popup.replaceChildren();
    for (const entry of datalist.options) {
      if (!entry.value.toLocaleLowerCase().includes(query)) continue;
      const option = document.createElement("div");
      option.id = `${popup.id}-${popup.children.length}`;
      option.setAttribute("role", "option");
      option.setAttribute("aria-selected", "false");
      option.textContent = entry.value;
      popup.append(option);
    }
    popup.hidden = !popup.children.length;
    input.setAttribute("aria-expanded", String(!popup.hidden));
    positionSelector();
  };
  const openSelector = (input, filter = false) => {
    if (input.disabled || input.readOnly) return;
    let datalist = selectors.get(input);
    if (!datalist) {
      datalist = document.getElementById(input.getAttribute("list"));
      if (!(datalist instanceof HTMLDataListElement)) return;
      selectors.set(input, datalist);
      input.removeAttribute("list");
      input.setAttribute("role", "combobox");
      input.setAttribute("aria-autocomplete", "list");
      input.setAttribute("aria-haspopup", "listbox");
    }
    if (activeSelector?.input !== input) {
      closeSelector();
      const popup = document.createElement("div");
      popup.className = "fabricops-selector-popup";
      popup.id = `fabricops-selector-popup-${++popupSequence}`;
      popup.setAttribute("role", "listbox");
      popup.setAttribute("aria-label", input.getAttribute("aria-label") || input.placeholder || "Options");
      document.body.append(popup);
      input.setAttribute("aria-controls", popup.id);
      const observer = new MutationObserver(() => renderSelector(false));
      observer.observe(datalist, {childList:true, subtree:true, attributes:true});
      activeSelector = {input, popup, datalist, observer, index:-1};
      popup.addEventListener("pointerdown", event => event.preventDefault());
      popup.addEventListener("click", event => {
        const option = event.target.closest('[role="option"]');
        if (option) chooseSelector(option);
      });
    }
    renderSelector(filter);
  };
  const selectorInput = target => target instanceof HTMLInputElement &&
    target.closest(".fabricops-form .fabricops-searchable-selector") ? target : null;
  document.addEventListener("pointerdown", event => {
    const input = selectorInput(event.target);
    if (input) openSelector(input);
    else if (activeSelector && !activeSelector.popup.contains(event.target)) closeSelector();
  }, true);
  document.addEventListener("focusin", event => {
    const input = selectorInput(event.target);
    if (input) openSelector(input);
  });
  document.addEventListener("focusout", event => {
    if (activeSelector?.input === event.target) closeSelector();
  });
  document.addEventListener("input", event => {
    const input = selectorInput(event.target);
    if (input && document.activeElement === input) openSelector(input, true);
  });
  document.addEventListener("keydown", event => {
    const input = selectorInput(event.target);
    if (!input || event.isComposing) return;
    if (event.key === "Escape" || event.key === "Tab") {
      closeSelector();
      if (event.key === "Escape") { event.preventDefault(); event.stopPropagation(); }
    } else if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      event.stopPropagation();
      if (!activeSelector) openSelector(input);
      highlightSelector((activeSelector?.index ?? -1) + (event.key === "ArrowDown" ? 1 : -1));
    } else if (event.key === "Enter" && activeSelector?.index >= 0) {
      event.preventDefault();
      event.stopPropagation();
      chooseSelector(activeSelector.popup.children[activeSelector.index]);
    }
  }, true);
  window.addEventListener("resize", positionSelector);
  document.addEventListener("scroll", event => {
    if (activeSelector && !activeSelector.popup.contains(event.target)) positionSelector();
  }, true);

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
      if (active && activeSelector?.input !== active && form.contains(active) && typeof active.blur === "function") {
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
