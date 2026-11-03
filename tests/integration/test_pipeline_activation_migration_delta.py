"""Offline, idempotent Registry cutover with durable exact historical retention."""
# ruff: noqa: F811
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import pytest

from fabricops_kit.activated_pipeline import shared as service, migrate_registry as migration
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry, encode_metadata_row, coerce_metadata_row_types
from tests.integration.test_activation_state_delta import authority_delta
from tests.unit.test_activated_pipeline import operation, PIPELINE_ID

pytestmark = pytest.mark.spark


def retained_fixture(r, *, selected=True):
    """Write a complete original Test/Contract/Agreement and matching legacy authority."""
    schemas = metadata_table_schema_registry()
    op = operation()
    op.update(contract_id="contract", contract_version=1, payload_sha256=None, status="succeeded",
        started_at=datetime(2026, 1, 1), completed_at=datetime(2026, 1, 1, 0, 1),
        stages=[dict(stage="Processing", status="passed"), dict(stage="Schema", status="passed")])
    payload = json.dumps({"contract": {"contract_id": "contract", "contract_version": 1},
        "table": {"table_id": "orders", "columns": [], "processing": {"load_strategy": "overwrite"}},
        "guardrails": []})
    contract = dict(contract_id="contract", contract_version=1, table_id="orders", status="frozen",
        evidence_workspace_id="DEV", contract_payload_json=payload)
    op["payload_sha256"] = service.hashlib.sha256(payload.encode()).hexdigest()
    run = dict(run_id="retained-test", approval_id=None, pipeline_id=PIPELINE_ID, execution_mode="testing",
        workspace_id="DEV", started_at=datetime(2026, 1, 1), completed_at=datetime(2026, 1, 1, 0, 1),
        status="succeeded", activation_revision=None, boundary_completed=True, operations=[op],
        profiling=[], failures=[], warnings_json="[]", **r.audit)
    agreement = dict(agreement_id="agreement", agreement_version="1", agreement_name="Agreement",
        start_date="2020-01-01", expiry_date="2099-01-01")
    for field in schemas["METADATA_DATA_AGREEMENT"]:
        if not field.nullable and field.name not in agreement and not field.name.startswith("_"):
            agreement[field.name] = "example"
    for table, row in [("METADATA_DATA_CONTRACT", contract), ("METADATA_DATA_AGREEMENT", agreement),
                       ("METADATA_PIPELINE_RUN", run)]:
        r.spark.createDataFrame([encode_metadata_row(table, coerce_metadata_row_types(table, {**row, **r.audit}))],
            schemas[table]).write.format("delta").mode("append").save(r.ensure(table))
    from fabricops_kit.pipeline.shared import contract_guardrail_rows
    rule = contract_guardrail_rows(contract, workspace_id="DEV", table_id="orders")[0]
    diagnostic = dict(guardrail_result_id="retained-diagnostic", guardrail_rule_id=rule["guardrail_rule_id"],
        guardrail_version=1, table_id="orders", table_name="orders", contract_id="contract", contract_version=1,
        execution_type="testing", run_id=run["run_id"], workspace_id="DEV", status="passed",
        can_continue=True, severity="blocking", result_payload_json="{}", **r.audit)
    table = "METADATA_GUARDRAIL_RESULTS"
    r.spark.createDataFrame([coerce_metadata_row_types(table, diagnostic)], schemas[table]).write.format("delta").mode(
        "append").save(r.ensure(table))
    # Use the exact retained physical row's logical representation, including nullable original fields.
    run = service.metadata_records("METADATA_PIPELINE_RUN", context=r.context, spark_session=r.spark)[0]
    agreement = service.metadata_records("METADATA_DATA_AGREEMENT", context=r.context, spark_session=r.spark)[0]
    native = dict(pipeline_id=PIPELINE_ID, workspace_id="DEV", pipeline_name="Orders", pipeline_version="1",
        testing_run_id=run["run_id"], testing_evidence_sha256=service.manifest_digest({"run": run, "guardrail_results": service.metadata_records("METADATA_GUARDRAIL_RESULTS", context=r.context, spark_session=r.spark)}),
        agreement_id="agreement", agreement_version="1",
        agreement_sha256=service.manifest_digest(service.agreement_definition(agreement)),
        warnings=["Approval validates table contracts and operation modes, not notebook transformation code."])
    native["approval_id"] = service.manifest_digest(native)
    old = dict(authority_id="central", token="legacy", registrations=[dict(pipeline_id=PIPELINE_ID,
        workspace_id="DEV", notebook_id="notebook", notebook_name="Orders", registered_at=datetime(2026, 1, 1),
        registered_by="engineer", registration_status="Active", **r.audit)],
        revisions=[dict(workspace_id="DEV", revision="old-revision")],
        approvals=[{**native, **r.audit}], selections=[], table_ownership=[], reservations=[], **r.audit)
    if selected:
        old["selections"] = [dict(workspace_id="DEV", pipeline_id=PIPELINE_ID, approval_id=native["approval_id"])]
        old["table_ownership"] = [dict(workspace_id="DEV", table_id="orders", contract_id="contract", contract_version=1,
            payload_sha256=op["payload_sha256"], destination=op["destination"], writer=PIPELINE_ID, readers=[])]
    return old


