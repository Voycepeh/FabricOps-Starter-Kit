# `scan_effective_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Discover visible Fabric data items and resolve effective table access to individual users.

<div class="reference-docstring-intro" markdown="1">

The scan discovers every workspace visible to the caller, then inventories
supported Lakehouse and Warehouse tables and the Workspace, SQL, and
OneLake permission surfaces that the caller can inspect. It uses the
current Fabric notebook identity and does not require FabricOps metadata,
persistence, Microsoft Graph, a separately supplied token, or Fabric Admin
APIs.

``identity_map_df`` must contain ``object_id``, ``display_name``,
``user_principal_name``, ``principal_type``, and ``group_type``.
``group_membership_df`` must contain ``group_object_id`` and
``member_object_id``. Only groups whose ``group_type`` identifies a
security group are recursively expanded. Cycles are stopped, duplicate
edges are ignored, and every distinct inheritance path is retained.

Returns a dictionary containing ``access`` and ``coverage`` Spark
DataFrames. ``access`` has one row per person, table, and permission
surface, with all contributing grants serialized in
``contributing_grants_json``. ``coverage`` records inaccessible scopes,
unresolved identities, incomplete group expansion, unsupported permission
shapes, applied denies, restrictions, and scan errors. A missing access row
is therefore not evidence that access does not exist; inspect ``coverage``
with every result.

The function only reads permission metadata. It does not grant access or
persist results. SQL and OneLake permissions remain separate access
surfaces. OneLake row and column constraints are retained and flagged as
restricted instead of being presented as unrestricted table access.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_effective_access.py:1090`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_effective_access.py#L1090-L1171">View on GitHub</a>
</div>


## Usage notes

Use for an auditable, non-persisted effective data access review based on the scopes visible to the caller.

Do not treat an empty access result as proof of no access; always inspect coverage for caller visibility and unsupported restrictions.

Discovers accessible workspaces, Lakehouses, Warehouses, and tables; resolves Workspace roles, SQL grants and database roles, and OneLake roles; recursively expands security groups; applies denies conservatively; and preserves every contributing grant and inheritance path.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_effective_access(*, identity_map_df, group_membership_df) -> dict[str, Any]
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = scan_effective_access(
...     identity_map_df=identity_map_df,
...     group_membership_df=group_membership_df,
... )
>>> display(result["access"])
>>> display(result["coverage"])

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `identity_map_df` | `pyspark.sql.DataFrame` | Yes | Principal directory snapshot with ``object_id``, ``display_name``, ``user_principal_name``, ``principal_type``, and ``group_type``. Object IDs remain the stable join keys and readable fields are copied to the person-level result. |
| `group_membership_df` | `pyspark.sql.DataFrame` | Yes | Caller-supplied group edges with ``group_object_id`` and ``member_object_id``. Supply transitive source edges; FabricOps performs the recursive expansion and cycle detection. |

## Returns

Dictionary with consolidated person/table/surface access and explicit coverage limitations.

### Return interpretation

Use result["access"] for person/table/surface outcomes and result["coverage"] for inaccessible scopes, unresolved identities, incomplete group expansion, unsupported permissions, restrictions, and errors.

## Raises / Errors

Raises ValueError for invalid mapping DataFrame schemas or mismatched Spark sessions; platform discovery failures are returned in coverage.

### Common failure causes

- The caller cannot list workspace role assignments or OneLake roles.
- The identity or membership mapping is incomplete.
- An item or SQL permission shape is unsupported or restricted.

## See also

- [Scan Effective Data Access](../../solutions/effective-data-access.md)


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
