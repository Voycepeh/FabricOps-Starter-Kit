<!-- Generated file. Edit docs/releases/manifests/0.5.1.yml or the authoritative source metadata and regenerate. -->

# `setup_metadata_tables`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.1`

Qualified callable: `fabricops_kit.config.setup_metadata_tables.setup_metadata_tables`

Source path: `src/fabricops_kit/config/setup_metadata_tables.py`

Frozen source ref: `v0.5.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.1/src/fabricops_kit/config/setup_metadata_tables.py)

Signature: `setup_metadata_tables(*, config: 'FrameworkConfig | dict[str, Any]', workspace_id: 'str', require_active_steward: 'bool' = False, verbose: 'bool' = True, raise_on_failure: 'bool' = False) -> 'dict[str, Any]'`

## Description

Create, validate and safely evolve the 13 canonical metadata tables.

## Parameters

config : FrameworkConfig | dict[str, Any]
    Configuration containing the selected workspace's central Metadata
    Lakehouse. Metadata must be a schema-enabled Lakehouse.
workspace_id : str
    Configuration scope used to resolve the Metadata store.
require_active_steward : bool, default=False
    Require an active Data Steward after table setup. No steward is created.
verbose : bool, default=True
    Print concise per-table creation, evolution and readiness results.
raise_on_failure : bool, default=False
    Raise after all tables have been processed when any table fails.

## Return value

dict[str, Any]
    Overall readiness, configured ownership schemas, canonical table names,
    created/evolved/validated/failed tables, per-table results, steward
    readiness, a separate processing_state result, and advisory diagnostics for
    noncanonical metadata tables. Overall readiness includes Processing State.

## Usage notes

Missing tables are created empty with error-if-exists semantics. Registry
and Contract Activation use Serializable isolation. Processing State is
initialized at misc.PROCESSING_STATE in the configured Metadata Lakehouse,
separately from the canonical METADATA_* tables. Its schema and Serializable
isolation are validated on repeat setup; existing rows are preserved.
Setup never manufactures
approvals, populates business metadata or replaces business targets. Governance definitions and activation are independent workflows.

Compatible missing columns are added automatically. Only columns explicitly
declared for retirement are removed, following their table-specific validation. Other extension
columns are preserved where the table's identity contract permits them.
Operational file source_id values are copied into the common table_id and
validated before source_id is retired. Conflicting identities block migration.
v0.5.0 profile rows are TABLE observations; their workspace remains explicitly
historical when physical scope cannot be established. Stop pipelines for this schema migration; recovery
restores the returned pre-upgrade Delta version together with the prior code.
Unproven populated retirements fail with data preserved. Cleanup and supported
identity changes commit atomically, with the pre-upgrade Delta version
returned for recovery before VACUUM or further writes. Setup never vacuums.
For legacy Catalogue rows, setup validates parent and column identities,
resolves physical workspaces, preserves stored column IDs in columns_json,
and retires the separate column records in the same Delta commit.
Setup standardizes physical asset workspace columns when their scope is known.
Historical workspace values without sufficient proof remain in legacy_workspace_id
extension columns on upgraded tables only; fresh tables omit this column.
Contract activation destinations and notebook audit fields retain their original values.
The per-table result returns the pre-upgrade version and recovery command.
Migration starts at released v0.5.0 and ends at the current canonical schema.
Older and intermediate PR schemas have no conversion paths. Catalogue and
Pipeline Run collection fields remain validated JSON strings; native physical
collections are rejected. Identity changes use tracked Delta reads and exact
schema/data readback. Existing rows, audit values, extension fields, table
identity/properties and Delta transaction identities are preserved. Run
provenance fields and retained content hashes are preserved.
Repeated setup validates compliant tables without rewriting them.

Processing State observations, checkpoints, accepted baselines and publication
receipts remain intact. Missing progress is never inferred for populated
targets. Incompatible identity layouts, incorrect types, malformed JSON and
duplicate Run identities fail explicitly with the existing data preserved.
A failure in one table does not prevent validation of the remaining tables.
Unchanged fields retain their physical nullability and order. Renamed
legacy_workspace_id extension fields are nullable so new physical observations can omit them.

Governed admission remains blocked pending signed-in Fabric acceptance.
Retirement presence diagnostics are advisory; unsupported tables are never
read as canonical authority or automatically deleted. METADATA_DATA_LINEAGE
stores scalar column dependency facts projected from finalized Runs. Setup
additively adds the new nullable fields to retained activity layouts without
rewriting historical rows; lineage_version=1 identifies new facts. Participation
remains in METADATA_PIPELINE_RUN.operations.

Primary keys shown in the metadata diagram are validated for every table.
Setup rejects existing null, blank or duplicate keys without deleting rows,
enables Serializable isolation and installs required-key Delta constraints.
Uniqueness is enforced by FabricOps transactional writers; external writers
must use the same protocol. Re-run setup before using upgraded writers.

[Back to release overview](../index.md)
