"""Data Sensitivity Assessment policy, evidence, and bounded inheritance tests."""

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from fabricops_kit import GovernanceConfig, assess_data_sensitivity
from fabricops_kit.data_contract import shared
from fabricops_kit.pipeline import shared as pipeline


def _profile(*names, **values):
    return {"profile": [{"COLUMN_NAME": name, "DATA_TYPE": "string", **values} for name in names],
            "profile_scope": "full_table"}


def _context(**options):
    return {"scope_workspace_id": "dev", "config": SimpleNamespace(
        governance_config=GovernanceConfig(**options))}


def test_no_contract_and_no_ai_defaults(monkeypatch):
    """Aggregate evidence leaves undefined business meaning unresolved."""
    monkeypatch.setattr(shared, "invoke_fabric_ai", lambda *a, **k: pytest.fail("AI ran without opt-in"))
    value = assess_data_sensitivity({"COLUMN_NAME": "amount", "DATA_TYPE": "long"})
    assert value["classification"] is None
    assert value["minimum_handling_classification"] == "Restricted"
    assert value["human_review_required"] and value["contains_personal_data"] is None


@pytest.mark.parametrize("target, expected", [(None, False), ("Public", True),
                                              ("Restricted", True), ("Confidential", False),
                                              ("Highly Sensitive", False)])
def test_conditional_treatments_for_nonpersonal_sensitive_information(target, expected):
    """Non-personal Confidential material can need treatment when lowering the target."""
    value = assess_data_sensitivity(
        _profile("exam"), column_definitions={"exam": {"category": "examination_material"}},
        target_classification=target,
    )
    assert value["classification"] == "Confidential"
    assert value["contains_personal_data"] is False and value["contains_sensitive_data"] is True
    assert bool(value["recommended_treatments"]) is expected
    if expected:
        assert value["recommended_treatments"][0]["parameters"]["treatment"] == "remove"


def test_pattern_positive_is_precautionary_and_excluded_from_result():
    """Positive value evidence raises handling without guessing business context."""
    evidence = "employee@example.test"
    value = assess_data_sensitivity(_profile("contact", MIN_VALUE=evidence), target_classification="Public")
    assert value["classification"] is None
    assert value["minimum_handling_classification"] == "Confidential"
    assert "pattern_match:email" in value["columns"][0]["evidence"]
    assert evidence not in repr(value)
    assert value["recommended_treatments"] == []
    business = assess_data_sensitivity(
        _profile("contact", MIN_VALUE=evidence),
        column_definitions={"contact": {"category": "business_contact"}},
    )
    assert business["classification"] == business["minimum_handling_classification"] == "Restricted"


def test_draft_category_cannot_lower_approved_labels(monkeypatch):
    """New evidence is reported without replacing the active classification."""
    module = __import__(assess_data_sensitivity.__module__, fromlist=["assessment_contract_evidence"])
    monkeypatch.setattr(module, "assessment_contract_evidence", lambda *_: {
        "classification": "Confidential", "columns": {
            "amount": {"classification": "Confidential", "description": "Previous description"},
        },
    })
    result = assess_data_sensitivity(_profile("amount"), column_definitions={
        "amount": {"description": "New draft", "category": "internal_budget"},
    })
    assert result["classification"] == "Confidential"
    assert result["columns"][0]["approved_classification"] == "Confidential"
    assert "conflicting_classification" in result["columns"][0]["evidence"]


def test_ai_is_one_sanitised_validated_request(monkeypatch):
    """Model input contains no raw value, schema identifier or unapproved description."""
    calls = []

    def invoke(prompt, **_):
        calls.append(prompt)
        return ('{"columns":[{"ref":"c0","classification":"Public","personal":null}],'
                '"dataset_classification":null}')

    monkeypatch.setattr(shared, "invoke_fabric_ai", invoke)
    context = _context(ai_enrichment={"enabled": True, "sensitive_data_prompt": "Generic policy"},
                       sensitivity_assessment={"ai_endpoint_approved": True})
    result = assess_data_sensitivity(
        _profile("PRIVATE_NAME", "other", MIN_VALUE="private@example.test"),
        description="Unapproved free text", use_ai=True, context=context,
    )
    assert len(calls) == 1 and "Generic policy" in calls[0]
    assert not any(secret in calls[0] for secret in ("PRIVATE_NAME", "private@example.test", "Unapproved free text"))
    assert result["columns"][0]["assessment_method"] == "ai_assisted"
    assert result["minimum_handling_classification"] == "Confidential"
    assert result["human_review_required"]


@pytest.mark.parametrize("response", ["not json", '{"columns":[{"ref":"unknown"}],"dataset_classification":null}'])
def test_malformed_ai_does_not_erase_deterministic_evidence(monkeypatch, response):
    """Validate the entire response before updating provisional findings."""
    monkeypatch.setattr(shared, "invoke_fabric_ai", lambda *_a, **_k: response)
    result = assess_data_sensitivity(_profile("column"), use_ai=True, context=_context(
        ai_enrichment={"enabled": True}, sensitivity_assessment={"ai_endpoint_approved": True}))
    assert result["ai_status"] == "invalid_response"
    assert result["classification"] is None
    assert result["minimum_handling_classification"] == "Restricted"


