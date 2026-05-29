from datetime import datetime, timezone

import pytest

from fabricops_kit.data_agreement import (
    DEFAULT_SENSITIVITY_LABELS,
    YES_NO_OPTIONS,
    _agreement_widget_specs,
    build_agreement_catalogue_record,
    build_agreement_header_record,
    build_agreement_scope_record,
    commit_agreement_metadata,
    derive_agreement_status,
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
    assert derive_agreement_status("2026-01-02", as_of_date="2026-01-01") == {
        "agreement_status": "Active",
        "status_as_of_date": "2026-01-01",
    }
    assert derive_agreement_status("2026-01-01", as_of_date="2026-01-01")["agreement_status"] == "Active"


def test_derive_agreement_status_returns_inactive_after_expiry_date():
    assert derive_agreement_status("2025-12-31", as_of_date="2026-01-01") == {
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
        build_agreement_header_record(_widget_values(agreement_name=""))


def test_record_builders_add_committed_by_and_committed_at():
    committed_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    record = build_agreement_header_record(
        _widget_values(),
        committed_by="steward@example.com",
        committed_at=committed_at,
    )
    assert record["committed_by"] == "steward@example.com"
    assert record["committed_at"] == "2026-01-01T00:00:00+00:00"


def test_record_builders_include_computed_status_and_status_as_of_date(monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 1, 1, tzinfo=tz)

    import fabricops_kit.data_agreement as data_agreement

    monkeypatch.setattr(data_agreement, "datetime", FixedDatetime)
    record = build_agreement_header_record(_widget_values(expiry_date="2026-01-01"))
    assert record["agreement_status"] == "Active"
    assert record["status_as_of_date"] == "2026-01-01"


def test_renewal_requirement_only_accepts_yes_or_no():
    assert YES_NO_OPTIONS == ["Yes", "No"]
    with pytest.raises(ValueError, match="renewal_required"):
        build_agreement_header_record(_widget_values(renewal_required="Maybe"))


def test_invalid_expiry_date_raises_clear_error():
    with pytest.raises(ValueError, match="expiry_date must be a valid date"):
        build_agreement_header_record(_widget_values(expiry_date="31/12/2026"))


def test_catalogue_and_scope_records_are_audited():
    values = _widget_values()
    catalogue = build_agreement_catalogue_record(values, committed_by="reviewer")
    scope = build_agreement_scope_record(values, committed_by="reviewer")
    assert catalogue["committed_by"] == "reviewer"
    assert catalogue["committed_at"]
    assert catalogue["catalogue_id"] == "agr-001|Source A|orders"
    assert scope["committed_by"] == "reviewer"
    assert scope["committed_at"]
    assert scope["scope_id"] == "agr-001|Reporting team|Dashboard"


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
    header = {"agreement_id": "agr-001", "agreement_status": "Active"}
    catalogue = {"agreement_id": "agr-001"}
    scope = {"agreement_id": "agr-001"}

    summary = commit_agreement_metadata(
        spark=spark,
        header_record=header,
        catalogue_record=catalogue,
        scope_record=scope,
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
