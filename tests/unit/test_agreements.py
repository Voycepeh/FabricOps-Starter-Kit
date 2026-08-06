"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

from types import SimpleNamespace
import ast
import inspect
import sys
import json
import uuid

import pytest

import fabricops_kit.widgets.shared as agreement
import fabricops_kit.widgets.widget_render_data_agreement as agreement_widget
import fabricops_kit.widgets.widget_render_data_steward as steward_widget
from tests.helpers import agreement_config, agreement_row, steward_row

pytestmark = pytest.mark.unit


def test_agreement_metadata_schemas_and_widget_fields_keep_only_supported_business_columns():
    """Verify agreement metadata schemas and widget fields keep only supported business columns."""
    config = agreement_config()

    steward_fields = agreement.get_widget_visible_fields(config, "data_steward_widget")
    agreement_fields = agreement.get_widget_visible_fields(config, "data_agreement_widget")

    assert "recipient" not in agreement_fields
    assert not any(field.startswith("approved_usage_") for field in agreement_fields)
    assert "custom_fields_json" not in steward_fields + agreement_fields
    assert "agreement_id" not in agreement_fields
    assert "effective_from" not in steward_fields
    assert "effective_to" not in steward_fields


def test_steward_and_agreement_create_update_write_append_only_metadata(monkeypatch):
    """Verify steward and agreement create update write append only metadata."""
    audit_columns = agreement.STANDARD_RUNTIME_AUDIT_COLUMNS
    writes = []

    monkeypatch.setattr(agreement_widget, "build_runtime_audit_fields", lambda **kwargs: {field: f"audit:{field}" for field in audit_columns})
    monkeypatch.setattr(steward_widget, "build_runtime_audit_fields", lambda **kwargs: {field: f"audit:{field}" for field in audit_columns})
    monkeypatch.setattr(agreement_widget, "list_data_stewards", lambda *args, **kwargs: [steward_row(), steward_row(steward_id="22222222-2222-4222-8222-222222222222")])
    monkeypatch.setattr(agreement_widget, "_generate_agreement_id", lambda: "33333333-3333-4333-8333-333333333333")
    monkeypatch.setattr(agreement_widget, "write_widget_metadata_row", lambda **kwargs: writes.append(kwargs))
    monkeypatch.setattr(steward_widget, "write_widget_metadata_row", lambda **kwargs: writes.append(kwargs))

    config = agreement_config(metadata_tables={"data_steward": "CUSTOM_STEWARD", "data_agreement": "CUSTOM_AGREEMENT"})
    steward = steward_widget._create_or_update_data_steward(
        spark=object(), config=config, env="dev", values=steward_row(), custom_fields={"group": "Shared Services"}
    )
    created = agreement_widget._create_or_update_data_agreement(
        spark=object(), config=config, env="dev", values=agreement_row(), custom_fields={"consumer_group": "ODI"}
    )
    updated = agreement_widget._create_or_update_data_agreement(
        spark=object(), config=config, env="dev", values=agreement_row(), selected_agreement=created
    )

    assert steward["custom_fields_json"]
    assert created["agreement_id"] == updated["agreement_id"] == "33333333-3333-4333-8333-333333333333"
    assert (created["agreement_version"], updated["agreement_version"]) == ("1.0.0", "1.1.0")
    assert [write["table"] for write in writes] == ["CUSTOM_STEWARD", "CUSTOM_AGREEMENT", "CUSTOM_AGREEMENT"]
    assert all(write["env"] == "dev" for write in writes)


def test_agreement_validation_fails_before_writes(monkeypatch):
    """Verify agreement validation fails before writes."""
    monkeypatch.setattr(agreement_widget, "list_data_stewards", lambda *args, **kwargs: [steward_row(), steward_row(steward_id="22222222-2222-4222-8222-222222222222")])
    monkeypatch.setattr(agreement_widget, "write_widget_metadata_row", lambda **kwargs: pytest.fail("invalid data should not be written"))
    monkeypatch.setattr(steward_widget, "write_widget_metadata_row", lambda **kwargs: pytest.fail("invalid data should not be written"))

    with pytest.raises(ValueError, match="steward_name"):
        steward_widget._create_or_update_data_steward(spark=object(), config=agreement_config(), env="dev", values=steward_row(steward_name=""))


