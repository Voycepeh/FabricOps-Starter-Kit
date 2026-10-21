"""Explicit switching and deactivation without editing approved version contents."""
from fabricops_kit.activated_pipeline.shared import activation_version, metadata_records, commit_pipeline_activation, ACTIVATED_TABLE


def set_pipeline_active(activated_pipeline_id, *, active, expected_active_id, governance_confirmed=False,
                        spark_session=None, context=None):
    """Explicitly switch to or deactivate an existing immutable approved version.

    Require Governance confirmation and the currently active ID (None for no
    active version). Saved environment selections are never changed by this call.
    Returns the selected version with its new is_active state; stale state fails.
    """
    if governance_confirmed is not True or not isinstance(active, bool):
        raise ValueError("Explicit Governance confirmation and boolean active are required.")
    row = activation_version(activated_pipeline_id, context=context, spark_session=spark_session, require_active=False)
    current = [item for item in metadata_records(ACTIVATED_TABLE, context=context, spark_session=spark_session)
               if item["pipeline_id"] == row["pipeline_id"] and item.get("is_active") is True]
    if len(current) > 1 or (current[0]["activated_pipeline_id"] if current else None) != expected_active_id:
        raise ValueError("Active pipeline changed; refresh before switching.")
    if not active and expected_active_id != activated_pipeline_id:
        raise ValueError("Deactivate only the currently active version.")
    from fabricops_kit.activated_pipeline import shared
    config, env, runtime = shared.resolve_fabric_context(context=context)
    row = {**row, "is_active": active,
           **shared.build_runtime_audit_fields(config=config, env=env, runtime_context=runtime)}
    commit_pipeline_activation(row, expected_active_id=expected_active_id, context=context, spark_session=spark_session)
    return row
