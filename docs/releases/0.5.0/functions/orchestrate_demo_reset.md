<!-- Generated file. Edit docs/releases/manifests/0.5.0.yml or the authoritative source metadata and regenerate. -->

# `orchestrate_demo_reset`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.0`

Qualified callable: `fabricops_kit.config.orchestrate_demo_reset.orchestrate_demo_reset`

Source path: `src/fabricops_kit/config/orchestrate_demo_reset.py`

Frozen source ref: `v0.5.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.0/src/fabricops_kit/config/orchestrate_demo_reset.py)

Signature: `orchestrate_demo_reset(*, reset: 'bool' = False) -> 'None'`

## Description

Preview or reset the dedicated FabricOps Guided Demo to Day 1.

## Parameters

reset : bool, default=False
    False prints configured store identities, metadata row counts and the
    eleven business tables in scope without writing. True opts into the
    destructive reset after all preflight checks pass. Only booleans are
    accepted; strings and integers are rejected.

## Return value

None
    Prints a preview or verified reset summary, including actual removed
    metadata counts. ``RESET COMPLETE`` is printed only after verification.

## Usage notes

True clears all current canonical metadata rows in the dedicated item,
including frozen Contracts, activations, approvals, promotion history,
Runs and Processing State. Saved submissions, Dry Run evidence and notebook
snapshots in its three native lifecycle folders are removed too. Table
definitions remain; no metadata migration is performed.

Four Day 1 tables are overwritten, Orders CSV is validated and retained,
and five Silver outputs plus the obsolete Bronze Orders table are removed in the reserved
``demo`` schemas of the configured Bronze/Silver stores. The Gold customer_summary
table is retained with zero rows when present. Other business
tables and source files are preserved. Exact demo table/workspace references,
artifact contents, fixture counts and catalog locations are
checked before deletion. A dedicated name alone cannot prove ownership;
never share this Metadata item or these eleven tables with other projects.

Missing outputs and repeated resets are supported. A failure may leave a
partial reset: this operation is not atomic across tables/stores. Stop all
writers, correct the reported cause and rerun. Deployed notebooks, schedules
and apps are not removed. Live Fabric acceptance is still required.

[Back to release overview](../index.md)
