# `scan_workspace_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Scan observable SQL permissions for registered governed physical tables across configured Fabric workspace data items.

<div class="reference-docstring-intro" markdown="1">

The scanner reads SQL permission catalogue views through the existing
read-only SQL endpoint connector. Each configured Warehouse or Lakehouse SQL
analytics endpoint target is scanned separately, without dynamic
``DECLARE`` / ``EXEC`` SQL.

Direct permissions and permissions inherited through explicit database
role membership are returned separately. Object-level permissions map to
one registered table. Schema-level and database-level permissions expand to
every active registered physical table in that scope while preserving the
original SQL permission class in ``access_level``.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access/scan_workspace_access.py:249`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access/scan_workspace_access.py#L249-L347">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Use for repeatable SQL permission inventory snapshots that should link back to governed FabricOps table identities.

Do not use as a complete Fabric authorization inventory; workspace roles, item sharing, OneLake Security, and Power BI security are outside this scanner.

Uses configured Warehouse and Lakehouse SQL analytics endpoints, preserves direct versus role-based permission evidence, expands schema/database scope across registered tables, and keeps unresolved observations visible.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_workspace_access(
    catalogue_df,
    targets: str | list[str] | tuple[str, ...]='warehouse',
    environment_name: str | None=None,
    access_snapshot_id: str | None=None,
    spark_session=None,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = scan_workspace_access(
...     catalogue_df,
...     targets=["warehouse", "curated_lakehouse"],
...     spark_session=spark,
... )
>>> result["access"].display()
>>> result["unmatched"].display()

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `catalogue_df` | `pyspark.sql.DataFrame` | Yes | ``METADATA_DATA_CATALOGUE`` rows used to resolve observed SQL objects to canonical FabricOps ``table_id`` values. |
| `targets` | `str \| list[str] \| tuple[str, ...]` | No | One or more configured Warehouse or Lakehouse target keys from ``00_env_config`` whose SQL endpoints expose the supported catalogue views. |
| `environment_name` | `str \| None` | No | Metadata environment to scan. Defaults to the active FabricOps environment. |
| `access_snapshot_id` | `str \| None` | No | Identifier shared by all rows in this scan. A UUID is generated when omitted. |
| `spark_session` | `object` | No | Spark session override used by the Fabric SQL connector. |
| `context` | `dict[str, Any] \| None` | No | Active FabricOps context override. |

## Returns

Dictionary with access rows aligned to METADATA_DATA_ACCESS and unmatched observed permissions that could not be linked to a registered table.

### Return interpretation

Use result["access"] as the governed table-level snapshot and review result["unmatched"] for observed SQL permissions that were not registered in the Catalogue.

## Raises / Errors

Raises ValueError when no valid workspace data item target is supplied and propagates configured SQL endpoint read or Spark errors.

### Common failure causes

- A workspace data item target is not configured or accessible.
- Catalogue layer/schema/table identity does not match the observed SQL object.
- The scanning identity cannot read the SQL permission catalogue views.

## Notes

<div class="reference-docstring-notes" markdown="1">

This scans observable SQL permissions only; it is not a complete workspace
security inventory. Workspace roles, item sharing, OneLake Security, and
Power BI security are outside this scanner's scope. The function returns
DataFrames and never persists or changes permissions.

</div>

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
