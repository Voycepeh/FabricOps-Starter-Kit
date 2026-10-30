# `scan_onelake_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Scan OneLake Security roles and map Lakehouse table access to canonical FabricOps table identities.


## Usage notes

Use when you need the OneLake Security path into governed Lakehouse table access.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = scan_onelake_access(catalogue_df, targets="Silver")
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_onelake_access(
    catalogue_df,
    *,
    targets: str | list[str] | tuple[str, ...],
    workspace_id: str | None=None,
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
| `catalogue_df` | `pyspark.sql.DataFrame` | Yes | `—` | Active Data Catalogue rows for the configured workspace_id. Its Spark session is used for mapping and persistence. |
| `targets` | `str \| list[str] \| tuple[str, ...]` | Yes | `—` | Configured Lakehouse keys whose permissions should be inventoried. |
| `workspace_id` | `str \| None` | No | `None` | Catalogue and configured-store workspace_id; defaults to the active workspace_id. |
| `access_snapshot_id` | `str \| None` | No | `None` | Shared scan identifier; a new UUID is generated when omitted. |
| `access_token` | `str \| None` | No | `None` | Fabric API token override; normally resolved from the notebook identity. |
| `persist` | `bool` | No | `True` | Append normalized rows to METADATA_DATA_ACCESS. Use False to inspect only. |
| `context` | `dict[str, Any] \| None` | No | `None` | FabricOps configuration and runtime context established by 00_env_config. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = scan_onelake_access(catalogue_df, targets="Silver", persist=False)
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

Use result["access"] as the normalized OneLake table-level snapshot, result["observations"] for raw role detail, and result["unmatched"] for paths outside registered governed tables.

## Raises / Errors

ValueError
    If targets are empty, invalid, or not Lakehouses. Check configured store keys.
RuntimeError
    If Fabric authentication, REST discovery, or safe pagination fails.
    Spark mapping and metadata write errors also propagate; check Catalogue
    columns and permissions on the configured metadata target.

### Common failure causes

- A target is not a Lakehouse.
- The token lacks OneLake.Read.All or OneLake.ReadWrite.All.
- A role path does not map to an active registered table.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

The scanner reads the Fabric dataAccessRoles REST endpoint for each configured
Lakehouse target. Explicit Entra members use a UPN or readable identity when
the response provides one and otherwise retain the Entra object ID. Groups
remain groups and are not expanded. Automatic Fabric item membership used by
roles such as DefaultReader is preserved as a selector instead of being
misrepresented as an individual user. No Microsoft Graph lookup is performed.

Normalized access rows are appended to METADATA_DATA_ACCESS by default.
Pass persist=False for an inspection-only scan. The scanner never changes
OneLake permissions.

</div>

## See also

- [Metadata reference](../../reference/metadata/metadata_data_access.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_onelake_access.py:158`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_onelake_access.py#L158-L283">View on GitHub</a>
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
| Preview | 0.3.0 |


</details>