def test_new_and_existing_steward_uuid_identity(monkeypatch):
    """Generate UUID4 identities once and retain them on steward edits."""
    writes = []
    monkeypatch.setattr(steward_widget, "build_runtime_audit_fields", lambda **kwargs: {})
    monkeypatch.setattr(steward_widget, "write_widget_metadata_row", lambda **kwargs: writes.append(kwargs["row"]))

    first = steward_widget._create_or_update_data_steward(
        spark=object(), config=agreement_config(), env="dev", values=steward_row(steward_id="")
    )
    second = steward_widget._create_or_update_data_steward(
        spark=object(), config=agreement_config(), env="dev", values=steward_row(steward_id="")
    )
    edited = steward_widget._create_or_update_data_steward(
        spark=object(), config=agreement_config(), env="dev", values=steward_row(steward_id=first["steward_id"])
    )

    assert uuid.UUID(first["steward_id"]).version == 4
    assert uuid.UUID(second["steward_id"]).version == 4
    assert first["steward_id"] != second["steward_id"]
    assert edited["steward_id"] == first["steward_id"]
    assert all(not row["steward_id"].startswith("STEW-") for row in writes)


def test_agreement_json_validation_and_deterministic_serialization():
    """Accept and round-trip mixed supporting-document location types."""
    rows = [
        {"label": "Web", "location": "  https://example.com/document  "},
        {"label": "Relative file", "location": "Files/governance/document.pdf"},
        {"label": "Table", "location": "Tables/reference_documents"},
        {"label": "ABFSS", "location": "abfss://container@account.dfs.core.windows.net/path/file.pdf"},
        {"label": "Absolute", "location": "/workspace/default_lakehouse/Files/document.pdf"},
        {"label": "", "location": ""},
    ]
    documents = agreement_widget._serialize_supporting_documents(rows)
    expected = [{**row, "location": row["location"].strip()} for row in rows[:-1]]
    assert json.loads(documents) == expected
    assert agreement_widget._deserialize_supporting_documents(documents) == expected
    assert agreement_widget._serialize_approved_usage(
        ["external", "internal"], ["internal", "research", "external"]
    ) == '["internal","external"]'
    with pytest.raises(ValueError, match="both a label and a location"):
        agreement_widget._serialize_supporting_documents([{"label": "Request", "location": ""}])
    with pytest.raises(ValueError, match="both a label and a location"):
        agreement_widget._serialize_supporting_documents([{"label": "", "location": "Files/request.pdf"}])
    with pytest.raises(ValueError, match="At least one"):
        agreement_widget._serialize_approved_usage([], ["internal"])
    with pytest.raises(ValueError, match="unconfigured"):
        agreement_widget._deserialize_approved_usage('["retired"]', ["internal"])


