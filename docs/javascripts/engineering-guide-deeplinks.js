(() => {
  const GUIDE_PATH = "/reference/engineering-cheat-sheet/";

  function isEngineeringGuide() {
    return window.location.pathname.endsWith(GUIDE_PATH);
  }

  function getHashId() {
    if (!window.location.hash) return "";

    try {
      return decodeURIComponent(window.location.hash.slice(1));
    } catch {
      return window.location.hash.slice(1);
    }
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

  function openHashTarget(attempt = 0) {
    if (!isEngineeringGuide()) return;

    const id = getHashId();
    if (!id) return;

    const target = document.getElementById(id);

    // MkDocs Material can replace page content during instant navigation.
    // Retry briefly until the new page DOM and its <details> blocks exist.
    if (!target) {
      if (attempt < 10) {
        window.setTimeout(() => openHashTarget(attempt + 1), 50);
      }
      return;
    }

    const details = resolveDetails(target);
    if (details) {
      details.open = true;
    }

    // Wait until opening the details block has changed the layout before scrolling.
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        const scrollTarget = details || target;
        scrollTarget.scrollIntoView({ block: "start", behavior: "auto" });
      });
    });
  }

  function scheduleOpen() {
    window.setTimeout(() => openHashTarget(), 0);
  }

  window.addEventListener("hashchange", scheduleOpen);
  window.addEventListener("popstate", scheduleOpen);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleOpen, { once: true });
  } else {
    scheduleOpen();
  }

  // MkDocs Material exposes document$ for both initial rendering and instant
  // navigation. Subscribe when available so deep links also work when users
  // move to the Engineering Guide from another documentation page.
  if (typeof document$ !== "undefined" && document$?.subscribe) {
    document$.subscribe(scheduleOpen);
  }
})();