def write_legacy(r, old):
    """Install a stopped, pre-upgrade authority in an isolated test table."""
    r.spark.createDataFrame([old], migration._legacy_registry_schema()).write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true").save(r.path)
    return r.spark.read.format("delta").load(r.path)


@pytest.mark.parametrize("selected", [False, True])
def test_migration_archives_all_history_and_never_activates_candidates(authority_delta, selected):
    """Selected/nonselected decisions survive outside the active Registry lifecycle."""
    from delta.tables import DeltaTable
    r = authority_delta
    old = retained_fixture(r, selected=selected)
    frame = write_legacy(r, old)
    before_runs = [row.asDict(recursive=True) for row in r.spark.read.format("delta").load(r.ensure("METADATA_PIPELINE_RUN")).collect()]
    table_id = DeltaTable.forPath(r.spark, r.path).detail().first().id
    upgraded, report = migration.migrate_registry(table=frame, context=r.context, spark_session=r.spark)
    rows = [row.asDict(recursive=True) for row in upgraded.collect()]
    control = service.registry_control(rows)
    assert len(rows) == (3 if selected else 1)
    assert all(row["status"] == "requires_reactivation" and row["activation_id"] is None for row in rows if row["record_type"] != "control")
    archive = Path(report["migration_archive_uri"]).read_text()
    assert service.hashlib.sha256(archive.encode()).hexdigest() == control["migration_archive_sha256"]
    snapshot = json.loads(archive)
    assert snapshot["rows"][0]["approvals"][0]["approval_id"] == old["approvals"][0]["approval_id"]
    assert snapshot["registration_ids"][0]["pipeline_id"] == PIPELINE_ID
    assert len(snapshot["rows"][0]["registrations"]) == 1
    assert DeltaTable.forPath(r.spark, r.path).detail().first().id == table_id
    assert DeltaTable.forPath(r.spark, r.path).detail().first().properties["delta.isolationLevel"] == "Serializable"
    assert [row.asDict(recursive=True) for row in r.spark.read.format("delta").load(r.ensure("METADATA_PIPELINE_RUN")).collect()] == before_runs
    repeated, second = migration.migrate_registry(table=upgraded, context=r.context, spark_session=r.spark)
    assert second is None
    assert repeated.collect() == upgraded.collect()
    assert len(report["requires_reactivation"]) == (2 if selected else 0)


@pytest.mark.parametrize("defect", ["reservation", "duplicate_selection", "ownership", "contract_hash", "run_tamper", "new_provenance"])
def test_ambiguous_migrations_fail_without_schema_or_authority_change(authority_delta, defect):
    """No current selection is reinterpreted to make an unsafe migration succeed."""
    from delta.tables import DeltaTable
    r = authority_delta
    old = retained_fixture(r)
    if defect == "reservation":
        old["reservations"] = [dict(workspace_id="DEV", reservation_id="busy", pipeline_id=PIPELINE_ID,
            mode="live", tables=["orders"], revision="old-revision", destinations=[])]
    elif defect == "duplicate_selection":
        old["selections"].append(deepcopy(old["selections"][0]))
    elif defect == "ownership":
        old["table_ownership"][0]["writer"] = "another"
    elif defect == "contract_hash":
        DeltaTable.forPath(r.spark, r.ensure("METADATA_DATA_CONTRACT")).update(set={"contract_payload_json": "'{}'"})
    elif defect == "run_tamper":
        DeltaTable.forPath(r.spark, r.ensure("METADATA_PIPELINE_RUN")).update(set={"warnings_json": "'[1]'"})
    else:
        DeltaTable.forPath(r.spark, r.ensure("METADATA_PIPELINE_RUN")).update(set={"deployment_id": "'forged'"})
    frame = write_legacy(r, old)
    before = frame.collect()
    version = DeltaTable.forPath(r.spark, r.path).history(1).first().version
    with pytest.raises(ValueError):
        migration.migrate_registry(table=frame, context=r.context, spark_session=r.spark)
    assert r.spark.read.format("delta").load(r.path).collect() == before
    assert DeltaTable.forPath(r.spark, r.path).history(1).first().version == version