def test_agreement_two_party_append_only_identity_and_no_change(monkeypatch):
    """Preserve agreement UUIDs while appending changed minor versions."""
    writes = []
    stored = []
    stewards = [
        steward_row(),
        steward_row(steward_id="22222222-2222-4222-8222-222222222222"),
    ]
    monkeypatch.setattr(agreement_widget, "build_runtime_audit_fields", lambda **kwargs: {field: field for field in agreement.STANDARD_RUNTIME_AUDIT_COLUMNS})
    monkeypatch.setattr(agreement_widget, "list_data_stewards", lambda *args, **kwargs: stewards)
    monkeypatch.setattr(agreement_widget, "list_all_data_agreement_rows", lambda *args, **kwargs: list(stored))
    monkeypatch.setattr(agreement_widget, "write_widget_metadata_row", lambda **kwargs: (writes.append(kwargs), stored.append(kwargs["row"])))

    created = agreement_widget._create_or_update_data_agreement(
        spark=object(), config=agreement_config(), env="dev", values=agreement_row()
    )
    unchanged = agreement_widget._create_or_update_data_agreement(
        spark=object(), config=agreement_config(), env="dev", values=agreement_row(), selected_agreement=created
    )
    changed_values = agreement_row(approved_usage=["internal single domain", "research"])
    updated = agreement_widget._create_or_update_data_agreement(
        spark=object(), config=agreement_config(), env="dev", values=changed_values, selected_agreement=created
    )
    separate = agreement_widget._create_or_update_data_agreement(
        spark=object(), config=agreement_config(), env="dev", values=agreement_row(agreement_name="Separate")
    )

    assert uuid.UUID(created["agreement_id"]).version == 4
    assert created["agreement_version"] == "1.0.0"
    assert unchanged["_fabricops_no_change"] is True
    assert updated["agreement_id"] == created["agreement_id"]
    assert updated["agreement_version"] == "1.1.0"
    assert separate["agreement_id"] != created["agreement_id"]
    assert len(writes) == 3
    assert "steward_id" not in updated
    assert set(writes[0]["row"]) == set(agreement.DATA_AGREEMENT_FIELDS)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"provider_steward_id": ""}, "provider_steward_id"),
        ({"recipient_steward_id": ""}, "recipient_steward_id"),
        ({"provider_steward_id": "99999999-9999-4999-8999-999999999999"}, "provider_steward_id"),
        ({"recipient_steward_id": "99999999-9999-4999-8999-999999999999"}, "recipient_steward_id"),
        ({"recipient_steward_id": "11111111-1111-4111-8111-111111111111"}, "must be different"),
    ],
)
def test_agreement_requires_two_different_active_stewards(monkeypatch, overrides, message):
    """Require distinct active stewards in both agreement roles."""
    monkeypatch.setattr(
        agreement_widget,
        "list_data_stewards",
        lambda *args, **kwargs: [
            steward_row(), steward_row(steward_id="22222222-2222-4222-8222-222222222222")
        ],
    )
    monkeypatch.setattr(agreement_widget, "write_widget_metadata_row", lambda **kwargs: pytest.fail("must not write"))
    with pytest.raises(ValueError, match=message):
        agreement_widget._create_or_update_data_agreement(
            spark=object(), config=agreement_config(), env="dev", values=agreement_row(**overrides)
        )


