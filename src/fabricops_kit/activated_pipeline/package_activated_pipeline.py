"""Deterministic approved definitions packaged beside deployment artifacts."""
from pathlib import Path
from fabricops_kit.activated_pipeline.shared import activation_version, validate_manifest
from fabricops_kit.pipeline.shared import notebook_executable_fingerprint
from fabricops_kit.pipeline.shared import canonical_candidate_json


def package_activated_pipeline(activated_pipeline_id, *, destination, executable_path, spark_session=None, context=None):
    """Package an approved manifest and exact definitions with its tested executable.

    Writes deterministic approved.json and executable.bin to an explicit mounted
    or local deployment directory. Does not deploy Fabric artifacts, copy metadata
    rows, configure bindings, select a version or publish business data. Governance
    approval remains authoritative and must be reachable by Live execution.
    """
    row = activation_version(activated_pipeline_id, context=context, spark_session=spark_session)
    manifest = validate_manifest(row)
    executable = Path(executable_path).read_bytes()
    if notebook_executable_fingerprint(executable) != manifest["candidate"]["executable_sha256"]:
        raise ValueError("Executable differs from the tested approved artifact.")
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    portable = {key: value for key, value in row.items() if not key.startswith("_") and key != "is_active"}
    for name, value in (("approved.json", canonical_candidate_json(portable).encode()), ("executable.bin", executable)):
        target = root / name
        if target.exists() and target.read_bytes() != value:
            raise ValueError("Deployment artifact already exists with different immutable contents; use another directory.")
        target.write_bytes(value)
    return {"activated_pipeline_id": activated_pipeline_id, "deployment_path": str(root.resolve())}
