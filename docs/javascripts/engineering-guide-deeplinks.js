(() => {
  const GUIDE_PATH = "/reference/engineering-cheat-sheet/";

  function isEngineeringGuide() {
    return window.location.pathname.endsWith(GUIDE_PATH);
  }

  function resolveDetails(target) {
    if (!target) return null;

    const containingDetails = target.closest?.("details");
    if (containingDetails) return containingDetails;

    let sibling = target.nextElementSibling;
    while (sibling) {
      if (sibling.tagName === "DETAILS") return sibling;
      if (sibling.id) break;
      sibling = sibling.nextElementSibling;
    }

    return null;
  }

  function openHashTarget() {
    if (!isEngineeringGuide() || !window.location.hash) return;

    let id;
    try {
      id = decodeURIComponent(window.location.hash.slice(1));
    } catch {
      id = window.location.hash.slice(1);
    }

    if (!id) return;

    const target = document.getElementById(id);
    if (!target) return;

    const details = resolveDetails(target);
    if (details) details.open = true;

    window.requestAnimationFrame(() => {
      target.scrollIntoView({ block: "start" });
    });
  }

  window.addEventListener("hashchange", openHashTarget);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", openHashTarget, { once: true });
  } else {
    openHashTarget();
  }
})();
