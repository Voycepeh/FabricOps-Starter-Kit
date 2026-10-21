"""Approve an exact successfully tested whole pipeline."""
from fabricops_kit.activated_pipeline.shared import tested_pipeline_manifest, approve_pipeline


def activate_pipeline(*, testing_run_id, candidate_fingerprint, pipeline_name, pipeline_version,
                      agreement_id, agreement_version, executable_path, governance_confirmed=False,
                      expected_active_id=None, spark_session=None, context=None):
    """Activate an immutable whole-pipeline version after independent service validation.

    Requires complete committed Testing evidence, exact candidate and effective
    Agreement identity, unchanged executable/dependencies/contracts and explicit
    Governance confirmation. A switch also requires expected_active_id. This
    action neither deploys artifacts nor publishes data.

    Returns the immutable METADATA_ACTIVATED_PIPELINE version and audit fields.
    Invalid evidence or a stale switch raises ValueError; metadata failures raise.
    """
    manifest = tested_pipeline_manifest(testing_run_id=testing_run_id, candidate_fingerprint=candidate_fingerprint,
        pipeline_name=pipeline_name, pipeline_version=pipeline_version, agreement_id=agreement_id,
        agreement_version=agreement_version, executable_path=executable_path, context=context, spark_session=spark_session)
    return approve_pipeline(manifest=manifest, governance_confirmed=governance_confirmed,
        expected_active_id=expected_active_id, context=context, spark_session=spark_session)
