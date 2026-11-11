"""File contract identities preserve selector scope without artificial Table IDs."""
import json
from copy import deepcopy

import pytest

from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.data_contract.shared import file_source_identity, validate_contract_source


def source(path="incoming/*.csv", **changes):
    """Return a physical file selector suitable for Governance review."""
    return file_source_identity(workspace_id="WORKSPACE", item_id="ITEM", relative_path=path, file_format="csv", **changes)


def test_identity_is_stable_case_sensitive_and_independent_of_reader_options():
    """Membership and parsing options do not manufacture table-like identities."""
    original = source()
    assert source("incoming//*.csv")["source_id"] == original["source_id"]
    assert source("Incoming/*.csv")["source_id"] != original["source_id"]
    changed = source(reader_options={"header": True})
    assert changed["source_id"] == original["source_id"] and changed != original
    assert "table_id" not in original
    validate_contract_source({"source": original, "table": {}})
    with pytest.raises(ValueError, match="without a Table ID"):
        validate_contract_source({"source": original, "table": {"table_id": "fake"}})


@pytest.mark.parametrize("path", [
    "../secret", "/absolute", "abfss://other", "a/../../b", ".", "a\\b",
    "{../outside.csv,safe/*.csv}", "{../,safe/}*.csv", "{safe/,{../../,nested/}}*.csv",
    ".{.,/safe}/outside.csv",
])
def test_selectors_cannot_escape_the_files_area(path):
    """Source authorization cannot be widened through a path escape."""
    with pytest.raises(ValueError):
        source(path)


@pytest.mark.parametrize("path", ["incoming/orders.csv", "incoming", "incoming/*.csv", "incoming/part-?.csv", "incoming/[ab]*.csv"])
def test_confined_file_folder_and_wildcard_selectors_remain_supported(path):
    """Confinement validation preserves ordinary Spark file selection."""
    assert source(path)["relative_path"] == path


