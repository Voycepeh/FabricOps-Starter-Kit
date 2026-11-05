<!-- Generated file. Edit docs/releases/manifests/0.4.0.yml or the authoritative source metadata and regenerate. -->

# `setup_metadata_tables`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.4.0`

Qualified callable: `fabricops_kit.config.setup_metadata_tables.setup_metadata_tables`

Source path: `src/fabricops_kit/config/setup_metadata_tables.py`

Frozen source ref: `v0.4.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.4.0/src/fabricops_kit/config/setup_metadata_tables.py)

Signature: `setup_metadata_tables(*, config: 'FrameworkConfig | dict[str, Any]', workspace_id: 'str', require_active_steward: 'bool' = False, verbose: 'bool' = True, raise_on_failure: 'bool' = False) -> 'dict[str, Any]'`

## Description

Create, validate and safely evolve the 14 canonical metadata tables.

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
    readiness and advisory diagnostics for noncanonical metadata tables.

## Usage notes

Missing tables are created empty with error-if-exists semantics. Registry
and Contract Activation use Serializable isolation. Setup never manufactures
approvals, populates business metadata, deletes rows or replaces business
targets. Governance definitions and activation are independent workflows.

Compatible missing columns are added automatically. Catalogue and Pipeline
Run collection fields are stored as validated JSON strings; supported native
collections are converted atomically with tracked Delta reads and exact
schema/data readback. Existing rows, audit values, extension fields, table
identity/properties and Delta transaction identities are preserved. Run
provenance additions are nullable and preserve retained content hashes.
Repeated setup validates compliant tables without rewriting them.

Processing State observations, checkpoints, accepted baselines and publication
receipts remain intact. Missing progress is never inferred for populated
targets. Incompatible identity layouts, incorrect types, malformed JSON and
duplicate Run identities fail explicitly with the existing data preserved.
A failure in one table does not prevent validation of the remaining tables.
Physical nullability and field order are not rewritten.

Governed admission remains blocked pending signed-in Fabric acceptance.
Retirement presence diagnostics are advisory; unsupported tables are never
read as canonical authority or automatically deleted.

[Back to release overview](../index.md)
