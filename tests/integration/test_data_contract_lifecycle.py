"""One stored payload through real authoring, hydration, both orchestrators and activation.

Spark, widget/service logic, resolution, checks, Coverage, and publication logic
are real. Only Fabric storage/Delta transport, schedule discovery, and profiling
are replaced with local boundaries. These tests do not access a live Lakehouse.
"""

from copy import deepcopy
from datetime import datetime, timedelta
import importlib
import json
import re
import sys
from types import SimpleNamespace

import pytest

from fabricops_kit import orchestrate_read, orchestrate_write
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry, coerce_metadata_row_types
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.pipeline import shared as runtime
from tests.helpers import framework_config
from tests.helpers import run_pipeline_operation

pytestmark = pytest.mark.integration


class _DeltaTransport:
    """Execute domain-authored metadata merges against the local transport's rows."""

    def __init__(self, boundary, name):
        self.boundary, self.name = boundary, name
        self.update_all, self.insert, self.updates, self.update_condition = False, False, None, None

    def toDF(self):
        """Expose the physical schema used by publication receipt checks."""
        if self.name.startswith("METADATA_"):
            return self.boundary.spark.createDataFrame([], metadata_table_schema_registry()[self.name])
        return self.boundary.business[self.name]

    def history(self):
        """Expose transaction receipts retained by the local Delta transport."""
        return self.boundary.spark.createDataFrame(self.boundary.commits.get(self.name, []), "userMetadata string")

    def alias(self, name):
        return self

    def merge(self, source, condition):
        self.source = [row.asDict(recursive=True) for row in source.collect()]
        self.condition = condition
        return self

    def whenMatchedUpdateAll(self, condition=None):
        self.update_all, self.update_condition = True, condition
        return self

    def whenNotMatchedInsertAll(self):
        self.insert = True
        return self

    def whenMatchedUpdate(self, set=None, condition=None):
        self.updates, self.update_condition = set, condition
        return self

    def execute(self):
        rows = self.boundary.metadata[self.name]
        pairs = re.findall(r"target\.(\w+)\s*=\s*source\.(\w+)", self.condition)
        literals = re.findall(r"target\.(\w+)\s*=\s*'([^']*)'", self.condition)
        for source in self.source:
            matches = [row for row in rows if
                all(row.get(left) == source.get(right) for left, right in pairs)
                and all(row.get(key) == value for key, value in literals)
                and ("target.column_id IS NULL" not in self.condition or row.get("column_id") is None)]
            for target in matches:
                if self.update_condition == "target.status = 'draft'" and target.get("status") != "draft":
                    continue
                if self.update_all:
                    target.update(deepcopy(source))
                elif self.updates:
                    for key, expression in self.updates.items():
                        match = re.search(r"source\.(\w+)", expression)
                        assert match or expression in {"true", "false"}, expression
                        value = source.get(match.group(1)) if match else expression == "true"
                        if value is not None or not expression.startswith("coalesce("):
                            target[key] = value
            if not matches and self.insert:
                rows.append(deepcopy(source))


