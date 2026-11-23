<!-- Generated file. Edit docs/releases/manifests/0.5.1.yml or the authoritative source metadata and regenerate. -->

# `orchestrate_demo_reset`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.1`

Qualified callable: `fabricops_kit.config.orchestrate_demo_reset.orchestrate_demo_reset`

Source path: `src/fabricops_kit/config/orchestrate_demo_reset.py`

Frozen source ref: `v0.5.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.1/src/fabricops_kit/config/orchestrate_demo_reset.py)

Signature: `orchestrate_demo_reset(*, reset: 'bool' = False) -> 'None'`

## Description

Preview or reset the Guided Demo data and its processing progress to Day 1.

## Parameters

reset : bool, default=False
    False prints configured destinations, scoped metadata counts and the
    eleven business tables without writing. True resets only those demo
    tables, their Processing State and profile snapshots after preflight.
    Only booleans are accepted.

## Return value

None
    Prints actual removed counts and ``RESET COMPLETE`` after verification.

## Usage notes

Deletion is restricted by exact demo identities and workspace: execution
workspace for ``misc.PROCESSING_STATE`` and asset workspace for
``METADATA_DATA_PROFILED`` and ``METADATA_DATA_PROFILED_FREQUENCY``. Only
configured mappings to the physical stores being reset participate. No
nested Run or Contract payloads are inspected to authorize deletion.

Contracts, activations, approvals, promotion history, Catalogue, Runs,
Lineage, Guardrail results and saved submissions, Dry Runs and notebook
snapshots are retained, including demo history. Profile snapshots for demo
assets are discarded so standard profiling can run again. Historical grain
and empty-frequency completion markers remain in retained Runs; use a zero
profiling interval when those activities must run again immediately.
This is a data restart, not a restart of governance authoring; use a separate
environment for a fresh governance walkthrough.

Four Day 1 source tables are overwritten. Orders CSV is validated and
retained. Five Silver outputs and obsolete Bronze Orders are removed from
the reserved ``demo`` schemas. Gold customer_summary is retained with zero
rows when present. Other business tables and all source files are preserved.

Preview never writes. Missing outputs and repeated resets are supported.
The reset is not atomic across stores; after a partial failure stop writers,
correct the cause and rerun. Never use it as production recovery. Actual
Microsoft Fabric validation remains required.

[Back to release overview](../index.md)
