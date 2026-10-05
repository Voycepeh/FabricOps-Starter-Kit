# `scan_workspace_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Scan Fabric workspace role assignments and expand them across registered governed tables.

<div class="reference-docstring-intro" markdown="1">

The scanner reads Fabric workspace role assignments for the workspaces that
contain the configured targets. Each unique workspace is scanned once.
Viewer is normalized to READ, while Admin, Member, and Contributor are
normalized to READWRITE. The original workspace role is retained in
role_name. Users use the UPN exposed by Fabric; groups and other principal
types remain separate records and are not expanded into members.

Rows are appended to METADATA_DATA_ACCESS by default. Pass persist=False to
inspect the result without writing metadata.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_workspace_access.py:195`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_workspace_access.py#L195-L278">View on GitHub</a>
</div>

## Usage notes

Use for repeatable workspace-role access inventory snapshots.

Do not use as an effective-access resolver; OneLake and SQL access are scanned separately.

Scans each unique configured workspace once, preserves the original workspace role, normalizes Viewer to READ and Admin/Member/Contributor to READWRITE, and expands that access across active registered tables in scanned items.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_workspace_access(
    catalogue_df,
    targets: str | list[str] | tuple[str, ...],
    environment_name: str | None=None,
    access_snapshot_id: str | None=None,
    access_token: str | None=None,
    persist: bool=True,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = scan_workspace_access(catalogue_df, targets=["Silver", "Gold"])
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `catalogue_df` | `—` | Yes | Not documented yet |
| `targets` | `str \| list[str] \| tuple[str, ...]` | Yes | Not documented yet |
| `environment_name` | `str \| None` | No | Not documented yet |
| `access_snapshot_id` | `str \| None` | No | Not documented yet |
| `access_token` | `str \| None` | No | Not documented yet |
| `persist` | `bool` | No | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |

## Returns

Dictionary with raw workspace observations, normalized METADATA_DATA_ACCESS rows, and unmatched role assignments.

### Return interpretation

Use result["access"] as the normalized workspace-derived table access snapshot and result["unmatched"] to identify role assignments with no registered scanned table.

## Raises / Errors

Raises for invalid targets, Fabric REST authentication or permission failures, and Spark mapping or persistence failures.

### Common failure causes

- The caller is below Workspace Member.
- The token lacks Workspace.Read.All or Workspace.ReadWrite.All.
- Configured targets do not match active Catalogue physical identities.

## See also

- [Metadata reference](../../reference/metadata/metadata_data_access.md)


<details>
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
| Preview | 0.2.0 |


</details>
