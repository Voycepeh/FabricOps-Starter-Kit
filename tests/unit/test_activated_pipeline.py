"""Notebook promotion, exact Contract authority and fail-closed admission."""
from copy import deepcopy
from datetime import date, datetime, timedelta
from types import SimpleNamespace
import json

import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry, metadata_table_owner

PIPELINE_ID = "4c7ae400-85ab-4023-9427-e8fde20bd596"


def operation(role="target", table="orders", mode="overwrite", workspace="DEV"):
    """Return one exact operation used by unit and actual Delta tests."""
    return dict(operation_key=role + ":Silver/" + table, table_id=table, pipeline_role=role,
        destination=dict(workspace_id=workspace, item_id="item", kind="lakehouse", schema="demo", table_name=table),
        read_mode="full" if role == "source" else None, write_mode=mode if role == "target" else None,
        query_sha256=None, incremental_target_table_id=None, source_table_ids=[], requested_schema="demo")


def contract_candidate(workspace="DEV"):
    """Return an independent per-physical-workspace Contract Activation."""
    return dict(workspace_id=workspace, table_id="orders", contract_id="contract", contract_version=1,
        payload_sha256="a" * 64, activation_id="activation-"+workspace, revision=1, status="active",
        destination_json=json.dumps(operation(workspace=workspace)["destination"]), _committed_by="governance",
        activated_at=datetime(2026, 1, 1))


def promotion(version=1, workspace="DEV", **overrides):
    """Return a complete immutable promotion row without runtime coordination fields."""
    return dict(execution_workspace_id=workspace, pipeline_id=PIPELINE_ID, pipeline_version=version,
        promotion_id=f"promotion-{workspace}-{version}", status="active", source_workspace_id="AUTHOR",
        source_notebook_id=PIPELINE_ID, governed_notebook_id=f"governed-{workspace}-{version}",
        snapshot_uri=f"snapshot-{workspace}-{version}", snapshot_sha256="a"*64,
        source_snapshot_uri="source.ipynb", source_snapshot_sha256="b"*64, executable_sha256="c"*64,
        operations_json=json.dumps([operation(workspace=workspace)]), bindings_sha256=service.manifest_digest([operation(workspace=workspace)]),
        parameters_json='{"manual":false,"days":null}', approval_id=f"approval-{workspace}-{version}",
        submission_id=f"submission-{workspace}-{version}", submission_sha256="d"*64,
        restored_from_version=None, _committed_by="governance", promoted_at=datetime(2026, 1, 1), **overrides)


def notebook(code=None):
    """Build complete notebook bytes, including original Markdown and outputs."""
    return json.dumps({"nbformat": 4, "nbformat_minor": 5, "metadata": {"kernelspec": {"name": "python3"}}, "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": "Notes"},
        {"cell_type": "code", "metadata": {"tags": ["parameters"]}, "execution_count": 1,
            "outputs": [{"output_type": "stream", "name": "stdout", "text": "output"}],
            "source": code or 'setup_pipeline(pipeline_mode="Dry Run")'}]}).encode()


def test_canonical_14_tables_and_separate_grains():
    """Verify canonical 14 tables and separate grains."""
    registry = metadata_table_schema_registry()
    assert len(registry) == 14
    assert metadata_table_owner(service.ACTIVATION_TABLE) == "governance"
    assert {"record_type", "leases_json", "git_commit_sha", "deployment_id", "table_id", "contract_id"}.isdisjoint(registry[service.REGISTRY_TABLE].fieldNames())
    assert {"execution_workspace_id", "pipeline_id", "pipeline_version", "snapshot_uri"} <= set(registry[service.REGISTRY_TABLE].fieldNames())
    assert service.validate_registry([]) == []


def test_contract_activation_is_independent_across_physical_workspaces():
    """Verify contract activation is independent across physical workspaces."""
    rows = [contract_candidate(), contract_candidate("PROD")]
    rows[1]["contract_version"] = 2
    assert service.validate_activations(rows) == rows
    rows[1]["destination_json"] = rows[0]["destination_json"]
    with pytest.raises(ValueError, match="physical|alias"):
        service.validate_activations(rows)


@pytest.mark.parametrize("duplicate", ["version", "promotion", "notebook", "active"])
def test_duplicate_registry_identities_fail_closed(duplicate):
    """Verify duplicate registry identities fail closed."""
    first, second = promotion(), promotion(2)
    if duplicate == "version": second["pipeline_version"] = 1
    if duplicate == "promotion": second["promotion_id"] = first["promotion_id"]
    if duplicate == "notebook": second["governed_notebook_id"] = first["governed_notebook_id"]
    with pytest.raises(ValueError, match="Duplicate|Multiple active"):
        service.validate_registry([first, second])


