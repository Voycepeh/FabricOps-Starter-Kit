# `scan_workspace_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Scan Fabric workspace role assignments and expand them across registered governed tables.


## Usage notes

Use when you need the workspace-role path into governed table access for configured Fabric items.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = scan_workspace_access(catalogue_df, targets=["Silver", "Gold"])
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_workspace_access(
    catalogue_df,
    *,
    targets: str | list[str] | tuple[str, ...],
    environment_name: str | None=None,
    access_snapshot_id: str | None=None,
    access_token: str | None=None,
    persist: bool=True,
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
| `catalogue_df` | `pyspark.sql.DataFrame` | Yes | `—` | Active Data Catalogue rows for the configured environment. Its Spark session is used for mapping and persistence. |
| `targets` | `str \| list[str] \| tuple[str, ...]` | Yes | `—` | Configured Fabric store keys whose permissions should be inventoried. |
| `environment_name` | `str \| None` | No | `None` | Catalogue and configured-store environment; defaults to the active environment. |
| `access_snapshot_id` | `str \| None` | No | `None` | Shared scan identifier; a new UUID is generated when omitted. |
| `access_token` | `str \| None` | No | `None` | Fabric API token override; normally resolved from the notebook identity. |
| `persist` | `bool` | No | `True` | Append normalized rows to METADATA_DATA_ACCESS. Use False to inspect only. |
| `context` | `dict[str, Any] \| None` | No | `None` | FabricOps configuration and runtime context established by 00_env_config. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = scan_workspace_access(catalogue_df, targets="Silver", persist=False)
display(result["access"])
display(result["unmatched"])
```

</div>

## Returns

dict[str, pyspark.sql.DataFrame]
    ``observations`` holds raw permission observations; ``access`` holds
    normalized METADATA_DATA_ACCESS rows; ``unmatched`` holds observations
    that could not be linked to registered tables. Review unmatched rows
    before interpreting missing access as absence of permission.

### Return interpretation

Use result["access"] as the normalized workspace-derived table access snapshot and result["unmatched"] to identify role assignments with no registered scanned table.

## Raises / Errors

ValueError
    If targets are empty, invalid. Check configured store keys.
RuntimeError
    If Fabric authentication, REST discovery, or safe pagination fails.
    Spark mapping and metadata write errors also propagate; check Catalogue
    columns and permissions on the configured metadata target.

### Common failure causes

- The caller is below Workspace Member.
- The token lacks Workspace.Read.All or Workspace.ReadWrite.All.
- Configured targets do not match active Catalogue physical identities.

## Behavior and scope

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

## See also

- [Metadata reference](../../reference/metadata/metadata_data_access.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_workspace_access.py:145`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_workspace_access.py#L145-L270">View on GitHub</a>
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
| Preview | 0.2.5 |


</details>
