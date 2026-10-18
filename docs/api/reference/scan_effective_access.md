# `scan_effective_access`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Discover visible Fabric data items and resolve effective table access to individual users.


## Usage notes

Use when you have caller-supplied identity and group-membership mappings and need a read-only person-level Workspace, SQL, and OneLake access report.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = scan_effective_access(identity_map_df=identity_map_df, group_membership_df=group_membership_df)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def scan_effective_access(*, identity_map_df, group_membership_df) -> dict[str, Any]
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `identity_map_df` | `pyspark.sql.DataFrame` | Yes | `—` | Principal directory snapshot with ``object_id``, ``display_name``, ``user_principal_name``, ``principal_type``, and ``group_type``. Object IDs remain the stable join keys and readable fields are copied to the person-level result. |
| `group_membership_df` | `pyspark.sql.DataFrame` | Yes | `—` | Caller-supplied group edges with ``group_object_id`` and ``member_object_id``. Supply transitive source edges; FabricOps performs the recursive expansion and cycle detection. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = scan_effective_access(
    identity_map_df=identity_map_df,
    group_membership_df=group_membership_df,
)
display(result["access"])
display(result["coverage"])
```

</div>

## Returns

dict[str, pyspark.sql.DataFrame]
    ``access`` contains consolidated person/table/surface observations,
    explicit verification status, confirmed effective permissions, and
    provenance. ``coverage`` contains visibility gaps, unsupported cases,
    restrictions, contradictions, and errors.

### Return interpretation

Filter result["access"] to access_verification_status == "CONFIRMED" for established effective permissions; review UNVERIFIED and NOT_EFFECTIVE observations with result["coverage"].

## Raises / Errors

ValueError
    If either DataFrame lacks required columns or the DataFrames belong to
    different Spark sessions.

### Common failure causes

- The caller cannot list workspace role assignments or OneLake roles.
- Direct item assignments or the SQL endpoint access mode cannot be established through supported read-only interfaces.
- The identity or membership mapping is incomplete.
- DefaultReader differs from its assumed baseline or a permission is restricted.

## Behavior and scope

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

## See also

- [Scan Effective Data Access](../../solutions/effective-data-access.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/access_scanner/scan_effective_access.py:1642`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/access_scanner/scan_effective_access.py#L1642-L1752">View on GitHub</a>
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