def test_file_draft_freezes_schema_grain_dq_and_freshness_without_catalogue_table(monkeypatch):
    """Shared contract semantics use file source identity with no Catalogue table row."""
    monkeypatch.setattr(contracts, "read_lakehouse_table", lambda *args, **kwargs: [])
    monkeypatch.setattr(contracts, "write_lakehouse_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(contracts, "build_runtime_audit_fields", lambda **kwargs: {})
    monkeypatch.setattr(contracts, "coerce_metadata_row_types", lambda table, row: row)
    spark = type("Spark", (), {"createDataFrame": lambda self, rows, schema=None: rows})()
    descriptor = source()
    draft = contracts.create_contract_draft(file_source=descriptor,
        columns=[{"column_id": "id", "column_name": "id", "data_type": "long"}],
        config={}, active_workspace_id="WORKSPACE", spark_session=spark)
    assert draft["table_id"] is None and draft["source_id"] == descriptor["source_id"]
    payload = json.loads(draft["contract_payload_json"])
    assert "table_id" not in payload["table"] and "processing" not in payload["table"]
    payload["guardrails"] = [{"guardrail_rule_id": "grain", "guardrail_type": "grain", "rule_type": "uniqueness",
        "rule_parameters": {"columns": ["id"]}, "action": "Block", "is_active": True},
        {"guardrail_rule_id": "fresh", "guardrail_type": "freshness", "rule_type": "freshness", "action": "Warn",
         "rule_parameters": {"evidence_method": "metadata", "evaluation_scope": "full_dataset", "maximum_age": 2, "maximum_age_unit": "hours"}}]
    frozen = contracts.freeze_contract_record(draft={**draft, "contract_payload_json": json.dumps(payload)}, audit={})
    assert json.loads(frozen["contract_payload_json"])["source"] == descriptor
    changed = deepcopy(payload)
    changed["source"]["relative_path"] = "different/*.csv"
    with pytest.raises(ValueError, match="stable file identity"):
        contracts.freeze_contract_record(draft={**draft, "contract_payload_json": json.dumps(changed)}, audit={})


def test_pipeline_submission_binds_exact_file_selector_and_reader_options():
    """Changing a file authorization requires another reviewed submission package."""
    from fabricops_kit.activated_pipeline import shared as activation
    from tests.unit.test_pipeline_handoff import package_candidate, resign
    descriptor = source(reader_options={"header": True})
    payload = {"contract": {"contract_id": "files", "contract_version": 1, "status": "frozen"},
        "source": descriptor, "table": {"columns": []}, "enrichment": {"table": [], "columns": []}, "guardrails": []}
    content = json.dumps(payload)
    package = package_candidate()
    package["contracts"][descriptor["source_id"]] = {"contract_id": "files", "contract_version": 1, "status": "frozen",
        "source_id": descriptor["source_id"], "table_id": None, "contract_payload_json": content}
    package["manifest"]["file_authorizations"] = [{"source": descriptor, "store": "Bronze", "contract_id": "files",
        "contract_version": 1, "payload_sha256": activation.hashlib.sha256(content.encode()).hexdigest()}]
    activation.validate_submission(resign(package))
    changed = deepcopy(package)
    changed["manifest"]["file_authorizations"][0]["source"]["reader_options"]["header"] = False
    with pytest.raises(ValueError, match="reader configuration"):
        activation.validate_submission(resign(changed))
    changed = deepcopy(package)
    changed["manifest"]["file_authorizations"][0]["source"]["relative_path"] = "other/*.csv"
    with pytest.raises(ValueError, match="stable file identity"):
        activation.validate_submission(resign(changed))


def test_file_activation_resolves_configured_physical_source(monkeypatch):
    """File Activation retains an exact frozen identity and rejects location drift."""
    from datetime import datetime
    from types import SimpleNamespace
    from fabricops_kit.activated_pipeline import shared as activation
    from fabricops_kit.io import shared as io
    descriptor = source()
    payload = {"source": descriptor, "table": {"columns": []}, "enrichment": {"table": [], "columns": []}, "guardrails": []}
    contract = {"contract_id": "files", "contract_version": 1, "source_id": descriptor["source_id"], "table_id": None,
        "status": "frozen", "contract_payload_json": json.dumps(payload)}
    context = {"config": {}, "scope_workspace_id": "workspace"}
    monkeypatch.setattr(activation, "resolve_fabric_context", lambda context=None: ({}, "workspace", context))
    monkeypatch.setattr(activation, "metadata_records", lambda *args, **kwargs: [contract])
    monkeypatch.setattr(activation, "build_runtime_audit_fields", lambda **kwargs: {"_committed_by": "reviewer"})
    monkeypatch.setattr(activation, "check_contract_agreement", lambda *args, **kwargs: None)
    store = SimpleNamespace(workspace_id="workspace", item_id="item")
    file_scopes = []
    def resolve_file(*args, **kwargs):
        file_scopes.append(kwargs["context"]["scope_workspace_id"])
        return store, "incoming/*.csv", "resolved"
    monkeypatch.setattr(io, "resolve_configured_file_path", resolve_file)
    def mutate(table, mutation, **kwargs):
        rows, result = mutation([])
        activation.validate_activations(rows)
        return result
    monkeypatch.setattr(activation, "mutate_metadata", mutate)
    result = activation.set_table_contract_activation(None, "files", 1, expected_activation_id=None,
        activation_id="file-activation", governance_confirmed=True, file_source=descriptor, file_store="Bronze", context=context,
        file_configuration_workspace_id="configuration-route")
    assert file_scopes == ["configuration-route"]
    assert result["workspace_id"] == "workspace"
    assert result["table_id"] is None and result["source_id"] == descriptor["source_id"]
    assert json.loads(result["destination_json"]) == descriptor
    store.item_id = "other-item"
    with pytest.raises(ValueError, match="physical authorization"):
        activation.set_table_contract_activation(None, "files", 1, expected_activation_id=None,
            activation_id="file-activation", governance_confirmed=True, file_source=descriptor, file_store="Bronze", context=context)


def test_file_approval_cannot_bypass_missing_execution_boundary(monkeypatch):
    """Even a retained approval cannot authorize unsupported file execution."""
    from fabricops_kit.activated_pipeline import shared as activation
    monkeypatch.setattr(activation, "verify_registry_approval", lambda *args, **kwargs:
        (None, {"manifest": {"file_authorizations": [{"source": source()}]}}))
    monkeypatch.setattr(activation, "get_spark_session", lambda *args, **kwargs: pytest.fail("No physical access is authorized"))
    with pytest.raises(RuntimeError, match="file orchestration boundary"):
        activation.verify_promotion_integrity({}, context={})