def test_stale_agreement_modules_are_removed_and_not_imported():
    """Verify stale agreement modules are removed from source ownership."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    assert not (root / "src" / "fabricops_kit" / "data_agreement.py").exists()
    assert not (root / "src" / "fabricops_kit" / "agreement_selection_state.py").exists()

    scanned = [root / "src", root / "templates", root / "docs"]
    offenders = []
    for base in scanned:
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".md", ".yml", ".yaml", ".json", ".ipynb"}:
                continue
            text = path.read_text(encoding="utf-8")
            for fragment in (
                "fabricops_kit.data_agreement",
                "fabricops_kit.agreement_selection_state",
                "from .data_agreement",
                "agreement_selection_state import",
            ):
                if fragment in text:
                    offenders.append(f"{path.relative_to(root)} imports {fragment}")
    assert offenders == []


class _FakeWidget:
    """Minimal ipywidgets-compatible test double."""

    def __init__(self, value=None, options=None, children=None, **kwargs):
        if children is None and isinstance(value, (list, tuple)):
            children, value = value, None
        self.value = value
        self.options = options or []
        self.children = children or []
        self.callbacks = []
        self.click_callbacks = []
        self.disabled = False
        self.description = kwargs.get("description", "")
        self.placeholder = kwargs.get("placeholder", "")
        self.layout = kwargs.get("layout")
        self.selected_index = 0
        self.titles = {}

    def set_title(self, index, title):
        """Record container titles."""
        self.titles[index] = title

    def observe(self, callback, names=None):
        """Record observer callbacks."""
        self.callbacks.append(callback)

    def on_click(self, callback):
        """Record click callbacks."""
        self.click_callbacks.append(callback)

    def clear_output(self, wait=False):
        """Match Output.clear_output."""

    def __enter__(self):
        """Enter output context."""
        return self

    def __exit__(self, exc_type, exc, tb):
        """Exit output context."""
        return False


class _FakeWidgets:
    """Minimal widget module used by public render tests."""

    Text = _FakeWidget
    Select = _FakeWidget
    HTML = _FakeWidget
    Button = _FakeWidget
    Output = _FakeWidget
    VBox = _FakeWidget
    HBox = _FakeWidget
    GridBox = _FakeWidget
    Tab = _FakeWidget
    Textarea = _FakeWidget
    DatePicker = _FakeWidget
    Checkbox = _FakeWidget

    class Dropdown(_FakeWidget):
        """Dropdown test double that validates underlying option values."""

        def __init__(self, value=None, options=None, **kwargs):
            option_values = [
                option[1] if isinstance(option, tuple) and len(option) == 2 else option
                for option in (options or [])
            ]
            if value is not None and value not in option_values:
                raise ValueError("dropdown value must match an underlying option value")
            super().__init__(value=value, options=options, **kwargs)

    class Layout:
        """Minimal layout test double that rejects unsupported ipywidgets traits."""

        _SUPPORTED_TRAITS = {
            "align_items",
            "border",
            "display",
            "flex",
            "flex_flow",
            "font_family",
            "gap",
            "grid_gap",
            "grid_template_columns",
            "height",
            "justify_content",
            "max_height",
            "max_width",
            "min_width",
            "overflow",
            "padding",
            "width",
        }

        def __init__(self, **kwargs):
            unknown = set(kwargs) - self._SUPPORTED_TRAITS
            if unknown:
                raise TypeError(f"Unsupported fake Layout traits: {sorted(unknown)}")
            self.kwargs = kwargs


@pytest.mark.parametrize(
    ("options", "supplied_value", "expected_value"),
    [
        (["Owner", "Steward"], "", "Owner"),
        ([("Data Owner", "owner"), ("Data Steward", "steward")], "", "owner"),
        (["Owner", "Steward"], "Steward", "Steward"),
        ([("Data Owner", "owner"), ("Data Steward", "steward")], "steward", "steward"),
        ([("Data Owner", "owner"), ("Data Steward", "steward")], "invalid", "owner"),
        ([], "", None),
    ],
)
def test_standard_widget_selects_underlying_dropdown_option_values(
    monkeypatch, options, supplied_value, expected_value
):
    """Select valid option values and fall back to the first underlying value."""
    monkeypatch.setattr(agreement, "require_ipywidgets", lambda: _FakeWidgets)

    dropdown = agreement.standard_widget("steward_role", supplied_value, options=options)

    assert dropdown.options == options
    assert dropdown.value == expected_value


def test_public_agreement_and_steward_widgets_render_independent_workflows(monkeypatch):
    """Verify public agreement and steward widgets render without the deleted shared workflow."""
    config = agreement_config()
    spark = object()

    monkeypatch.setattr(agreement_widget, "resolve_fabric_context", lambda context=None: (config, "dev", {}))
    monkeypatch.setattr(steward_widget, "resolve_fabric_context", lambda context=None: (config, "dev", {}))
    monkeypatch.setitem(sys.modules, "IPython", SimpleNamespace(display=SimpleNamespace(display=lambda value: None)))
    monkeypatch.setattr(agreement, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(steward_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "list_data_agreements", lambda *args, **kwargs: [agreement_row(agreement_id="33333333-3333-4333-8333-333333333333", agreement_version="1.0.0", supporting_documents_json="[]", approved_usage_json='["internal"]', custom_fields_json='{"consumer_group":"ODI"}')])
    monkeypatch.setattr(agreement_widget, "list_data_stewards", lambda *args, **kwargs: [steward_row(), steward_row(steward_id="22222222-2222-4222-8222-222222222222")])
    monkeypatch.setattr(steward_widget, "list_data_stewards", lambda *args, **kwargs: [steward_row(custom_fields_json='{"group":"Shared Services"}')])

    agreement_controls = agreement_widget.widget_render_data_agreement(spark=spark)
    steward_controls = steward_widget.widget_render_data_steward(spark=spark)

    assert agreement_controls["identity_context"] is not None
    assert agreement_controls["provider_steward_selector"].options
    assert agreement_controls["recipient_steward_selector"].options
    assert "recipient" not in agreement_controls["fields"]
    form_body = agreement_controls["container"].children[1]
    form_flow = form_body.children[0]
    assert len(form_flow.children) == 5
    agreement_header = agreement_controls["container"].children[0]
    assert "Data Agreement Creation Widget" in agreement_header.value
    assert "Governance-level agreement" in agreement_header.value
    assert "Specific datasets and technical delivery terms" in agreement_header.value
    assert "schema versions" not in agreement_header.value
    assert "background:#0f6cbd" in agreement_header.value
    assert agreement_controls["container"].layout.kwargs["width"] == "100%"
    assert "widgets.Tab" not in inspect.getsource(agreement_widget.widget_render_data_agreement)
    steward_section = form_flow.children[2]
    steward_panels_row = steward_section.children[1]
    assert len(steward_panels_row.children) == 2
    for panel, selector in zip(
        steward_panels_row.children,
        (agreement_controls["provider_steward_selector"], agreement_controls["recipient_steward_selector"]),
        strict=True,
    ):
        assert panel.layout.kwargs["width"] == "49%"
        search_selector_summary = panel.children[1]
        assert len(search_selector_summary.children) == 3
        assert search_selector_summary.children[1] is selector
    assert len(agreement_controls["supporting_documents"]) == 1
    document_container = agreement_controls["supporting_documents"][0]["container"]
    assert [child.value for child in document_container.children if isinstance(child.value, str) and "Document" in child.value] == [
        "<b>Document name</b>", "<b>Document link</b>"
    ]
    root = agreement_controls["container"]
    documents_container = agreement_controls["supporting_documents_container"]
    agreement_controls["supporting_documents"][0]["label"].value = "First"
    agreement_controls["add_supporting_document_button"].click_callbacks[0](None)
    agreement_controls["supporting_documents"][1]["label"].value = "Second"
    agreement_controls["supporting_documents"][0]["remove"].click_callbacks[0](None)
    assert agreement_controls["container"] is root
    assert agreement_controls["supporting_documents_container"] is documents_container
    assert agreement_controls["supporting_documents"][0]["label"].value == "Second"
    assert steward_controls["identity_context"] is None
    assert steward_controls["fields"]["steward_role"].options
    assert steward_controls["fields"]["steward_role"].value == "Data Owner"
    assert "effective_from" not in steward_controls["fields"]
    assert "effective_to" not in steward_controls["fields"]
    steward_header = steward_controls["container"].children[0]
    assert "Data Steward" in steward_header.value
    assert "Data Steward Creation Widget" not in steward_header.value
    assert "background:#0f6cbd" in steward_header.value


def test_steward_widget_blocks_missing_required_fields_before_persistence(monkeypatch, capsys):
    """List friendly missing fields without reaching steward persistence."""
    config = agreement_config()
    monkeypatch.setattr(steward_widget, "resolve_fabric_context", lambda context=None: (config, "dev", {}))
    monkeypatch.setitem(sys.modules, "IPython", SimpleNamespace(display=SimpleNamespace(display=lambda value: None)))
    monkeypatch.setattr(agreement, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(steward_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(steward_widget, "list_data_stewards", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        steward_widget,
        "_create_or_update_data_steward",
        lambda **kwargs: pytest.fail("missing required fields must not reach persistence"),
    )

    controls = steward_widget.widget_render_data_steward(spark=object())
    assert controls["save_button"].disabled is True
    controls["fields"]["steward_name"].value = "  "
    controls["fields"]["contact"].value = None
    controls["save_button"].click_callbacks[0](None)

    message = capsys.readouterr().out
    assert message == ""
    assert controls["status"].value == (
        "Data steward was not saved. Complete the following required fields: "
        "Steward name, Contact."
    )


def test_widget_metadata_write_uses_canonical_explicit_steward_schema(monkeypatch):
    """Create valid steward frames with the canonical schema, including custom table names."""
    created = {}

    class Spark:
        def createDataFrame(self, rows, schema=None):  # noqa: N802
            created.update(rows=rows, schema=schema)
            return "frame"

    monkeypatch.setattr(agreement, "write_lakehouse_table_core", lambda *args, **kwargs: created.update(table=args[1]))
    config = agreement_config(metadata_tables={"data_steward": "CUSTOM_STEWARD", "data_agreement": "CUSTOM_AGREEMENT"})

    agreement.write_widget_metadata_row(
        spark=Spark(), config=config, env="dev", table="CUSTOM_STEWARD", row=steward_row()
    )

    assert created["schema"].fieldNames() == [
        "steward_id", "steward_name", "steward_role", "contact", "is_active",
        "custom_fields_json", *agreement.STANDARD_RUNTIME_AUDIT_COLUMNS,
    ]
    assert created["table"] == "CUSTOM_STEWARD"


def test_agreement_widget_always_renders_mandatory_stewards(monkeypatch):
    """Render and require both steward roles when visible columns omit them."""
    config = agreement_config()
    config.data_agreement_config.data_agreement_widget["visible_columns"] = [
        "agreement_name", "domain", "start_date", "expiry_date", "business_purpose"
    ]
    monkeypatch.setattr(agreement_widget, "resolve_fabric_context", lambda context=None: (config, "dev", {}))
    monkeypatch.setitem(sys.modules, "IPython", SimpleNamespace(display=SimpleNamespace(display=lambda value: None)))
    monkeypatch.setattr(agreement, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(agreement_widget, "list_data_stewards", lambda *args, **kwargs: [
        steward_row(), steward_row(steward_id="22222222-2222-4222-8222-222222222222")
    ])
    monkeypatch.setattr(agreement_widget, "list_all_data_agreement_rows", lambda *args, **kwargs: [])
    monkeypatch.setattr(agreement_widget, "write_widget_metadata_row", lambda **kwargs: pytest.fail("must not write"))

    controls = agreement_widget.widget_render_data_agreement(spark=object())

    assert controls["provider_steward_selector"].options
    assert controls["recipient_steward_selector"].options
    controls["provider_steward_selector"].value = ""
    controls["recipient_steward_selector"].value = ""
    controls["approved_usage_checkboxes"]["internal cross domain"].value = True
    controls["save_button"].click_callbacks[0](None)
    assert "provider_steward_id" in controls["status"].value
    assert "recipient_steward_id" in controls["status"].value


@pytest.mark.parametrize(
    ("stewards", "save_disabled"),
    [
        ([], True),
        ([steward_row()], True),
        ([steward_row(), steward_row()], True),
        ([steward_row(), steward_row(steward_id="")], True),
        ([steward_row(), steward_row(steward_id="22222222-2222-4222-8222-222222222222")], False),
    ],
)
def test_agreement_widget_disables_save_until_two_active_stewards_exist(monkeypatch, stewards, save_disabled):
    """Keep the workflow visible while enforcing its steward prerequisite."""
    config = agreement_config()
    monkeypatch.setattr(agreement_widget, "resolve_fabric_context", lambda context=None: (config, "dev", {}))
    monkeypatch.setitem(sys.modules, "IPython", SimpleNamespace(display=SimpleNamespace(display=lambda value: None)))
    monkeypatch.setattr(agreement, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(agreement_widget, "list_data_stewards", lambda *args, **kwargs: stewards)

    controls = agreement_widget.widget_render_data_agreement(spark=object())

    assert controls["container"] is not None
    assert controls["save_button"].disabled is save_disabled
    assert ("At least two distinct active data stewards are required" in controls["status"].value) is save_disabled


def test_agreement_widget_refresh_updates_steward_prerequisite(monkeypatch):
    """Recalculate Save state and preserve only active selections on refresh."""
    config = agreement_config()
    active_rows = [steward_row()]
    second = steward_row(steward_id="22222222-2222-4222-8222-222222222222")
    monkeypatch.setattr(agreement_widget, "resolve_fabric_context", lambda context=None: (config, "dev", {}))
    monkeypatch.setitem(sys.modules, "IPython", SimpleNamespace(display=SimpleNamespace(display=lambda value: None)))
    monkeypatch.setattr(agreement, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(agreement_widget, "list_data_stewards", lambda *args, **kwargs: list(active_rows))

    controls = agreement_widget.widget_render_data_agreement(spark=object())
    active_rows.append(second)
    controls["provider_steward_selector"].value = steward_row()["steward_id"]
    controls["recipient_steward_selector"].value = second["steward_id"]
    controls["refresh_stewards_button"].click_callbacks[0](None)

    assert controls["save_button"].disabled is False
    assert controls["provider_steward_selector"].value == steward_row()["steward_id"]
    assert controls["recipient_steward_selector"].value == second["steward_id"]

    active_rows[:] = [second]
    controls["refresh_stewards_button"].click_callbacks[0](None)

    assert controls["save_button"].disabled is True
    assert controls["provider_steward_selector"].value == ""
    assert controls["recipient_steward_selector"].value == second["steward_id"]
    assert "At least two distinct active data stewards are required" in controls["status"].value


def test_widget_architecture_cleanup_contracts_hold():
    """Verify deleted workflow containers and private shared imports stay removed."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    agreement_source = (root / "src" / "fabricops_kit" / "widgets" / "widget_render_data_agreement.py").read_text(encoding="utf-8")
    steward_source = (root / "src" / "fabricops_kit" / "widgets" / "widget_render_data_steward.py").read_text(encoding="utf-8")
    shared_source = (root / "src" / "fabricops_kit" / "widgets" / "shared.py").read_text(encoding="utf-8")

    assert "render_maintenance_widget_shared_workflow" not in agreement_source + steward_source + shared_source
    assert "def _render_data_agreement_widget" not in agreement_source
    assert "def _render_data_steward_widget" not in steward_source
    assert "_create_or_update_data_steward" not in agreement_source
    assert "_create_or_update_data_agreement" not in steward_source
    assert "%" not in steward_source

    for source in (agreement_source, steward_source):
        tree = ast.parse(source)
        public_functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name.startswith("widget_render_data_")]
        assert len(public_functions) == 1
        public_names = {node.name for node in ast.walk(public_functions[0]) if isinstance(node, ast.FunctionDef)}
        assert "_save" in public_names
        assert "_populate" in public_names

        private_shared_imports = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == "fabricops_kit.widgets.shared":
                private_shared_imports.extend(alias.name for alias in node.names if alias.name.startswith("_"))
        assert private_shared_imports == []