def test_automatic_setup_migrates_registry_and_reports_governed_block(authority_delta, monkeypatch):
    """Public setup performs cutover and leaves explicit deployment readiness blocked."""
    import importlib
    from tests.helpers import framework_config, call_with_spark
    r = authority_delta
    old = retained_fixture(r, selected=False)
    write_legacy(r, old)
    module = importlib.import_module("fabricops_kit.config.setup_metadata_tables")
    monkeypatch.setattr(module, "read_lakehouse_table", lambda name, **kw: r.spark.read.format("delta").load(r.ensure(name)))
    monkeypatch.setattr(module, "_retired_preview_warnings", lambda **kw: [])
    result = call_with_spark(r.spark, module.setup_metadata_tables, config=framework_config(), workspace_id="dev", verbose=False)
    assert result["status"] == "ready"
    assert result["table_results"][service.REGISTRY_TABLE]["status"] == "evolved"
    assert result["governed_execution"]["status"] == "blocked"
    assert any("trusted deployment verification" in warning for warning in result["warnings"])


def test_migration_preserves_column_mapping_and_table_properties(authority_delta):
    """The schema replacement retains the original Delta table and mapping protocol."""
    from delta.tables import DeltaTable
    r = authority_delta
    old = retained_fixture(r)
    r.spark.createDataFrame([old], migration._legacy_registry_schema()).write.format("delta").mode(
        "overwrite").option("overwriteSchema", "true").option("delta.columnMapping.mode", "name").option(
        "delta.minReaderVersion", "2").option("delta.minWriterVersion", "5").save(r.path)
    quoted_path = "delta." + chr(96) + r.path + chr(96)
    r.spark.sql("ALTER TABLE " + quoted_path + " SET TBLPROPERTIES ('delta.columnMapping.mode'='name', 'delta.minReaderVersion'='2', 'delta.minWriterVersion'='5')")
    before = DeltaTable.forPath(r.spark, r.path).detail().first()
    assert before.properties["delta.columnMapping.mode"] == "name"
    upgraded, report = migration.migrate_registry(table=r.spark.read.format("delta").load(r.path),
        context=r.context, spark_session=r.spark)
    after = DeltaTable.forPath(r.spark, r.path).detail().first()
    assert before.id == after.id
    assert after.properties["delta.columnMapping.mode"] == "name"
    assert after.minReaderVersion >= before.minReaderVersion
    assert service.registry_control([row.asDict(recursive=True) for row in upgraded.collect()])["migration_archive_uri"] == report["migration_archive_uri"]
    assert r.spark.read.format("delta").load(r.ensure("METADATA_PIPELINE_RUN")).count() == 1


def test_migration_archive_failure_leaves_legacy_authority_intact(authority_delta, monkeypatch):
    """A durable audit failure cannot turn into an unaudited schema cutover."""
    r = authority_delta
    frame = write_legacy(r, retained_fixture(r))
    before = frame.collect()
    monkeypatch.setattr(migration, "write_governance_archive",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("archive unavailable")))
    with pytest.raises(OSError, match="archive unavailable"):
        migration.migrate_registry(table=frame, context=r.context, spark_session=r.spark)
    assert r.spark.read.format("delta").load(r.path).collect() == before


@pytest.mark.parametrize("metadata_workspace", [None, "CENTRAL"])
def test_migration_keeps_central_owner_when_validating_foreign_history(authority_delta, monkeypatch, metadata_workspace):
    """Engineering Test scope must not replace the setup Metadata routing workspace."""
    r = authority_delta
    old = retained_fixture(r)
    frame = write_legacy(r, old)
    context = {**r.context, "scope_workspace_id": "GOV"}
    if metadata_workspace:
        context["metadata_workspace_id"] = metadata_workspace
    scopes = []
    original = service.read_lakehouse_table

    def read(table, **kwargs):
        scopes.append(kwargs["context"]["scope_workspace_id"])
        return original(table, **kwargs)

    monkeypatch.setattr(service, "read_lakehouse_table", read)
    upgraded, report = migration.migrate_registry(table=frame, context=context, spark_session=r.spark)
    assert scopes and set(scopes) == {metadata_workspace or "GOV"}
    rows = [row.asDict(recursive=True) for row in upgraded.collect()]
    contract = service.exact_record(rows, record_type="table_contract_activation")
    assert contract["workspace_id"] == "DEV"
    assert json.loads(contract["destination_json"]) == old["table_ownership"][0]["destination"]
    assert report["migration_archive_uri"]
