<!-- Generated file. Edit docs/releases/manifests/0.4.1.yml or the authoritative source metadata and regenerate. -->

# `widget_activate_data_contract`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.4.1`

Qualified callable: `fabricops_kit.widgets.widget_activate_data_contract.widget_activate_data_contract`

Source path: `src/fabricops_kit/widgets/widget_activate_data_contract.py`

Frozen source ref: `v0.4.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.4.1/src/fabricops_kit/widgets/widget_activate_data_contract.py)

Signature: `widget_activate_data_contract(table_id: 'str | None' = None, contract_id: 'str | None' = None, contract_version: 'int | None' = None, *, workspace_id: 'str | None' = None, context=None) -> 'dict'`

## Description

Select and review a physical table, frozen Contract and applicable Agreement.

## Parameters

table_id, contract_id : str | None, optional
    Preselect an exact logical table and frozen Contract. With no arguments,
    select from registered physical workspaces/tables and frozen versions.
contract_version : int | None, optional
    Exact positive frozen version to preselect; never a latest fallback.
workspace_id : str | None, optional
    Physical table workspace. With a supplied table, defaults to the current
    configured scope. Governance metadata stays in its central Lakehouse.
context : dict | None, optional
    Configured Governance notebook context.

## Return value

dict
    Widget, selection/review state, controls and review/activate/refresh actions.
    Opening changes no metadata. Backend mutation independently revalidates
    exact bindings, policy hashes and the reviewed current activation ID.

## Usage notes

Governance owns all central metadata, so selection uses Catalogue records
without opening Engineering workspaces. Actual Fabric permissions authorize
writes. Each physical activation selects one frozen Contract and at most one
Agreement; cross-workspace execution requires effective associated terms.
Retained revisions provide history independently of notebook promotion.

[Back to release overview](../index.md)