@pytest.fixture
def lifecycle(monkeypatch, spark_session, tmp_path):
    """Share one configured local metadata store across every real workflow phase."""
    from importlib import metadata
    installed_version = metadata.version
    monkeypatch.setattr(metadata, "version", lambda name: "test-delta-runtime" if name == "delta-spark" else installed_version(name))
    modules = [importlib.import_module(name) for name in (
        "fabricops_kit.widgets.widget_data_contract", "fabricops_kit.pipeline.setup_pipeline",
        "fabricops_kit.widgets.widget_activate_pipeline", "fabricops_kit.data_contract.scheduled_refresh",
        "fabricops_kit.pipeline.orchestrate_read", "fabricops_kit.pipeline.orchestrate_write",
        "fabricops_kit.pipeline.pipeline_read", "fabricops_kit.pipeline.pipeline_write",
    )]
    config = framework_config()
    config.path_config.paths["prod"] = dict(config.path_config.paths["dev"])
    now = datetime.now()
    context = {"config": config, "env": "dev", "activity_id": "authoring", "notebook_id": "pipeline-id",
               "notebook_name": "pipeline", "workspace_id": "workspace-id", "workspace_name": "workspace"}
    audit = {"_committed_at": now, "_committed_by": "test@example.test", "_workspace_id": "workspace-id",
             "_workspace_name": "workspace", "_notebook_id": "pipeline-id", "_notebook_name": "pipeline",
             "_metadata_lakehouse_name": "Metadata", "_activity_id": "authoring"}
    registry = metadata_table_schema_registry()
    state = SimpleNamespace(config=config, context=context, metadata={name: [] for name in registry}, business={}, reads=[], commits={})

    from fabricops_kit.activated_pipeline import shared as activation
    state.metadata["METADATA_ACTIVATION_STATE"] = [{"authority_id": "central", "token": "initial", "snapshot_json": activation.empty_activation_state()}]
    def commit_authority(snapshot, *, expected_token, **kwargs):
        row = state.metadata["METADATA_ACTIVATION_STATE"][0]
        if row["token"] != expected_token:
            raise ValueError("Concurrent approval")
        from uuid import uuid4
        row.update(token=str(uuid4()), snapshot_json=runtime.canonical_candidate_json(snapshot))
        return row["token"]
    monkeypatch.setattr(activation, "commit_activation_state", commit_authority)
    activity_times = {}
    def audit_fields(**kwargs):
        activity = context["activity_id"]
        activity_times.setdefault(activity, now + timedelta(microseconds=len(activity_times)))
        return {**audit, "_activity_id": activity, "_committed_at": activity_times[activity]}

    def read(name, **kwargs):
        state.reads.append(name)
        if not name.startswith("METADATA_"):
            if name not in state.business:
                raise RuntimeError("[TABLE_OR_VIEW_NOT_FOUND] Table does not exist")
            return state.business[name]
        assert name in registry, f"Unexpected metadata dependency: {name}"
        assert kwargs.get("store") == "Metadata"
        values = []
        for row in state.metadata[name]:
            value = coerce_metadata_row_types(name, {**audit_fields(), **row})
            for field in registry[name]:
                if value.get(field.name) is None and not field.nullable:
                    value[field.name] = {"StringType": "unused", "IntegerType": 1, "LongType": 0,
                                         "BooleanType": False, "TimestampType": now, "DateType": now.date(), "DoubleType": 0.0}.get(type(field.dataType).__name__)
            values.append(value)
        return spark_session.createDataFrame(values, registry[name])

    def write(frame, name, **kwargs):
        if name.startswith("METADATA_"):
            assert name in registry
            state.metadata[name].extend(row.asDict(recursive=True) for row in frame.collect())
        else:
            state.business[name] = frame
            state.commits.setdefault(name, []).append(((kwargs.get("options") or {}).get("userMetadata"),))

    def resolve(context=None, **kwargs):
        selected = context if context is not None else state.context
        return config, selected.get("env", "dev"), selected

    def path(store, name, schema=None, **kwargs):
        return store, name, schema, name

    # Patch imported infrastructure references, retaining all domain implementations.
    for module in list(sys.modules.values()):
        if module is None or not getattr(module, "__name__", "").startswith("fabricops_kit"):
            continue
        for name, replacement in (("read_lakehouse_table", read), ("write_lakehouse_table", write),
                                  ("resolve_fabric_context", resolve), ("build_runtime_audit_fields", audit_fields),
                                  ("get_spark_session", lambda *a, **k: spark_session),
                                  ("resolve_configured_lakehouse_table", path),
                                  ("get_default_fabric_context", lambda: context)):
            if hasattr(module, name):
                monkeypatch.setattr(module, name, replacement)
    monkeypatch.setitem(sys.modules, "delta.tables", SimpleNamespace(DeltaTable=SimpleNamespace(
        forPath=lambda spark, name: _DeltaTransport(state, name),
        isDeltaTable=lambda spark, name: name in state.business)))
    def persist_run(plan, row, **kwargs):
        record = runtime.pipeline_run_row(row)
        runtime.pipeline_run_result(record)
        state.metadata['METADATA_PIPELINE_RUN'] = [item for item in state.metadata['METADATA_PIPELINE_RUN']
            if item['run_id'] != plan.plan_id] + [record]
    monkeypatch.setattr(runtime, '_merge_pipeline_run_row', persist_run)
    schedule = importlib.import_module("fabricops_kit.data_contract.scheduled_refresh")
    monkeypatch.setattr(schedule, "discover_scheduled_refresh", lambda **kwargs: {"status": "not_configured", "schedules": []})
    for name in ("_CURRENT_SOURCE_OBSERVATIONS", "_CURRENT_FRESHNESS_EVIDENCE", "_PENDING_SOURCE_OBSERVATIONS",
                 "_PENDING_SOURCE_DRIFT_OBSERVATIONS", "_INCREMENTAL_SOURCE_SCOPES", "_CURRENT_TABLE_IDENTITIES"):
        monkeypatch.setattr(runtime, name, {})
    for module in modules:
        if module.__name__.endswith(("orchestrate_read", "orchestrate_write")):
            monkeypatch.setattr(module, "schedule_table_profiling", lambda *args, **kwargs: {"row_count": 2})
    monkeypatch.setattr(importlib.import_module("fabricops_kit.widgets.shared"), "pipeline_active_context", lambda: None)
    monkeypatch.setattr(importlib.import_module("IPython.display"), "display", lambda *a, **k: None)
    for layer, name in (("Bronze", "orders"), ("Bronze", "products"), ("Silver", "curated_orders")):
        identity = runtime.resolve_physical_table_identity(config, "dev", store=layer, schema="dbo", table_name=name)
        table_id = identity["table_id"]
        setattr(state, "source_id" if name == "orders" else "schema_source_id" if name == "products" else "target_id", table_id)
        table = {"table_id": table_id, "table_name": name, "environment_name": "dev", "metadata_level": "table",
                 "column_id": None, "store_type": "lakehouse", "layer": layer, "schema_name": "dbo",
                 "is_active": True, "load_strategy": "overwrite", "load_strategy_parameters_json": "{}",
                 "scheduled_refresh_json": '{"status":"not_configured","schedules":[]}', **audit}
        state.metadata["METADATA_DATA_CATALOGUE"].append(table)
        for column, dtype in (("id", "bigint"), ("email", "string"), ("modified_at", "timestamp"), ("day", "string")):
            state.metadata["METADATA_DATA_CATALOGUE"].append({**table, "metadata_level": "column", "column_id": f"{table_id}/{column}", "column_name": column, "data_type": dtype})
    state.business["orders"] = spark_session.createDataFrame([
        (1, "one@example.test", now - timedelta(hours=1), str(now.date())),
        (2, "two@example.test", now - timedelta(hours=1), str(now.date())),
    ], "id long, email string, modified_at timestamp, day string")
    state.business["products"] = state.business["orders"]
    state.metadata["METADATA_DATA_AGREEMENT"] = [{"agreement_id": "agreement", "agreement_version": "1", "agreement_name": "Demo", "start_date": "2020-01-01", "expiry_date": "2099-01-01", **audit}]
    state.spark, state.read, state.write = spark_session, read, write
    return state