def test_versions_scoped_to_destination_workspace():
    """Verify versions scoped to destination workspace."""
    assert service.validate_registry([promotion(), promotion(workspace="PROD")])
    first, second = promotion(), promotion(2)
    first["status"] = "superseded"
    assert service.validate_registry([first, second])

def test_original_and_repeatedly_promoted_notebooks_resolve_to_one_identity(monkeypatch):
    """Every physical notebook in a promotion chain resolves to its original source ID."""
    source_id = PIPELINE_ID
    first = promotion(1, workspace="PROD", source_workspace_id="DEV",
                      source_notebook_id=source_id, governed_notebook_id="00000000-0000-4000-8000-000000000002")
    second = promotion(2, workspace="PROD", source_workspace_id="DEV",
                       source_notebook_id=source_id, governed_notebook_id="00000000-0000-4000-8000-000000000003")
    second["status"] = "active"
    first["status"] = "superseded"
    rows = [first, second]
    monkeypatch.setattr(service, "resolve_fabric_context",
        lambda context=None: ({}, context["scope_workspace_id"], context))
    monkeypatch.setattr(service, "read_registry", lambda **kwargs: rows)

    source_id_result, source = service.resolve_pipeline_identity(
        context={"scope_workspace_id": "DEV", "notebook_id": source_id})
    first_id_result, first_copy = service.resolve_pipeline_identity(
        context={"scope_workspace_id": "PROD", "notebook_id": first["governed_notebook_id"]})
    second_id_result, second_copy = service.resolve_pipeline_identity(
        context={"scope_workspace_id": "PROD", "notebook_id": second["governed_notebook_id"]})

    assert source_id_result == first_id_result == second_id_result == source_id
    assert source["role"] == "source"
    assert first_copy["role"] == second_copy["role"] == "governed"
    assert first_copy["row"]["status"] == "superseded"
    assert second_copy["row"]["status"] == "active"


def test_registry_rejects_physical_notebook_reassigned_to_another_pipeline():
    """A physical Fabric notebook cannot silently become another logical pipeline."""
    first = promotion(1, workspace="PROD", source_workspace_id="DEV",
                      source_notebook_id=PIPELINE_ID, governed_notebook_id="00000000-0000-4000-8000-000000000002")
    second = promotion(1, workspace="TEST", source_workspace_id="DEV",
                       source_notebook_id="00000000-0000-4000-8000-000000000099",
                       governed_notebook_id="00000000-0000-4000-8000-000000000002")
    with pytest.raises(ValueError, match="multiple logical Pipeline IDs"):
        service.validate_registry([first, second])


def test_markdown_and_outputs_do_not_change_executable_hash():
    """Verify markdown and outputs do not change executable hash."""
    original = notebook()
    changed = json.loads(original)
    changed["cells"][0]["source"] = "Revised Markdown"
    changed["cells"][1]["outputs"] = []
    changed["cells"][1]["execution_count"] = 99
    assert service.notebook_executable_digest(original) == service.notebook_executable_digest(json.dumps(changed).encode())
    changed["cells"][1]["source"] += "\nx = 1"
    assert service.notebook_executable_digest(original) != service.notebook_executable_digest(json.dumps(changed).encode())


@pytest.mark.parametrize("change", ["parameter", "metadata", "query", "tags"])
def test_behavior_changes_affect_notebook_hash(change):
    """Verify behavior changes affect notebook hash."""
    original = notebook()
    changed = json.loads(original)
    if change == "parameter": changed["cells"][1]["source"] += "\nlimit = 5"
    if change == "query": changed["cells"][1]["source"] += '\nsql = "SELECT * FROM other"'
    if change == "metadata": changed["metadata"]["dependencies"] = {"lakehouse": "different"}
    if change == "tags": changed["cells"][1]["metadata"]["tags"] = []
    assert service.notebook_executable_digest(original) != service.notebook_executable_digest(json.dumps(changed).encode())


def test_promotion_only_switches_literal_mode_and_retains_full_content():
    """Verify promotion only switches literal mode and retains full content."""
    raw = notebook()
    promoted, parameters = service.promoted_notebook(raw)
    expected = json.loads(raw)
    expected["cells"][1]["source"] = expected["cells"][1]["source"].replace('"Dry Run"', '"Governed"')
    assert json.loads(promoted) == expected
    assert parameters == {"manual": False, "days": None}


