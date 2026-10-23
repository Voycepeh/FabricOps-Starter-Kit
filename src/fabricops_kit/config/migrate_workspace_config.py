"""Reviewable migration from environment mappings to workspace registrations."""
from dataclasses import asdict

from .shared import get_store, registry_bootstrap, validate_framework_config, validate_workspace_registration


def migrate_workspace_config(config, *, assignments: list[dict]) -> list[dict]:
    """Convert existing mappings into reviewed registrations without writing metadata.

    Preserve contract identities, frozen payloads and historical records. Each
    assignment supplies legacy_environment, workspace_id, display_name,
    environment (DEV/TEST/PROD), notebooks and status. Multiple assignments may
    reference one legacy environment, but approvals are never copied implicitly.
    Publish reviewed registrations through register_workspace. Physical Warehouse
    names fall back to their previous logical key during migration.

    Parameters
    ----------
    config : FrameworkConfig
        Existing environment mappings and governance settings.
    assignments : list[dict]
        Explicit workspace and deployment environment assignments; no inference.

    Returns
    -------
    list[dict]
        Complete validated registrations for administrator review and publication.

    """
    config = validate_framework_config(config)
    locator = registry_bootstrap()
    output = []
    for assignment in assignments:
        row = dict(assignment)
        legacy = row.pop("legacy_environment")
        resources = {}
        for key in config.path_config.paths[legacy]:
            store = get_store(config, legacy, key)
            resource = {key: value for key, value in asdict(store).items() if key not in {"env", "key"}}
            if store.kind == "warehouse" and not resource["item_name"]:
                resource["item_name"] = key
            resources[key] = resource
        row.update(resources=resources, settings={"audit_timezone": config.audit_timezone,
                   "governance_config": asdict(config.governance_config),
                   "data_agreement_config": asdict(config.data_agreement_config)})
        output.append(validate_workspace_registration(row, locator=locator))
    if len({row["workspace_id"] for row in output}) != len(output):
        raise ValueError("Each workspace may be registered only once.")
    return output
