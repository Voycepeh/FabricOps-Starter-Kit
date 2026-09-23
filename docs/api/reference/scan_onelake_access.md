# `scan_onelake_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Scan OneLake Security roles and map Lakehouse table access to canonical FabricOps table identities.

<div class="reference-docstring-intro" markdown="1">

The scanner reads the Fabric dataAccessRoles REST endpoint for each configured
Lakehouse target. Explicit Entra members are preserved by object ID. Automatic
Fabric item membership used by roles such as DefaultReader is preserved as a
selector instead of being misrepresented as an individual user.

Normalized access rows are appended to METADATA_DATA_ACCESS by default.
Pass persist=False for an inspection-only scan. The scanner never changes
OneLake permissions.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_onelake_access.py:248`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_onelake_access.py#L248-L329">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Use for repeatable OneLake Security access inventory snapshots.

Do not use for Warehouse targets or as a full effective-access resolver.

Preserves explicit Entra members and automatic item-access selectors, expands supported OneLake table and schema paths to registered table_id values, and keeps unmatched Files or unknown paths visible.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_onelake_access(
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
result = scan_onelake_access(catalogue_df, targets="Silver")
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

Dictionary with raw OneLake observations, normalized METADATA_DATA_ACCESS rows, and unmatched paths.

### Return interpretation

Use result["access"] as the normalized OneLake table-level snapshot, result["observations"] for raw role detail, and result["unmatched"] for paths outside registered governed tables.

## Raises / Errors

Raises for non-Lakehouse targets, Fabric REST authentication or permission failures, unsafe continuation hosts, and Spark mapping or persistence failures.

### Common failure causes

- A target is not a Lakehouse.
- The token lacks OneLake.Read.All or OneLake.ReadWrite.All.
- A role path does not map to an active registered table.

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


</details>
