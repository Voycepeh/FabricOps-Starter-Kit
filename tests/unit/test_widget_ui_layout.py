"""Focused contracts for the shared Fabric notebook widget design system."""

from __future__ import annotations

import inspect

from fabricops_kit import widgets as widget_package
from fabricops_kit.widgets import shared
from tests.unit.test_widget_author_guardrails import _install_fake_notebook_widgets


LIVE_WIDGETS = {
    "widget_render_data_steward",
    "widget_render_data_agreement",
    "widget_register_data_contract",
    "widget_view_catalogue",
    "widget_enrich_table_metadata",
    "widget_author_guardrails",
    "widget_author_dq_rules",
}


def test_live_widget_inventory_uses_the_canonical_page_composer():
    """Verify every exported live widget is owned by the shared page design."""
    assert set(widget_package.__all__) == LIVE_WIDGETS
    for name in LIVE_WIDGETS:
        module = __import__(f"fabricops_kit.widgets.{name}", fromlist=[name])
        assert "form_page(" in inspect.getsource(module)


def test_live_widgets_do_not_shadow_fabric_display():
    """Keep IPython widget rendering namespaced so Fabric display() stays native."""
    for name in LIVE_WIDGETS:
        module = __import__(f"fabricops_kit.widgets.{name}", fromlist=[name])
        source = inspect.getsource(module)
        assert "from IPython import display as ip" in source
        assert "ip.display(" in source
        assert "from IPython.display import display" not in source
        assert "from IPython import display\n" not in source


def test_authoring_workspace_is_full_width_stable_and_shrinkable(monkeypatch):
    """Verify the reusable landscape workspace keeps stable pane dimensions."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    workspace = shared.authoring_workspace(
        widgets,
        target=[widgets.HTML("target")],
        selection=[widgets.HTML("selection")],
        configuration=[widgets.HTML("configuration")],
    )

    assert workspace.layout.width == "100%"
    assert workspace.layout.min_width == "0"
    assert workspace.layout.max_width == "100%"
    assert workspace.layout.grid_template_columns == (
        "minmax(0, 25fr) minmax(0, 30fr) minmax(0, 45fr)"
    )
    assert len(workspace.children) == 3
    for pane in workspace.children:
        assert pane.layout.width == "100%"
        assert pane.layout.min_width == "0"
        assert pane.layout.max_width == "100%"
        assert pane.layout.height == "560px"
        assert pane.layout.overflow == "auto"


def test_status_and_preview_regions_reserve_bounded_space(monkeypatch):
    """Verify dynamic messages and JSON previews do not drive page jumping."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    status = shared.status_message(widgets)
    preview = shared.preview_region(widgets, widgets.Textarea())

    assert status.layout.min_height == "32px"
    assert status.layout.min_width == "0"
    assert status.layout.max_width == "100%"
    assert preview.layout.height == "180px"
    assert preview.layout.overflow == "auto"
    assert preview.layout.min_width == "0"


def test_dq_dynamic_content_is_updated_inside_one_workspace():
    """Verify DQ rule switching mutates dynamic regions, not the outer page."""
    module = __import__(
        "fabricops_kit.widgets.widget_author_dq_rules", fromlist=["widget_author_dq_rules"]
    )
    source = inspect.getsource(module.widget_author_dq_rules)

    assert source.count("shared.authoring_workspace(") == 1
    assert "parameter_box.children =" in source
    assert "column_box.children =" in source
    assert "ui.children =" not in source
    assert "workspace.children =" not in source