def test_explicit_local_scan_finds_rare_matches_and_reports_counts_only(spark_session):
    """Use Spark to find matches omitted from aggregate stats or frequency tops."""
    frame = spark_session.createDataFrame([("ordinary",), ("rare@example.test",),
                                          ("4111111111111111",)], "contact string")
    result = assess_data_sensitivity(_profile("contact", ROW_COUNT=3), dataframe=frame)
    assert result["columns"][0]["local_detector_counts"]["email"] == 1
    assert result["columns"][0]["local_detector_counts"]["payment_card"] == 1
    assert "rare@example.test" not in repr(result)
    with pytest.raises(ValueError, match="different row counts"):
        assess_data_sensitivity(_profile("contact", ROW_COUNT=10), dataframe=frame)


def test_joint_small_groups_escalate_context(spark_session):
    """Two columns classified individually can warrant a higher dataset classification."""
    frame = spark_session.createDataFrame([(2001, "A"), (2001, "B")], "birth_year int, group string")
    categories = {name: {"category": "quasi_identifier"} for name in frame.columns}
    result = assess_data_sensitivity(_profile(*frame.columns, ROW_COUNT=2), dataframe=frame,
                                     column_definitions=categories)
    assert result["classification"] == "Confidential"
    assert {finding["code"] for finding in result["dataset_findings"]} == {"small_joint_groups"}
    assert {column["classification"] for column in result["columns"]} == {"Restricted"}


def _graph(source, target, source_column, output_column):
    nodes = [
        {"node_id": "root", "node_type": "SOURCE_COLUMN", "table_id": source,
         "asset_workspace_id": "dev", "asset_type": "TABLE", "name": source_column,
         "column_id": f"{source}:{source_column}", "data_type": "bigint"},
        {"node_id": "alias", "node_type": "EXPRESSION", "operation": "Alias", "data_type": "bigint"},
        {"node_id": "column", "node_type": "COLUMN", "operation": "Project", "data_type": "bigint"},
    ]
    return {"version": 1, "scope": "write_input", "nodes": nodes,
            "outputs": [{"column_name": output_column, "column_id": f"{target}:{output_column}",
                         "node_id": "column", "status": "complete",
                         "sources": [{"node_id": "root", "dependency_types": ["VALUE"]}]}],
            "edges": [{"source_node_id": a, "target_node_id": b, "dependency_type": "VALUE"}
                      for a, b in (("root", "alias"), ("alias", "column"))]}


def test_captured_graph_accepts_consecutive_pyspark_steps(spark_session):
    """Trace filter, rename and deduplication through one analysed Spark graph."""
    tracker = pipeline.LineageTracker()
    source = spark_session.createDataFrame([(1, 10)], "staff_id long, salary long")
    tracker.register(source, {"table_id": "staff", "asset_workspace_id": "dev", "asset_type": "TABLE"})
    from pyspark.sql import functions as F
    transformed = (source.filter("salary > 0").withColumnRenamed("staff_id", "employee_id")
                   .dropDuplicates().withColumn("salary_band", F.col("salary") + 1))
    graph = pipeline._lineage_graph(tracker.analyse(transformed), transformed.columns, "output", "overwrite")
    index = shared._SensitivityGraph(graph)
    supported, direct, roots, population = index.column("employee_id", "bigint")
    assert supported and direct and population and roots[0]["name"] == "staff_id"
    assert not index.column("salary_band", "bigint")[1]


def test_bounded_verified_chain_reaches_last_approved_source(monkeypatch):
    """A published intermediate with no active label can inherit through a verified current link."""
    lineage = shared._SensitivityLineage({}, {"Restricted": 0, "Confidential": 1})
    start = datetime(2026, 1, 2, tzinfo=UTC)
    now = int(start.timestamp() * 1_000_000)

    def publication(run_id, source, target, a, b, stamp):
        op = {"operation_key": "target:" + target}
        read = {"asset_workspace_id": "dev", "table_id": source, "asset_type": "TABLE",
                "pipeline_role": "source", "status": "succeeded", "started_at": stamp, "destination": {}}
        return ({"run_id": run_id, "operations": [read]}, op,
                shared._SensitivityGraph(_graph(source, target, a, b)),
                int(stamp.timestamp() * 1_000_000) + 1_000)

    ab = publication("run-b", "a", "b", "id", "renamed", start.replace(day=1))
    bc = publication("run-c", "b", "c", "renamed", "employee_id", start)
    seen = []

    def approved(source, *_args):
        seen.append(source["table_id"])
        return ("Confidential", "Confidential", {"contract_version": 3}, False) if source["table_id"] == "a" else (
            None, None, None, False)

    monkeypatch.setattr(lineage, "approved_source", approved)
    monkeypatch.setattr(lineage, "publication", lambda *_: ab)
    monkeypatch.setattr(lineage, "history", lambda *_: [{"instant": now - 50}])
    inherited = lineage.walk(bc, "employee_id", "bigint")
    assert inherited["classification"] == "Confidential"
    assert seen == ["b", "a"]
    assert lineage.walk(bc, "employee_id", "bigint") == inherited
    assert seen == ["b", "a"]
    lineage.resolved.clear()
    monkeypatch.setattr(lineage, "history", lambda *_: [{"instant": now + 2}, {"instant": now - 50}])
    unverified = lineage.walk(bc, "employee_id", "bigint")
    assert unverified["classification"] is None
    assert unverified["review"] == "upstream_approval_unverified"


