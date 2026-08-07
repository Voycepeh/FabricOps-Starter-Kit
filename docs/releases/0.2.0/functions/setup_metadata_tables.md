<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `setup_metadata_tables`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.config.setup_metadata_tables.setup_metadata_tables`

Source path: `src/fabricops_kit/config/setup_metadata_tables.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/config/setup_metadata_tables.py)

Signature: `setup_metadata_tables(*, spark: 'Any', config: 'FrameworkConfig | dict[str, Any]', env: 'str', metadata_schema: 'str | None' = None, require_active_steward: 'bool' = False, verbose: 'bool' = True, raise_on_failure: 'bool' = False) -> 'dict[str, Any]'`

## Description

Create or check the FabricOps metadata tables for one environment.

## Parameters

spark : Any
    Spark session used to create empty schema DataFrames and read or write
    the metadata lakehouse tables.
config : FrameworkConfig | dict[str, Any]
    FabricOps configuration used to find the selected environment and its
    metadata lakehouse.
env : str
    Environment whose configured metadata lakehouse should be initialized
    or validated.
metadata_schema : str | None, optional
    Optional explicit schema for schema-enabled metadata lakehouses. When
    omitted, the configured metadata store schema is used where
    applicable.
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
    including the resolved metadata schema, metadata tables checked,
    tables created, existing tables successfully validated, failed tables,
    per-table messages, active steward readiness, fully qualified table
    names, and overall setup status. Key fields are ``status``,
    ``data_agreement``, ``governance``, ``tables``, ``table_results``,
    ``metadata_schema``, ``fully_qualified_tables``, ``created_tables``,
    ``validated_tables``, ``failed_tables``, ``created_or_checked_tables``,
    ``warnings``, ``active_metadata_tables``, and
    ``active_metadata_table_count``.

    ``status`` is ``"ready"`` when no table failures occur,
    ``"partial_failure"`` when some tables succeed and some fail, and
    ``"failed"`` when all table operations fail. ``data_agreement``
    summarizes steward, agreement, and contract readiness. ``governance``
    summarizes the remaining metadata tables. Active steward readiness
    depends on whether active steward rows already exist.

## Usage notes

Setup flow:

1. Validate the supplied FabricOps configuration.
2. Find the metadata lakehouse configured for the selected environment.
3. Verify that the metadata target is a lakehouse.
4. Resolve the metadata schema from ``metadata_schema`` or the configured
   metadata store.
5. Load the required FabricOps table definitions.
6. Attempt to read each required metadata table.
7. When a table is missing, create an empty Spark DataFrame using its
   required FabricOps table structure.
8. Write that empty DataFrame to the metadata lakehouse using overwrite
   mode to create the table.
9. Read the created table again.
10. Validate required column names and physical Spark data types.
11. Continue processing the remaining tables when one table fails.
12. Check whether at least one active steward record exists.
13. Return overall, data-agreement, governance, and per-table setup
    results.

``data_agreement["active_steward_count"]`` is retained for compatibility
and reports readiness presence: ``1`` when at least one active steward
exists and ``0`` otherwise. It is not a complete active steward population
count.

The canonical registry may expand in later compatible FabricOps releases.
In v0.2.0, metadata tables created or validated from
``metadata_table_schema_registry()`` are ``METADATA_DATA_STEWARD``,
``METADATA_DATA_AGREEMENT``, ``METADATA_DATA_CONTRACT``,
``METADATA_DATA_CATALOGUE``, ``METADATA_DATA_PROFILED``,
``METADATA_DATA_PROFILED_FREQUENCY``, ``METADATA_DATA_LINEAGE``, ``METADATA_DATA_ACCESS``,
``METADATA_ENRICHMENT``, ``METADATA_GUARDRAIL``, and
``METADATA_GUARDRAIL_RESULTS``.

Of that v0.2.0 inventory, ``METADATA_DATA_CATALOGUE``,
``METADATA_DATA_PROFILED``, ``METADATA_DATA_PROFILED_FREQUENCY``, and
``METADATA_DATA_LINEAGE`` are Live schemas with compatibility guarantees.
Every other metadata schema in the registry remains Preview.

Detailed table contents:

- ``METADATA_DATA_STEWARD`` is a person registry storing ``steward_id``,
  ``steward_name``, ``steward_role``, ``contact``, ``is_active``,
  ``custom_fields_json``, and the standard audit fields. Responsibility
  effective periods remain on ``METADATA_DATA_AGREEMENT``.
