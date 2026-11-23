# `scan_onelake_role_members`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Preview workaround for named OneLake role assignments with supplied group membership.


## Usage notes

UNSTABLE WORKAROUND: name resolution uses an undocumented regional Power BI portal endpoint. Its contract, minimum permissions, and availability can change. Supply the observed portal origin explicitly. Group membership is caller-supplied and unverified; automatic selectors remain unresolved.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = scan_onelake_role_members(workspace_id, lakehouse_id, portal_base_url=portal_origin, group_memberships={"Data Readers": ["alice@example.com"]})
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_onelake_role_members(
    workspace_id: str,
    item_id: str,
    *,
    portal_base_url: str,
    group_memberships: dict[str, list[str]] | None=None,
    access_token: str | None=None,
    catalogue_df=None,
    target: str | None=None,
    persist: bool=False,
    access_snapshot_id: str | None=None,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `workspace_id` | `str` | Yes | `—` | Physical workspace UUID containing the Lakehouse. |
| `item_id` | `str` | Yes | `—` | Lakehouse item UUID, not its SQL endpoint UUID. |
| `portal_base_url` | `str` | Yes | `—` | HTTPS wabi-*.analysis.windows.net origin observed in the portal Network panel. No tenant-specific host is inferred or built into the package. Redirects are refused; obtain the current origin if the portal moves. |
| `group_memberships` | `dict[str, list[str]] \| None` | No | `None` | Group object ID or exact display name mapped to user UPN strings, for example {"Data Readers": ["alice@example.com", "bob@example.com"]}. IDs take precedence over names. Ambiguous names are not expanded. Values are caller-supplied direct membership, not directory-verified. An UNKNOWN principal with a matching key is a caller-declared group. Nested groups are not expanded; provide their final user membership. An empty list means no users supplied, not a verified empty group. |
| `access_token` | `str \| None` | No | `None` | Current caller token; otherwise NotebookUtils getToken("pbi") is used. Never paste a browser bearer token into a shared notebook. |
| `catalogue_df` | `pyspark.sql.DataFrame` | No | `None` | Active METADATA_DATA_CATALOGUE rows. Required for mapping or persistence. |
| `target` | `str \| None` | No | `None` | Configured Lakehouse store key. Must match workspace_id and item_id. |
| `persist` | `bool` | No | `False` | Write mapped observations to METADATA_DATA_ACCESS. Requires Catalogue, target, configured Metadata Lakehouse, metadata write permission, and setup_metadata_tables() after upgrading the package. Permissions remain unchanged. |
| `access_snapshot_id` | `str \| None` | No | `None` | Snapshot identity, generated when omitted. Reuse only to retry the same immutable observation set; writes use a transaction identity to avoid duplication. |
| `context` | `dict[str, Any] \| None` | No | `None` | FabricOps configured metadata routing and notebook audit context. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = scan_onelake_role_members(
    workspace_id, lakehouse_id, portal_base_url=portal_origin,
    group_memberships={"Data Readers": ["alice@example.com"]},
)
import pandas as pd
display(pd.DataFrame(result["role_members"]))
display(pd.DataFrame(result["users"]))
display(pd.DataFrame(result["coverage"]))
saved = scan_onelake_role_members(
    workspace_id, lakehouse_id, portal_base_url=portal_origin,
    group_memberships={"Data Readers": ["alice@example.com"]},
    catalogue_df=catalogue_df, target="Silver", persist=True,
)
display(saved["access"])
display(saved["unmatched"])
```

</div>

## Returns

dict[str, Any]
    Python records: role_members, workspace_assignments, item_access, users, coverage,
    raw_roles, raw_workspace_assignments, and raw_item_access. The users
    records retain the originating principal fields; user_principal names
    the resolved user and identity_source distinguishes API users from
    supplied membership. Email and principal type can remain unknown.
    Rule JSON retains paths, actions, and restrictions unchanged. Automatic
    membership stays a selector, not a list of users. Portal permission
    bitmasks stay raw and are never interpreted. Always inspect coverage;
    missing rows do not establish absence of access. With catalogue_df,
    access and unmatched are Spark DataFrames; otherwise both are None.
    access_snapshot_id identifies the scan. persist=True saves mapped rows
    including unresolved groups/selectors and supplied users, with original
    rules and assignment provenance in permission_details_json. Every saved
    row is UNVERIFIED effective access. Item bitmasks are stored as observations,
    never converted into table data grants. No permissions are changed.

## Raises / Errors

ValueError
    If UUIDs, the portal origin, or membership mappings are invalid.
RuntimeError
    If authentication or the primary OneLake role read fails. Workspace
    and portal failures instead appear in coverage with available role
    observations retained; partial source pages are discarded on failure.

## Notes

<div class="reference-docstring-notes" markdown="1">

Workspace assignment listing requires Member or Admin plus Workspace API
scope; Contributor is insufficient. OneLake role listing documents item
Read permission plus OneLake API scope. The undocumented portal endpoint's
minimum rights and stability are unverified: a successful caller test does
not establish support for all Members. Notebook and Environment access are
separate prerequisites. Scheduled/service-principal execution is untested.
Public API permission references:
https://learn.microsoft.com/rest/api/fabric/core/workspaces/list-workspace-role-assignments
and https://learn.microsoft.com/rest/api/fabric/core/onelake-data-access-security/list-data-access-roles.
Group expansion describes supplied assignments, not confirmed effective
access. The current caller token never grants additional permissions.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

This is an unstable inventory workaround, not a supported Microsoft API
integration or an effective-access verifier. It joins public OneLake roles
and Workspace assignments to names returned by the undocumented Power BI
portal item-access endpoint. No Graph or tenant-admin API is called.
Inspection requires no FabricOps setup or Spark. Optional Catalogue mapping
writes observed permission snapshots through the configured Metadata Lakehouse.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_onelake_role_members.py:417`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_onelake_role_members.py#L417-L618">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.5.1 |


</details>
