"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

from types import SimpleNamespace

from docs.breadcrumbs import on_page_context


def _page(title: str, url: str):
    return SimpleNamespace(title=title, url=url, file=object())


def _section(title: str, children: list[object]):
    return SimpleNamespace(title=title, children=children)


def test_breadcrumbs_follow_configured_nav_hierarchy() -> None:
    """Verify breadcrumbs follow configured nav hierarchy."""
    current = _page("setup_notebook", "api/reference/setup_notebook/")
    module_page = _page("config", "api/modules/config/")
    nav = SimpleNamespace(
        items=[
            _page("Home", ""),
            _section(
                "Function & DQ Rules Reference",
                [
                    _section("List of functions", [_page("Overview", "reference/"), current]),
                    _section("Functions by Modules", [module_page]),
                ],
            ),
        ]
    )
    context: dict[str, object] = {}

    on_page_context(context, current, {}, nav)

    assert context["fabricops_breadcrumbs"] == [
        {"title": "Home", "url": "index.html"},
        {"title": "Function & DQ Rules Reference", "url": "reference/"},
        {"title": "List of functions", "url": "reference/"},
        {"title": "setup_notebook", "url": None},
    ]


def test_breadcrumbs_keep_current_page_non_clickable() -> None:
    """Verify breadcrumbs keep current page non clickable."""
    current = _page("Guided Demo", "guided-demo/")
    nav = SimpleNamespace(items=[_page("Home", ""), _section("Get Started", [current])])
    context: dict[str, object] = {}

    on_page_context(context, current, {}, nav)

    assert context["fabricops_breadcrumbs"][-1] == {"title": "Guided Demo", "url": None}
    assert context["fabricops_breadcrumbs"][1] == {"title": "Get Started", "url": "guided-demo/"}


def test_breadcrumbs_fall_back_for_pages_outside_nav() -> None:
    """Verify breadcrumbs fall back for pages outside nav."""
    current = _page("Generated Function", "api/reference/generated-function/")
    nav = SimpleNamespace(items=[_page("Home", "")])
    context: dict[str, object] = {}

    on_page_context(context, current, {}, nav)

    assert context["fabricops_breadcrumbs"] == [
        {"title": "Home", "url": "index.html"},
        {"title": "Generated Function", "url": None},
    ]
