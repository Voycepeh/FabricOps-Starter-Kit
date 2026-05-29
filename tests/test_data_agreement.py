from datetime import datetime

import pytest

from fabricops_kit.data_agreement import (
    DEFAULT_SENSITIVITY_LABELS,
    YES_NO_OPTIONS,
    _agreement_widget_specs,
    _derive_agreement_status,
    collect_agreement_metadata,
    commit_agreement_metadata,
)


def _widget_values(**overrides):
    values = {
        "agreement_id": "agr-001",
        "agreement_name": "Example sharing agreement",
        "data_steward_name": "Data Steward",
        "data_steward_email": "steward@example.com",
        "department": "Analytics",
        "business_owner": "Business Owner",
        "scope_of_use": "Approved analytics use only.",
        "purpose": "Support approved reporting.",
        "start_date": "2026-01-01",
        "expiry_date": "2026-12-31",
        "renewal_required": "Yes",
        "sensitivity_label": "Public",
        "source_system": "Source A",
        "source_database": "source_db",
        "source_schema": "dbo",
        "source_table": "orders",
        "business_name": "Orders",
        "business_description": "Order records.",
        "data_owner": "Owner",
        "contains_sensitive_data": "No",
        "intended_use": "Reporting",
        "allowed_consumer": "Reporting team",
        "allowed_consumer_type": "Team",
        "allowed_output_type": "Dashboard",
        "dashboard_allowed": "Yes",
        "data_dump_allowed": "No",
        "self_service_extract_allowed": "No",
        "refresh_frequency": "Monthly",
        "retention_expectation": "Retain according to policy.",
        "special_conditions": "None.",
        "commit_note": "Approved by steward.",
    }
    values.update(overrides)
    return values


def test_derive_agreement_status_returns_active_before_or_on_expiry_date():
    assert _derive_agreement_status("2026-01-02", as_of_date="2026-01-01") == {
        "agreement_status": "Active",
        "status_as_of_date": "2026-01-01",
    }
    assert _derive_agreement_status("2026-01-01", as_of_date="2026-01-01")["agreement_status"] == "Active"


def test_derive_agreement_status_returns_inactive_after_expiry_date():
    assert _derive_agreement_status("2025-12-31", as_of_date="2026-01-01") == {
        "agreement_status": "Inactive",
        "status_as_of_date": "2026-01-01",
    }


def test_sensitivity_labels_default_to_public_confidential_restricted():
    specs = {spec["name"]: spec for spec in _agreement_widget_specs()}
    assert specs["sensitivity_label"]["kind"] == "dropdown"
    assert specs["sensitivity_label"]["options"] == DEFAULT_SENSITIVITY_LABELS


def test_custom_sensitivity_labels_are_used():
    specs = {spec["name"]: spec for spec in _agreement_widget_specs(sensitivity_labels=["Internal", "Secret"])}
    assert specs["sensitivity_label"]["options"] == ["Internal", "Secret"]


def test_department_and_source_system_dropdown_only_when_options_are_passed():
    free_text_specs = {spec["name"]: spec for spec in _agreement_widget_specs(departments=None, source_systems=None)}
    assert free_text_specs["department"]["kind"] == "text"
    assert free_text_specs["source_system"]["kind"] == "text"

    dropdown_specs = {
        spec["name"]: spec
        for spec in _agreement_widget_specs(departments=["Finance"], source_systems=["ERP"])
    }
    assert dropdown_specs["department"]["kind"] == "dropdown"
    assert dropdown_specs["department"]["options"] == ["Finance"]
    assert dropdown_specs["source_system"]["kind"] == "dropdown"
    assert dropdown_specs["source_system"]["options"] == ["ERP"]


def test_missing_required_agreement_fields_raise_clear_error():
    with pytest.raises(ValueError, match=r"Missing required agreement field\(s\): agreement_name"):
        collect_agreement_metadata(widget_values=_widget_values(agreement_name=""))


def test_collect_agreement_metadata_adds_committed_by_and_committed_at():
    metadata = collect_agreement_metadata(
        widget_values=_widget_values(),
        committed_by="steward@example.com",
        committed_at="2026-01-01T00:00:00+00:00",
    )
    record = metadata["header_record"]
    assert record["committed_by"] == "steward@example.com"
    assert record["committed_at"] == "2026-01-01T00:00:00+00:00"


