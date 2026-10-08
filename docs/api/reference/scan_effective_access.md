# `scan_effective_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Discover visible Fabric data items and resolve effective table access to individual users.

<div class="reference-docstring-intro" markdown="1">

The scan uses caller-scoped Workspace and Catalog Search APIs to discover
visible and directly shared Lakehouse and Warehouse items, then inventories
tables and the Workspace, SQL, and OneLake permission surfaces that the
caller can inspect. It uses the current Fabric notebook identity and does
not require FabricOps metadata, persistence, Microsoft Graph, a separately
supplied token, or Fabric Admin APIs.

``identity_map_df`` must contain ``object_id``, ``display_name``,
``user_principal_name``, ``principal_type``, and ``group_type``.
``group_membership_df`` must contain ``group_object_id`` and
``member_object_id``. Only groups whose ``group_type`` identifies a
security group are recursively expanded. Cycles are stopped, duplicate
edges are ignored, and every distinct inheritance path is retained.

Effective table access requires both applicable item-level access and an
applicable data permission. ``access`` therefore labels each person,
table, and permission surface as ``CONFIRMED``, ``UNVERIFIED``, or
``NOT_EFFECTIVE`` in ``access_verification_status``. Only confirmed
permissions appear in ``effective_permissions``; visible permissions that
still lack a verified prerequisite remain in ``observed_permissions`` and
provenance instead of being presented as effective.

Workspace roles establish item access and can also establish data access.
For Lakehouse Viewers, the scan preserves Fabric's normal DefaultReader
assumption: an unmodified DefaultReader role maps item ``ReadAll`` to
OneLake ``Read``. An observed conflicting configuration is reported in
``coverage`` and is not claimed as confirmed unrestricted access. The scan
never modifies DefaultReader.

SQL table permissions are effective only when item ``Read`` is established
and the SQL analytics endpoint is in delegated identity mode. In user
identity mode, OneLake Security governs table access and SQL table grants
are retained as ``NOT_EFFECTIVE`` evidence. If a supported read-only
mechanism cannot establish the mode, the SQL result remains
``UNVERIFIED``. SQL and OneLake permissions remain separate surfaces.

``contributing_grants_json`` retains all contributing item and data grants,
modes, restrictions, and inheritance paths. ``channel_permissions_json``
keeps SQL and OneLake capabilities distinct when one Workspace path
contributes to both channels. ``coverage`` records
inaccessible scopes, unresolved identities, incomplete group expansion,
unsupported permission shapes, applied denies, restrictions, scan errors,
and item-permission visibility gaps. A missing access row is therefore not
evidence that access does not exist; inspect ``coverage`` with every
result.

The function only reads permission metadata. It does not grant access,
modify DefaultReader, or persist results. OneLake row and column
constraints and SQL column restrictions are retained and flagged as
restricted instead of being presented as unrestricted table access.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_effective_access.py:1682`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_effective_access.py#L1682-L1792">View on GitHub</a>
</div>


## Usage notes

Use for an auditable, non-persisted effective data access review based on the scopes visible to the caller.

Do not treat UNVERIFIED observations or an empty access result as proof of effective access or denial; always inspect coverage.

Uses caller-scoped Workspace and Catalog Search APIs to discover visible and directly shared Lakehouses, Warehouses, and tables; combines item access with Workspace, SQL, and OneLake data permissions; distinguishes SQL authorization modes; recursively expands security groups; applies denies conservatively; and preserves every contributing path.


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

Dictionary with person/table/surface observations labelled CONFIRMED, UNVERIFIED, or NOT_EFFECTIVE, plus explicit coverage limitations.

### Return interpretation

Filter result["access"] to access_verification_status == "CONFIRMED" for established effective permissions; review UNVERIFIED and NOT_EFFECTIVE observations with result["coverage"].

## Raises / Errors

Raises ValueError for invalid mapping DataFrame schemas or mismatched Spark sessions; platform discovery failures are returned in coverage.

### Common failure causes

- The caller cannot list workspace role assignments or OneLake roles.
- Direct item assignments or the SQL endpoint access mode cannot be established through supported read-only interfaces.
- The identity or membership mapping is incomplete.
- DefaultReader differs from its assumed baseline or a permission is restricted.

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