@pytest.mark.parametrize("code", ["x = 1", 'setup_pipeline(pipeline_id=ID, pipeline_mode="Dry Run")',
    'setup_pipeline(pipeline_mode=MODE)',
    'setup_pipeline(pipeline_mode="Dry Run", **params)',
    'setup_pipeline(pipeline_mode="Ungoverned")'])
def test_ambiguous_or_parameterized_startup_rejects(code):
    """Verify ambiguous or parameterized startup rejects."""
    with pytest.raises(ValueError, match="literal|exactly one|Save"):
        service.promoted_notebook(notebook(code))


def test_fabric_gate_rejects_forged_plan_and_never_reads_metadata(monkeypatch):
    """Verify fabric gate rejects forged plan and never reads metadata."""
    monkeypatch.setattr(service, "read_registry", lambda **kw: pytest.fail("must reject before admission"))
    with pytest.raises(RuntimeError, match="signed-in Fabric"):
        service.build_governed_pipeline_plan(pipeline_id=PIPELINE_ID)
    with pytest.raises(RuntimeError, match="signed-in Fabric"):
        service.verify_governed_plan(SimpleNamespace(promotion_id="forged"))


def test_agreement_requires_exact_effective_period():
    """Verify agreement requires exact effective period."""
    today = date.today()
    service.validate_agreement({"start_date": today, "expiry_date": today})
    with pytest.raises(ValueError, match="effective"):
        service.validate_agreement({"start_date": today-timedelta(days=2), "expiry_date": today-timedelta(days=1)})


def test_promotion_cas_preserves_old_row_and_replays_idempotently(monkeypatch):
    """Verify promotion cas preserves old row and replays idempotently."""
    state = []
    def mutate(_table, mutation, **kwargs):
        proposed, result = mutation(deepcopy(state))
        service.validate_registry(proposed)
        state[:] = proposed
        return result
    monkeypatch.setattr(service, "mutate_metadata", mutate)
    monkeypatch.setattr(service, "verify_registry_approval", lambda *a, **kw: None)
    monkeypatch.setattr(service, "verify_promotion_integrity", lambda *a, **kw: None)
    first = service.commit_pipeline_promotion(promotion(), expected_active_version=None, context={})
    assert first["pipeline_version"] == 1
    second = service.commit_pipeline_promotion(promotion(2), expected_active_version=1, context={})
    assert [row["status"] for row in state] == ["superseded", "active"]
    assert service.commit_pipeline_promotion(promotion(2), expected_active_version=1, context={}) == second
    assert service.commit_pipeline_promotion(promotion(), expected_active_version=None, context={})["status"] == "superseded"
    with pytest.raises(ValueError, match="Stale"):
        service.commit_pipeline_promotion(promotion(3), expected_active_version=1, context={})
    assert len(state) == 2
    assert state[0]["snapshot_uri"] == first["snapshot_uri"]


def test_reused_promotion_id_with_changed_code_rejects(monkeypatch):
    """Verify reused promotion id with changed code rejects."""
    original = promotion()
    monkeypatch.setattr(service, "verify_registry_approval", lambda *a, **kw: None)
    monkeypatch.setattr(service, "verify_promotion_integrity", lambda *a, **kw: None)
    monkeypatch.setattr(service, "mutate_metadata", lambda table, mutation, **kw: mutation([deepcopy(original)])[1])
    changed = deepcopy(original); changed["executable_sha256"] = "e"*64
    with pytest.raises(ValueError, match="reused"):
        service.commit_pipeline_promotion(changed, expected_active_version=1, context={})


def test_ungoverned_physical_alias_is_protected_in_foreign_workspace(monkeypatch):
    """Verify ungoverned physical alias is protected in foreign workspace."""
    calls = []
    monkeypatch.setattr(service, "publication_claim", lambda *a, **kw: calls.append(kw.get("release", False)))
    monkeypatch.setattr(service, "read_activations", lambda **kw: [contract_candidate("PROD")])
    plan = SimpleNamespace(plan_id="run", evidence={}, runtime_context={}, workspace_id="DEV")
    with pytest.raises(ValueError, match="physical destination alias"):
        service.guard_ungoverned_write(plan, "alias", operation(workspace="PROD")["destination"])
    assert calls == [False, True]


def test_redundant_public_approval_functions_are_removed():
    """Unreleased standalone approval/mutation functions have no public aliases."""
    import fabricops_kit
    from fabricops_kit.public_api import RELEASE_PUBLIC_API
    for name in ("activate_data_contract", "promote_pipeline", "restore_pipeline", "widget_deploy_pipeline"):
        assert not hasattr(fabricops_kit, name)
        assert not any(path.endswith("." + name) for path in RELEASE_PUBLIC_API)