def _author_and_freeze(state, table_id, *, source, schema_only=False):
    """Persist authored definitions, hydrate the real widget, edit, save, reopen and freeze."""
    draft = contracts.create_contract_draft(table_id=table_id, config=state.config, env="dev", spark_session=state.spark)
    payload = json.loads(draft["contract_payload_json"])
    specs = [("schema", "required_columns", "", {"required_columns": [f"{table_id}/id"]}),
             ("grain", "uniqueness", "", {"columns": ["id"]}),
             ("data_quality", "completeness", f"{table_id}/id", {"columns": ["id"], "maximum_missing_percent": 0, "treat_blank_as_missing": False})]
    if source:
        specs += [("freshness", "freshness", "", {"freshness_column": "modified_at", "expected_refresh_frequency": 1, "expected_refresh_unit": "days", "maximum_age": 2, "maximum_age_unit": "days"}),
                  ("source_drift", "historical_mutation", "", {"partition_column": "day", "change_column": "modified_at"})]
    else:
        specs += [("sensitive_data", "mask", f"{table_id}/email", {"scope": "column", "treatment": "mask", "preserve_start": 0, "preserve_end": 0, "mask_character": "*"})]
    if schema_only:
        specs = specs[:1]
    payload["guardrails"] = [{"guardrail_rule_id": f"{table_id}:{kind}", "guardrail_version": 1,
        "contract_id": draft["contract_id"], "contract_version": 1, "guardrail_type": kind, "rule_id": rule_type,
        "rule_type": rule_type, "column_id": column, "rule_parameters": params, "is_active": True, "action": "Block"}
        for kind, rule_type, column, params in specs]
    payload["enrichment"]["columns"] = [{"enrichment_id": f"{table_id}:description", "enrichment_level": "column",
        "column_id": f"{table_id}/email", "enrichment_type": "Description", "value": "Contact email"}]
    contracts.save_contract_draft(draft=draft, payload=payload, config=state.config, env="dev", spark_session=state.spark)
    widget_module = importlib.import_module("fabricops_kit.widgets.widget_data_contract")
    widget = widget_module.widget_data_contract(table_id=table_id, contract_version=1, spark_session=state.spark, context=state.context)
    widget["_controls"]["open"].click()
    assert widget["current"] is not None, widget.get("message")
    assert widget["_controls"]["grain_enabled"].value is (not schema_only)
    if not schema_only:
        assert widget["_controls"]["row_key_columns"].value == ("id",)
    assert len(widget["current"]["guardrails"]) == (1 if schema_only else 5 if source else 4)
    widget["_controls"]["table_description"].value = "Authored and hydrated"
    widget["save_data_contract"](return_to_selector_after=False)
    widget = widget_module.widget_data_contract(table_id=table_id, contract_version=1, spark_session=state.spark, context=state.context)
    widget["_controls"]["open"].click()
    assert widget["current"] is not None, widget.get("message")
    assert widget["_controls"]["table_description"].value == "Authored and hydrated"
    assert any(row.get("value") == "Contact email" for row in widget["current"]["enrichment"])
    frozen = widget["freeze"]()["contract"]
    assert frozen["status"] == "frozen" and "is_active" not in frozen
    return frozen