def test_record_builders_include_computed_status_and_status_as_of_date(monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 1, 1, tzinfo=tz)

    import fabricops_kit.data_agreement as data_agreement

    monkeypatch.setattr(data_agreement, "datetime", FixedDatetime)
    metadata = collect_agreement_metadata(widget_values=_widget_values(expiry_date="2026-01-01"))
    assert metadata["header_record"]["agreement_status"] == "Active"
    assert metadata["header_record"]["status_as_of_date"] == "2026-01-01"


def test_renewal_requirement_only_accepts_yes_or_no():
    assert YES_NO_OPTIONS == ["Yes", "No"]
    with pytest.raises(ValueError, match="renewal_required"):
        collect_agreement_metadata(widget_values=_widget_values(renewal_required="Maybe"))


def test_invalid_expiry_date_raises_clear_error():
    with pytest.raises(ValueError, match="expiry_date must be a valid date"):
        collect_agreement_metadata(widget_values=_widget_values(expiry_date="31/12/2026"))


def test_catalogue_and_scope_records_are_audited():
    metadata = collect_agreement_metadata(widget_values=_widget_values(), committed_by="reviewer")
    catalogue = metadata["catalogue_record"]
    scope = metadata["scope_record"]
    assert catalogue["committed_by"] == "reviewer"
    assert catalogue["committed_at"]
    assert catalogue["catalogue_id"] == "agr-001|Source A|orders"
    assert scope["committed_by"] == "reviewer"
    assert scope["committed_at"]
    assert scope["scope_id"] == "agr-001|Reporting team|Dashboard"


def test_collect_agreement_metadata_builds_records_with_shared_audit_fields():
    metadata = collect_agreement_metadata(
        widget_values=_widget_values(),
        committed_by="reviewer",
        committed_at="2026-01-02T03:04:05+00:00",
        runtime_context={"notebook_name": "01_da_example"},
    )

    assert set(metadata) == {"header_record", "catalogue_record", "scope_record", "summary"}
    assert metadata["summary"] == {
        "agreement_id": "agr-001",
        "agreement_status": "Active",
        "expiry_date": "2026-12-31",
        "status_as_of_date": metadata["header_record"]["status_as_of_date"],
        "committed_by": "reviewer",
        "committed_at": "2026-01-02T03:04:05+00:00",
        "tables_updated": [],
    }
    committed_values = {
        metadata["header_record"]["committed_at"],
        metadata["catalogue_record"]["committed_at"],
        metadata["scope_record"]["committed_at"],
    }
    assert committed_values == {"2026-01-02T03:04:05+00:00"}
    assert metadata["catalogue_record"]["committed_by"] == "reviewer"
    assert metadata["scope_record"]["committed_by"] == "reviewer"


class _DummyWriter:
    def __init__(self, writes):
        self._writes = writes
        self._format = None
        self._mode = None

    def format(self, value):
        self._format = value
        return self

    def mode(self, value):
        self._mode = value
        return self

    def saveAsTable(self, table_name):
        self._writes.append(("table", table_name, self._format, self._mode))

    def save(self, path):
        self._writes.append(("path", path, self._format, self._mode))


class _DummyDataFrame:
    def __init__(self, writes):
        self.write = _DummyWriter(writes)


class _DummySpark:
    def __init__(self):
        self.writes = []

    def createDataFrame(self, rows):
        assert rows
        return _DummyDataFrame(self.writes)


def test_commit_agreement_metadata_uses_lakehouse_safe_default_table_names():
    spark = _DummySpark()
    agreement_metadata = {
        "header_record": {"agreement_id": "agr-001", "agreement_status": "Active"},
        "catalogue_record": {"agreement_id": "agr-001"},
        "scope_record": {"agreement_id": "agr-001"},
    }

    summary = commit_agreement_metadata(
        spark=spark,
        agreement_metadata=agreement_metadata,
    )

    assert summary["tables_updated"] == [
        "METADATA_AGREEMENT_HEADER",
        "METADATA_AGREEMENT_CATALOGUE",
        "METADATA_AGREEMENT_SCOPE",
    ]
    assert [write[1] for write in spark.writes] == summary["tables_updated"]


def test_commit_agreement_metadata_normalizes_custom_prefix_to_safe_names():
    summary = commit_agreement_metadata(
        spark=_DummySpark(),
        header_record={"agreement_id": "agr-001"},
        table_prefix="metadata.custom",
    )

    assert summary["tables_updated"] == ["METADATA_CUSTOM_AGREEMENT_HEADER"]
