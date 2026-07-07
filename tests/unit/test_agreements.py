"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

from types import SimpleNamespace
import sys

import pytest

import fabricops_kit.widgets.shared as agreement
import fabricops_kit.widgets.widget_render_data_agreement as agreement_widget
import fabricops_kit.widgets.widget_render_data_steward as steward_widget
import importlib

evidence = importlib.import_module("fabricops_kit.widgets.widget_render_agreement_evidence")
from tests.helpers import agreement_config, agreement_row, steward_row

pytestmark = pytest.mark.unit


def test_agreement_metadata_schemas_and_widget_fields_keep_only_supported_business_columns():
    """Verify agreement metadata schemas and widget fields keep only supported business columns."""
    config = agreement_config()

    steward_fields = agreement._get_widget_visible_fields(config, "data_steward_widget")
    agreement_fields = agreement._get_widget_visible_fields(config, "data_agreement_widget")

    assert set(agreement.DATA_AGREEMENT_EVIDENCE_FIELDS).issuperset({"agreement_id", "contract_version", "file_path"})
    assert {"recipient", "approved_usage_internal", "approved_usage_external", "approved_usage_research"}.issubset(agreement_fields)
    assert "approved_usage" not in agreement_fields
    assert "custom_fields_json" not in steward_fields + agreement_fields
    assert "agreement_id" not in agreement_fields


def test_steward_and_agreement_create_update_write_append_only_metadata(monkeypatch):
    """Verify steward and agreement create update write append only metadata."""
    audit_columns = agreement.STANDARD_RUNTIME_AUDIT_COLUMNS
    writes = []

    monkeypatch.setattr(agreement_widget, "build_runtime_audit_fields", lambda **kwargs: {field: f"audit:{field}" for field in audit_columns})
    monkeypatch.setattr(steward_widget, "build_runtime_audit_fields", lambda **kwargs: {field: f"audit:{field}" for field in audit_columns})
    monkeypatch.setattr(agreement_widget, "_list_data_stewards", lambda *args, **kwargs: [steward_row()])
    monkeypatch.setattr(agreement_widget, "_generate_agreement_id", lambda *args, **kwargs: "DA-GENERATED")
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
    assert created["agreement_id"] == updated["agreement_id"] == "DA-GENERATED"
    assert (created["contract_version"], updated["contract_version"]) == ("1.0.0", "1.1.0")
    assert [write["table"] for write in writes] == ["CUSTOM_STEWARD", "CUSTOM_AGREEMENT", "CUSTOM_AGREEMENT"]
    assert all(write["env"] == "dev" for write in writes)


def test_agreement_validation_and_evidence_path_parsing_fail_before_writes(monkeypatch):
    """Verify agreement validation and evidence path parsing fail before writes."""
    monkeypatch.setattr(agreement_widget, "_list_data_stewards", lambda *args, **kwargs: [steward_row()])
    monkeypatch.setattr(agreement_widget, "write_widget_metadata_row", lambda **kwargs: pytest.fail("invalid data should not be written"))
    monkeypatch.setattr(steward_widget, "write_widget_metadata_row", lambda **kwargs: pytest.fail("invalid data should not be written"))

    with pytest.raises(ValueError, match="steward_name"):
        steward_widget._create_or_update_data_steward(spark=object(), config=agreement_config(), env="dev", values=steward_row(steward_name=""))
    with pytest.raises(ValueError, match="recipient"):
        agreement_widget._create_or_update_data_agreement(spark=object(), config=agreement_config(), env="dev", values=agreement_row(recipient=""))

    references = evidence._prepare_evidence_file_references("- Files/fabricops/evidence/a.pdf\n* Files/fabricops/evidence/b.docx\n")
    assert [item["file_name"] for item in references] == ["a.pdf", "b.docx"]
    with pytest.raises(ValueError, match="Files/"):
        evidence._prepare_evidence_file_references("Files/fabricops/evidence/a.pdf\n/tmp/local.pdf")


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
        self.value = value
        self.options = options or []
        self.children = children or []
        self.callbacks = []
        self.click_callbacks = []
        self.disabled = False
        self.description = kwargs.get("description", "")
        self.placeholder = kwargs.get("placeholder", "")

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
    Textarea = _FakeWidget
    DatePicker = _FakeWidget
    Checkbox = _FakeWidget
    Dropdown = _FakeWidget

    class Layout:
        """Minimal layout test double."""

        def __init__(self, **kwargs):
            self.kwargs = kwargs


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
    monkeypatch.setattr(agreement_widget, "list_data_agreements", lambda *args, **kwargs: [agreement_row(agreement_id="DA-1", contract_version="1.0.0", custom_fields_json='{"consumer_group":"ODI"}')])
    monkeypatch.setattr(agreement_widget, "_list_data_stewards", lambda *args, **kwargs: [steward_row()])
    monkeypatch.setattr(steward_widget, "_list_data_stewards", lambda *args, **kwargs: [steward_row(custom_fields_json='{"group":"Shared Services"}')])

    agreement_controls = agreement_widget.widget_render_data_agreement(spark=spark)
    steward_controls = steward_widget.widget_render_data_steward(spark=spark)

    assert agreement_controls["identity_context"] is not None
    assert agreement_controls["fields"]["steward_id"].options
    assert steward_controls["identity_context"] is None
    assert steward_controls["fields"]["steward_role"].options


def test_widget_architecture_cleanup_contracts_hold():
    """Verify deleted generic workflow and cross-owned create/update helpers stay removed."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    agreement_source = (root / "src" / "fabricops_kit" / "widgets" / "widget_render_data_agreement.py").read_text(encoding="utf-8")
    steward_source = (root / "src" / "fabricops_kit" / "widgets" / "widget_render_data_steward.py").read_text(encoding="utf-8")
    shared_source = (root / "src" / "fabricops_kit" / "widgets" / "shared.py").read_text(encoding="utf-8")

    assert "render_maintenance_widget_shared_workflow" not in agreement_source + steward_source + shared_source
    assert "_create_or_update_data_steward" not in agreement_source
    assert "_create_or_update_data_agreement" not in steward_source
    assert "%" not in steward_source