def _activation(state, testing_results=()):
    """Open whole-pipeline Governance review with the real headless service."""
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    return module.widget_activate_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52",
        spark_session=state.spark, context=state.context)


def test_authored_payload_lifecycle_and_both_orchestrators(lifecycle):
    """Author/freeze, bootstrap-free Testing, explicit Governance review, then governed Live."""
    state = lifecycle
    source = _author_and_freeze(state, state.source_id, source=True)
    schema_source = _author_and_freeze(state, state.schema_source_id, source=True, schema_only=True)
    target = _author_and_freeze(state, state.target_id, source=False)
    frozen_json = {row["contract_id"]: row["contract_payload_json"] for row in (source, schema_source, target)}
    before = _activation(state)
    assert not before["eligible_runs"] and before["activate"].disabled
    assert not state.metadata["METADATA_DATA_LINEAGE"]
    coordinates = {"pipeline_id": "8f32a471-6c91-4b7e-9d13-2f0c947eab52", "configuration": {}, "sources": [
        {"store": "Bronze", "schema": "dbo", "table_name": "orders"},
        {"store": "Bronze", "schema": "dbo", "table_name": "products"}],
        "targets": [{"store": "Silver", "schema": "dbo", "table_name": "curated_orders"}]}
    choices = {row["table_id"]: {"contract_id": row["contract_id"], "contract_version": 1}
               for row in (source, schema_source, target)}
    snapshot = deepcopy(state.metadata)
    state.context["activity_id"] = "testing"
    plan = runtime.build_pipeline_execution_plan(**coordinates, execution_mode="testing", selections=choices,
        spark_session=state.spark, context=state.context)
    def reads(plan):
        return [run_pipeline_operation(orchestrate_read, plan=plan, **coords, spark_session=state.spark, verbose=False)
                for coords in coordinates["sources"]]
    inputs = reads(plan)
    from pyspark.sql import functions as F
    invalid = inputs[0]["dataframe"].withColumn("id", F.lit(None).cast("long"))
    failed = run_pipeline_operation(orchestrate_write, invalid, plan=plan, sources=inputs, **coordinates["targets"][0],
        write_mode="overwrite", spark_session=state.spark, verbose=False)
    assert not failed["validation_passed"] and not failed["published"]
    assert failed["grain_result"]["can_continue"] is False
    assert_ordinary_metadata_unchanged(state.metadata, snapshot)
    assert "curated_orders" not in state.business
    from fabricops_kit.pipeline.shared import finalize_pipeline_run
    assert finalize_pipeline_run(plan, spark_session=state.spark)["status"] == "failed"
    gate = _activation(state)
    assert not gate["eligible_runs"] and gate["activate"].disabled
    plan = runtime.build_pipeline_execution_plan(**coordinates, execution_mode="testing", selections=choices,
        spark_session=state.spark, context=state.context)
    with plan:
        inputs = reads(plan)
        tested = run_pipeline_operation(orchestrate_write, inputs[0]["dataframe"], plan=plan, sources=inputs,
            **coordinates["targets"][0], write_mode="overwrite", spark_session=state.spark, verbose=False)
    assert tested["validation_passed"] and not tested["published"]
    assert tested["validation_passed"]
    assert tested["dataframe"].first().email == "****************"
    assert_ordinary_metadata_unchanged(state.metadata, snapshot)
    completed = plan.run_result
    assert completed["status"] == "succeeded"
    assert all(row["run_id"] == plan.plan_id for row in plan.results)
    assert all(row["rule_type"] != "contract_validation" for row in plan.results)
    runtime.publish_pipeline_testing_results(plan, spark_session=state.spark)
    widget = _activation(state)
    assert len(widget["eligible_runs"]) == 1 and widget["activate"].disabled
    assert len(state.metadata["METADATA_PIPELINE_RUN"]) == 1
    assert state.metadata["METADATA_GUARDRAIL_RESULTS"]
    assert all(row["contract_payload_json"] == frozen_json[row["contract_id"]]
               for row in state.metadata["METADATA_DATA_CONTRACT"])


def assert_ordinary_metadata_unchanged(current, before):
    """Allow run evidence and Guardrail diagnostics while protecting ordinary metadata."""
    for name, rows in before.items():
        if name not in {"METADATA_PIPELINE_RUN", "METADATA_GUARDRAIL_RESULTS"}:
            assert current[name] == rows