def test_canonical_agreement_schema_exact_order_and_nullability():
    """Keep the canonical agreement schema ordered and correctly nullable."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    schema = metadata_table_schema_registry()[agreement.DATA_AGREEMENT_TABLE]
    expected = [
        "agreement_id", "agreement_version", "agreement_name", "domain",
        "provider_steward_id", "recipient_steward_id", "start_date",
        "expiry_date", "business_purpose", "supporting_documents_json",
        "approved_usage_json", "custom_fields_json", *agreement.STANDARD_RUNTIME_AUDIT_COLUMNS,
    ]
    assert schema.fieldNames() == expected
    fields = {field.name: field for field in schema.fields}
    assert not fields["provider_steward_id"].nullable
    assert not fields["recipient_steward_id"].nullable
    assert fields["supporting_documents_json"].nullable
    assert not fields["approved_usage_json"].nullable
    assert "steward_id" not in fields


def test_canonical_steward_schema_identity_and_existing_order():
    """Require the steward UUID while preserving all other schema fields."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    schema = metadata_table_schema_registry()[agreement.DATA_STEWARD_TABLE]
    assert schema.fieldNames() == [
        "steward_id", "steward_name", "steward_role", "contact", "is_active",
        "custom_fields_json", *agreement.STANDARD_RUNTIME_AUDIT_COLUMNS,
    ]
    assert "effective_from" not in schema.fieldNames()
    assert "effective_to" not in schema.fieldNames()
    steward_id = next(field for field in schema.fields if field.name == "steward_id")
    assert type(steward_id.dataType).__name__ == "StringType"
    assert steward_id.nullable is False
    assert all(field.nullable for field in schema.fields[1:6])
