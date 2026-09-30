"""MkDocs breadcrumb context helpers for the documentation theme."""

from __future__ import annotations


def _item_children(item):
    """Return child navigation items for section-like MkDocs nav nodes."""
    return getattr(item, "children", None) or []


def _item_url(item):
    """Return the item's direct URL, if MkDocs exposes one."""
    return getattr(item, "url", None)


def _first_descendant_url(item):
    """Return the first URL reachable from a navigation item."""
    url = _item_url(item)
    if url:
        return url

    for child in _item_children(item):
        child_url = _first_descendant_url(child)
        if child_url:
            return child_url

    return None


def _is_current_page(item, page):
    """Return True when a navigation item represents the current page."""
    if item is page:
        return True

    item_file = getattr(item, "file", None)
    page_file = getattr(page, "file", None)
    if item_file is not None and page_file is not None and item_file is page_file:
        return True

    item_url = _item_url(item)
    page_url = getattr(page, "url", None)
    return bool(item_url and page_url and item_url == page_url)


def _find_nav_path(items, page):
    """Return the configured navigation path for ``page``."""
    for item in items:
        if _is_current_page(item, page):
            return [item]

        child_path = _find_nav_path(_item_children(item), page)
        if child_path:
            return [item, *child_path]

    return []


def _crumb_from_item(item, *, current=False):
    """Convert a MkDocs navigation item to serializable breadcrumb data."""
    return {
        "title": getattr(item, "title", ""),
        "url": None if current else _first_descendant_url(item),
    }


def _home_crumb(nav):
    """Return the home breadcrumb from the configured navigation, if present."""
    for item in getattr(nav, "items", []):
        if getattr(item, "title", "") == "Home":
            return {"title": "Home", "url": _first_descendant_url(item) or "index.html"}

    return {"title": "Home", "url": "index.html"}


def on_page_context(context, page, config, nav):
    """Add navigation-derived breadcrumbs to each rendered page context."""
    nav_path = _find_nav_path(getattr(nav, "items", []), page)
    if not nav_path:
        context["fabricops_breadcrumbs"] = [
            _home_crumb(nav),
            {"title": getattr(page, "title", ""), "url": None},
        ]
        return context

    home = _home_crumb(nav)
    crumbs = [home]
    path_without_home = [item for item in nav_path if getattr(item, "title", "") != home["title"]]

    if not path_without_home:
        crumbs = [{"title": home["title"], "url": None}]
    else:
        last_index = len(path_without_home) - 1
        for index, item in enumerate(path_without_home):
            crumbs.append(_crumb_from_item(item, current=index == last_index))

    context["fabricops_breadcrumbs"] = [crumb for crumb in crumbs if crumb.get("title")]
    return context
