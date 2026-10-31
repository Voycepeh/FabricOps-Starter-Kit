<!-- Generated file. Edit docs/releases/manifests/0.3.1.yml or the authoritative source metadata and regenerate. -->

# `setup_metadata_tables`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.1`

Qualified callable: `fabricops_kit.config.setup_metadata_tables.setup_metadata_tables`

Source path: `src/fabricops_kit/config/setup_metadata_tables.py`

Frozen source ref: `v0.3.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.1/src/fabricops_kit/config/setup_metadata_tables.py)

Signature: `setup_metadata_tables(*, config: 'FrameworkConfig | dict[str, Any]', workspace_id: 'str', require_active_steward: 'bool' = False, verbose: 'bool' = True, raise_on_failure: 'bool' = False) -> 'dict[str, Any]'`

## Description

Create or check the FabricOps metadata tables for one workspace_id.

## Parameters

config : FrameworkConfig | dict[str, Any]
    FabricOps configuration used to find the selected workspace_id and its
    metadata lakehouse.
workspace_id : str
    Workspace whose configured metadata lakehouse should be initialized
    or validated.
require_active_steward : bool, default=False
    When ``True``, raise if ``METADATA_DATA_STEWARD`` contains no active
    steward rows after setup. This option does not create a steward
    record.
verbose : bool, default=True
    Controls whether the concise per-table setup summary is printed.
raise_on_failure : bool, default=False
    When ``True``, raise a ``RuntimeError`` after processing all tables if
    any table failed creation or validation.

## Return value

dict[str, Any]
    A dictionary summarizing the completed metadata lakehouse setup,
    including the resolved governance and engineering metadata schemas,
    metadata tables checked,
    tables created, additively evolved, successfully validated, failed tables,
    per-table messages, active steward readiness, fully qualified table
    names, and overall setup status. Key fields are ``status``,
    ``data_agreement``, ``governance``, ``engineering``, ``tables``,
    ``table_results``,
    ``metadata_schemas``, ``fully_qualified_tables``, ``created_tables``,
    ``evolved_tables``, ``validated_tables``, ``failed_tables``,
    ``created_or_checked_tables``,
    ``warnings``, ``active_metadata_tables``, and
    ``active_metadata_table_count``.

    ``status`` is ``"ready"`` when no table failures occur,
    ``"partial_failure"`` when some tables succeed and some fail, and
    ``"failed"`` when all table operations fail. ``data_agreement``
    summarizes steward, agreement, and contract readiness. ``governance``
    summarizes governance-authored tables, and ``engineering`` summarizes
    engineering-written tables. Active steward readiness depends on
    whether active steward rows already exist.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)
