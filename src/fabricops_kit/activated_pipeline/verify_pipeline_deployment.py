"""Bind an approved deployment to one explicit configured Fabric environment."""
import json
from pathlib import Path
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.activated_pipeline.shared import activation_version, bound_pipeline_participants, validate_manifest
from fabricops_kit.pipeline.shared import notebook_executable_fingerprint
from fabricops_kit.pipeline.shared import canonical_candidate_json


def verify_pipeline_deployment(*, deployment_path, authority_environment, sources, targets, spark_session=None, context=None):
    """Verify approved artifact contents and persist separate physical bindings.

    Run after deploying the tested executable and definitions with Fabric tooling.
    This records explicit workspace/notebook/store bindings in deployment.json.
    It does not deploy notebooks, activate versions, select Live or publish data.
    Every Live setup rechecks the artifacts, approval, dependencies and bindings.
    """
    config, env, runtime = resolve_fabric_context(context=context)
    root = Path(deployment_path).resolve(strict=True)
    package = json.loads((root / "approved.json").read_text())
    manifest = validate_manifest(package)
    approved = activation_version(package["activated_pipeline_id"], context={**runtime, "config": config, "env": authority_environment}, spark_session=spark_session)
    if approved["manifest_json"] != package["manifest_json"]:
        raise ValueError("Packaged manifest differs from Governance approval.")
    if notebook_executable_fingerprint((root / "executable.bin").read_bytes()) != manifest["candidate"]["executable_sha256"]:
        raise ValueError("Deployed executable identity mismatch.")
    if not runtime.get("notebook_id") or not runtime.get("workspace_id"):
        raise ValueError("Explicit deployed workspace and notebook identities are required.")
    bindings = {"pipeline_id": manifest["pipeline_id"], "authority_environment": authority_environment,
        "environment_name": env, "workspace_id": runtime["workspace_id"], "notebook_id": runtime["notebook_id"],
        "participants": bound_pipeline_participants(sources=sources, targets=targets, context=context, spark_session=spark_session)}
    expected = {item["participant"]: sorted(item["roles"]) for item in manifest["candidate"]["participants"]}
    if {key: value["roles"] for key, value in bindings["participants"].items()} != expected:
        raise ValueError("Deployed pipeline participants/roles differ from the approved manifest.")
    target = root / "deployment.json"
    content = canonical_candidate_json(bindings)
    if target.exists() and target.read_text() != content:
        raise ValueError("Deployment is already bound differently; use another deployment directory.")
    target.write_text(content)
    return bindings
