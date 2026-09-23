# `scan_sql_access`

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

Configured target keys are related to catalogue rows by reconstructing the
canonical ``table_id`` from the configured item kind, target key, schema,
and table name. The catalogue ``layer`` classification is not used as a
physical item identifier.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_sql_access.py:245`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_sql_access.py#L245-L369">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Use for repeatable SQL permission inventory snapshots that should link back to governed FabricOps table identities.

Do not use as a complete Fabric authorization inventory; workspace and OneLake access are scanned separately.

Uses configured Warehouse and Lakehouse SQL analytics endpoints, preserves direct versus role-based permission evidence, expands schema/database scope across registered tables, and keeps unresolved observations visible.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_sql_access(
    catalogue_df,
    targets: str | list[str] | tuple[str, ...]='warehouse',
    environment_name: str | None=None,
    access_snapshot_id: str | None=None,
    spark_session=None,
    persist: bool=True,
    context: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = scan_sql_access(
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
| `environment_name` | `str \| None` | No | FabricOps configuration environment used for target resolution, catalogue filtering, and environment-labelled access rows. Defaults to the active FabricOps environment. Fabric authentication and execution identity continue to come from the active runtime. |
| `access_snapshot_id` | `str \| None` | No | Identifier shared by all rows in this scan. A UUID is generated when omitted. |
| `spark_session` | `object` | No | Spark session override used by the Fabric SQL connector. |
| `persist` | `bool` | No | Append normalized access rows to METADATA_DATA_ACCESS when True. |
| `context` | `dict[str, Any] \| None` | No | Active FabricOps context override. |

## Returns

Dictionary with normalized METADATA_DATA_ACCESS rows and unmatched observed SQL permissions.

### Return interpretation

Use result["access"] as the governed table-level snapshot and review result["unmatched"] for observed SQL permissions that were not registered in the Catalogue.

## Raises / Errors

Raises ValueError when no valid workspace data item target is supplied and propagates configured SQL endpoint read, Spark, or persistence errors.

### Common failure causes

- A workspace data item target is not configured or accessible.
- Canonical Catalogue physical identity does not match the observed SQL object.
- The scanning identity cannot read the SQL permission catalogue views.

## Notes

<div class="reference-docstring-notes" markdown="1">

This scans SQL-engine permission metadata only; it is not a complete Fabric
access inventory. Workspace and OneLake access are scanned by their own
access_scanner entrypoints. Direct item sharing and Power BI security are
outside this scanner's scope.
By default the normalized access rows are appended to METADATA_DATA_ACCESS;
pass persist=False for inspection-only scans. The scanner never changes permissions.

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
