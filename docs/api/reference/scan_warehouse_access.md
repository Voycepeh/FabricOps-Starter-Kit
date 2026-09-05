# `scan_warehouse_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Scan configured Fabric Warehouses for observable SQL permissions and link them to governed tables.

<div class="reference-docstring-intro" markdown="1">

The scanner reads SQL permission catalogue views through the existing
read-only ``read_warehouse_query`` entry point. Each configured Warehouse
target is scanned separately, so FabricOps does not need to execute dynamic
``DECLARE`` / ``EXEC`` SQL or weaken the read-only Warehouse IO contract.

Direct permissions and permissions inherited through explicit database
role membership are returned separately. Object-level permissions map to
one registered table. Schema-level and database-level permissions expand to
every active registered Warehouse table in that scope while preserving the
original SQL permission class in ``access_level``.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access/scan_warehouse_access.py:250`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access/scan_warehouse_access.py#L250-L335">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Use for repeatable SQL permission inventory snapshots that should link back to governed FabricOps table identities.

Do not use as a complete Fabric authorization inventory; workspace roles, item sharing, OneLake Security, and Power BI security are outside this scanner.

Uses the existing read-only Warehouse query helper, preserves direct versus role-based permission evidence, expands schema/database scope across registered tables, and keeps unresolved observations visible.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_warehouse_access(
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

```python
result = scan_warehouse_access(catalogue_df, targets="warehouse", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `catalogue_df` | `pyspark.sql.DataFrame` | Yes | ``METADATA_DATA_CATALOGUE`` rows used to resolve observed SQL objects to canonical FabricOps ``table_id`` values. |
| `targets` | `str \| list[str] \| tuple[str, ...]` | No | One or more configured Warehouse target keys from ``00_env_config``. |
| `environment_name` | `str \| None` | No | Metadata environment to scan. Defaults to the active FabricOps environment. |
| `access_snapshot_id` | `str \| None` | No | Identifier shared by all rows in this scan. A UUID is generated when omitted. |
| `spark_session` | `object` | No | Spark session override passed to ``read_warehouse_query``. |
| `context` | `dict[str, Any] \| None` | No | Active FabricOps context override. |

## Returns

Dictionary with access rows aligned to METADATA_DATA_ACCESS and unmatched observed permissions that could not be linked to a registered table.

### Return interpretation

Use result["access"] as the governed table-level snapshot and review result["unmatched"] for observed SQL permissions that were not registered in the Catalogue.

## Raises / Errors

Raises ValueError when no valid Warehouse target is supplied and propagates configured Warehouse read or Spark errors.

### Common failure causes

- A Warehouse target is not configured or accessible.
- Catalogue layer/schema/table identity does not match the observed SQL object.
- The scanning identity cannot read the SQL permission catalogue views.

## Notes

<div class="reference-docstring-notes" markdown="1">

This is a SQL permission inventory, not a complete Fabric authorization
inventory. Workspace roles, item sharing, OneLake Security, and Power BI
security are outside this scanner's scope.

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