- ``METADATA_DATA_AGREEMENT`` stores ``agreement_id``,
  ``agreement_version``, ``agreement_name``, ``domain``,
  ``provider_steward_id``, ``recipient_steward_id``, ``recipient``,
  ``start_date``, ``expiry_date``, ``business_purpose``,
  ``custom_fields_json``, and the standard audit fields.
- ``METADATA_DATA_CONTRACT`` stores ``agreement_id``,
  ``metadata_table_key``, ``schema_fingerprint``, and the standard audit
  fields. ``_activity_id`` groups one saved inventory and ``_committed_at``
  orders inventory saves.
- ``METADATA_DATA_CATALOGUE`` stores ``metadata_table_key``,
  ``metadata_column_key``, ``schema_fingerprint``, ``environment_name``,
  ``store_type``, ``layer``, ``schema_name``, ``table_name``,
  ``column_name``, ``data_type``, and the standard audit fields.
- ``METADATA_DATA_PROFILED`` stores ``metadata_table_key``,
  ``metadata_column_key``, ``environment_name``, ``store_type``, ``layer``,
  ``schema_name``, ``table_name``, ``column_name``, ``data_type``,
  ``row_count``, ``non_null_count``, ``null_count``, ``null_percent``,
  ``distinct_count``, ``distinct_percent``, ``mean_value``,
  ``stddev_value``, ``min_value``, ``percentile_25_value``,
  ``median_value``, ``percentile_75_value``, ``max_value``,
  ``schema_fingerprint``, ``profiled_at``, and the standard audit fields.
- ``METADATA_DATA_PROFILED_FREQUENCY`` stores one flattened row per
  distinct profiled value with ``metadata_column_key``, value, count,
  percentage, rank, profiled row totals, ``profiled_at``, and audit fields.
  Join historical snapshots to ``METADATA_DATA_PROFILED`` through both
  ``metadata_column_key`` and ``profiled_at``.
- ``METADATA_DATA_LINEAGE`` stores ``lineage_event_id``, ``activity_id``,
  ``notebook_id``, ``notebook_name``, ``workspace_id``,
  ``workspace_name``, ``metadata_table_key``, ``schema_fingerprint``,
  ``profile_role``, ``profiled_at``, ``committed_by``,
  ``environment_name``, ``metadata_lakehouse_name``, and the standard
  audit fields.
- ``METADATA_DATA_ACCESS`` stores access scope, role, permission,
  approval, expiry, table and column identity, and audit information.
- ``METADATA_ENRICHMENT`` stores business metadata enrichment,
  classification, sensitivity, ownership, governance review, activation,
  effective dates, and audit information.
- ``METADATA_GUARDRAIL`` stores guardrail rule identity, scope,
  parameters, severity, lifecycle, governance review, approval, effective
  dates, and audit information.
- ``METADATA_GUARDRAIL_RESULTS`` stores guardrail execution results,
  status, continuation decision, expected and actual values, result
  payload, and audit information.

Standard audit fields are ``_committed_by``, ``_committed_at``,
``_workspace_id``, ``_workspace_name``, ``_notebook_id``,
``_notebook_name``, ``_metadata_lakehouse_name``, and ``_activity_id``.

Existing tables are validated for required column names and
compatible Spark data types. Physical Spark/Delta nullability is
intentionally not compared because persisted Fabric tables may report
fields as nullable regardless of the canonical logical requirement. The
legacy ``frequency_json`` column specifically fails
``METADATA_DATA_PROFILED`` validation; unrelated
metadata tables continue to permit additive columns.
Because normalized frequency persistence is a breaking physical-schema
change, existing metadata tables may need recreation through this setup
flow; no automatic migration is performed.
Existing tables are not automatically overwritten merely because they
already exist. Missing columns or incompatible types mark that table as
failed, processing continues for remaining metadata tables, and
``raise_on_failure=True`` raises only after all tables have been processed
when failures exist.

A missing table is created by writing an empty Spark DataFrame with the
required FabricOps table structure. This creates the metadata table structure but
does not populate business metadata records. The function does not
automatically create steward records, agreements, contracts, catalogue
records, profile records, lineage events, access assignments, enrichment
records, guardrail rules, or guardrail results; those are populated by
their respective FabricOps workflows.

[Back to release overview](../index.md)
