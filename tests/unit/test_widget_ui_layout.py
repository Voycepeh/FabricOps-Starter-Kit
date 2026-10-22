"""Focused contracts for the shared Fabric notebook widget design system."""

from __future__ import annotations

import ast
import inspect
import re
import types

from fabricops_kit import widgets as widget_package
from fabricops_kit.widgets import shared


def _install_fake_notebook_widgets(monkeypatch):
    """Install minimal widget fakes for shared layout contracts."""

    class Widget:
        def __init__(self, value="", options=(), layout=None, **kwargs):
            self.value = value
            self.options = options
            self.layout = layout or types.SimpleNamespace(display="")

    class Box(Widget):
        def __init__(self, children=None, **kwargs):
            super().__init__(**kwargs)
            self.children = children or []

    widgets = types.SimpleNamespace(
        HTML=Widget,
        Textarea=Widget,
        VBox=Box,
        HBox=Box,
        GridBox=Box,
        Layout=lambda **kwargs: types.SimpleNamespace(**kwargs),
    )
    return widgets


LIVE_WIDGETS = {
    "widget_data_contract",
    "widget_activate_pipeline",
    "widget_render_data_steward",
    "widget_render_data_agreement",
}


def test_live_widget_inventory_uses_the_canonical_page_composer():
    """Verify every exported live widget is owned by the shared page design."""
    assert set(widget_package.__all__) == LIVE_WIDGETS
    for name in LIVE_WIDGETS:
        module = __import__(f"fabricops_kit.widgets.{name}", fromlist=[name])
        assert "form_page(" in inspect.getsource(module)
    pipeline = __import__("fabricops_kit.pipeline.setup_pipeline", fromlist=["setup_pipeline"])
    from fabricops_kit.pipeline.shared import start_pipeline_session
    assert "start_pipeline_session" in inspect.getsource(pipeline)
    assert "form_page(" in inspect.getsource(start_pipeline_session)
    assert "build_live_pipeline_plan" in inspect.getsource(start_pipeline_session)


def test_form_page_is_a_stable_full_width_scrolling_viewport(monkeypatch):
    """Keep long widget content inside a bounded notebook output viewport."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    page = shared.form_page(
        widgets,
        title="Title",
        description="Description",
        children=[widgets.HTML(str(index)) for index in range(100)],
    )

    assert page.layout.width == "100%"
    assert page.layout.min_width == "0"
    assert page.layout.max_width == "100%"
    assert page.layout.height == "720px"
    assert page.layout.overflow == "auto"


def test_live_widgets_avoid_fabric_unsupported_widget_apis():
    """Verify live widget owners do not use APIs unsupported by Fabric notebooks."""
    forbidden = re.compile(r"(?:\bwidgets\.(?:Output|FileUpload|interact|jslink)|\b(?:interact|jslink))\s*\(")
    for name in LIVE_WIDGETS:
        module = __import__(f"fabricops_kit.widgets.{name}", fromlist=[name])
        assert forbidden.search(inspect.getsource(module)) is None, name


def test_live_widgets_preserve_fabric_native_display_resolution():
    """Verify widget rendering cannot shadow Fabric's native bare display function."""
    for name in LIVE_WIDGETS:
        module = __import__(f"fabricops_kit.widgets.{name}", fromlist=[name])
        tree = ast.parse(inspect.getsource(module))
        imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        assert any(
            node.module == "IPython"
            and any(alias.name == "display" and alias.asname == "ip" for alias in node.names)
            for node in imports
        ), name
        assert not any(
            node.module == "IPython.display"
            and any(alias.name == "display" for alias in node.names)
            for node in imports
        ), name
        assert not any(
            node.module == "IPython"
            and any(alias.name == "display" and alias.asname is None for alias in node.names)
            for node in imports
        ), name
        assert not any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "display"
            for node in ast.walk(tree)
        ), name


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


def test_optional_custom_dropdown_starts_blank_and_required_keeps_default(monkeypatch):
    """Optional configured dropdowns should not silently save the first option."""

    class Dropdown:
        def __init__(self, options, value=None, **kwargs):
            values = [
                option[1] if isinstance(option, tuple) and len(option) == 2 else option
                for option in options
            ]
            if value not in values:
                raise ValueError("dropdown value must match an underlying option value")
            self.options = options
            self.value = value

    widgets = types.SimpleNamespace(Dropdown=Dropdown, Layout=lambda **kwargs: kwargs)
    monkeypatch.setattr(shared, "require_ipywidgets", lambda: widgets)

    definitions = [
        {"key": "optional", "type": "dropdown", "required": False, "options": ["ODI", "Faculty"]},
        {
            "key": "defaulted",
            "type": "dropdown",
            "required": False,
            "options": ["ODI", "Faculty"],
            "default": "Faculty",
        },
        {"key": "required", "type": "dropdown", "required": True, "options": ["ODI", "Faculty"]},
    ]
    fields = shared.render_custom_fields(definitions)

    assert shared.collect_custom_fields(definitions, fields) == {
        "optional": "",
        "defaulted": "Faculty",
        "required": "ODI",
    }
    assert fields["optional"].value == ""
    assert fields["optional"].options[0] == ("Select an option", "")
    assert fields["defaulted"].value == "Faculty"
    assert fields["required"].value == "ODI"
    assert fields["required"].options == [
        ("Select an option", ""), ("ODI", "ODI"), ("Faculty", "Faculty")
    ]
    fields["required"].value = ""

    empty_required = shared.render_custom_fields(
        [{"key": "empty", "type": "dropdown", "required": True, "options": []}]
    )
    assert empty_required["empty"].value == ""


def test_custom_dropdown_accepts_plain_and_labelled_options_in_ipywidgets(monkeypatch):
    """Construct the real dropdown with the same options Fabric receives."""
    import ipywidgets

    monkeypatch.setattr(shared, "require_ipywidgets", lambda: ipywidgets)
    definitions = [
        {"key": "group", "type": "dropdown", "options": ["ODI", "Faculty"]},
        {"key": "tier", "type": "dropdown", "required": True,
         "options": [["Tier one", "one"], ["Tier two", "two"]]},
    ]

    fields = shared.render_custom_fields(definitions)

    assert fields["group"].value == ""
    assert fields["group"].options == (("Select an option", ""), ("ODI", "ODI"), ("Faculty", "Faculty"))
    assert fields["tier"].value == "one"
    fields["group"].value = "ODI"
    assert shared.collect_custom_fields(definitions, fields) == {"group": "ODI", "tier": "one"}