def test_dry_run_and_skipped_profiles_have_explicit_scope():
    """A prepared input or missing activity cannot become a full output assessment."""
    dry = {**_profile("value"), "profile_scope": "supplied_dataframe",
           "assessment_reference": {"profile_subject": "prepared_input"}}
    assert assess_data_sensitivity(dry)["scope"]["kind"] == "supplied_dataframe"
    skipped = {"status": "passed", "profile_scope": "full_table",
               "activities": {"standard": {"status": "skipped"}}}
    result = assess_data_sensitivity(skipped)
    assert result["scope"]["kind"] == "unknown"
    assert "standard_profile_unavailable" in result["limitations"]


def test_scheduled_profile_reuses_exact_scoped_snapshot(spark_session, monkeypatch):
    """A result resolves its completed profile by Run, snapshot, physical asset and role."""
    time = datetime(2026, 1, 2, tzinfo=UTC)
    metadata = spark_session.createDataFrame([
        ("asset", "dev", "TABLE", "run", "wanted", "target", "selected", "string", "full_table", time),
        ("asset", "other", "TABLE", "run", "wanted", "target", "cross_workspace", "string", "full_table", time),
        ("asset", "dev", "TABLE", "run", "other", "target", "different_snapshot", "string", "full_table", time),
        ("asset", "dev", "TABLE", "run", "wanted", "source", "different_role", "string", "full_table", time),
    ], ["table_id", "asset_workspace_id", "asset_type", "run_id", "profile_snapshot_id", "pipeline_role",
        "column_name", "data_type", "profile_scope", "_committed_at"])
    requests = []

    def frame(table, _):
        requests.append(table)
        return metadata

    monkeypatch.setattr(shared, "_assessment_frame", frame)
    result = {"status": "passed", "profile_scope": "full_table", "assessment_reference": {
        "table_id": "asset", "asset_workspace_id": "dev", "asset_type": "TABLE",
        "run_id": "run", "operation": "write", "profile_subject": "persisted_output",
    }, "activities": {"standard": {"status": "passed", "profile_snapshot_id": "wanted",
                                   "executed_at": time.isoformat()}}}
    columns, scope, asset, one, limitations = shared.assessment_profile_evidence(result, {"config": {}})
    assert list(columns) == ["selected"]
    assert scope["profile_snapshot_id"] == "wanted" and scope["kind"] == "full_table"
    assert asset["asset_workspace_id"] == "dev" and not one and not limitations
    assert requests == ["METADATA_DATA_PROFILED"]


def test_configured_identifier_checksum_preserves_uncertainty():
    """A valid synthetic identifier is positive evidence without confirming business meaning."""
    result = assess_data_sensitivity(
        _profile("identifier", MIN_VALUE="S0000000J"),
        context=_context(sensitivity_assessment={"detectors": ["nric_fin"]}),
    )
    assert "pattern_match:nric_fin" in result["columns"][0]["evidence"]
    assert result["minimum_handling_classification"] == "Confidential"
    assert result["classification"] is None
    assert "S0000000J" not in repr(result)


def test_changed_upstream_approval_keeps_stricter_handling(monkeypatch):
    """An activated reduction on the upstream asset cannot reduce historical protection."""
    before = datetime(2026, 1, 1, tzinfo=UTC)
    after = datetime(2026, 1, 3, tzinfo=UTC)
    read = {"contract_id": "contract", "contract_version": 1, "payload_sha256": "first"}
    source = {"asset_workspace_id": "dev", "table_id": "staff", "asset_type": "TABLE",
              "name": "id", "column_id": "id", "data_type": "string"}
    monkeypatch.setattr(shared, "_assessment_contracts", lambda *_: [
        {**read, "activation_id": "old", "revision": 1, "status": "superseded", "activated_at": before},
        {**read, "contract_version": 2, "payload_sha256": "second",
         "activation_id": "new", "revision": 2, "status": "active", "activated_at": after},
    ])
    monkeypatch.setattr(shared, "_assessment_contract_payload", lambda _asset, activation, _runtime: {
        "provenance": {"activation_id": activation["activation_id"]},
        "columns": {"id": {"column_id": "id", "data_type": "string",
                           "classification": "Confidential" if activation["revision"] == 1 else "Restricted"}},
    })
    lineage = shared._SensitivityLineage({}, {"Restricted": 0, "Confidential": 1})
    result = lineage.approved_source(source, read, shared._assessment_instant(before.replace(day=2)))
    assert result == ("Confidential", "Confidential", {"activation_id": "old"}, True)
