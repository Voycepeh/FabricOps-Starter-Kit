# Scan Effective Data Access

<span class="fabricops-release-status fabricops-release-status--preview">Preview</span>

Resolve which actual people can access visible Fabric tables, through which permission surface, and why.

![Effective data access scan](../assets/EffectiveAccessScan.png){ .fabricops-solution-hero }

## The problem

Access to governed data in Microsoft Fabric is not represented by one permission list. A person or security group can receive access through the Workspace, through OneLake Security, or through the SQL analytics endpoint.

Looking at only one surface can therefore give Governance an incomplete picture of who can reach a table.

## The solution

FabricOps provides one read-only scan that discovers the Fabric scopes visible to the caller and resolves three supported permission paths to actual people and tables:

1. **Workspace roles** — access inherited from Fabric Workspace roles.
2. **OneLake Security roles** — access granted through OneLake data access roles for Lakehouses.
3. **SQL endpoint grants** — direct SQL permissions and permissions inherited through explicit database roles.

The caller supplies identity and group-membership mappings as Spark DataFrames. The result keeps SQL and OneLake as separate access surfaces, consolidates overlapping grants by person and table, and preserves every contributing grant and inheritance path. No FabricOps metadata initialization or persistence target is required.

!!! important "A scan only sees what the account running it can see"
    FabricOps uses the account that runs the notebook. If that account cannot inspect a permission surface, FabricOps records the limitation in `coverage`. **A missing access row is not proof that no access exists.**

## How it works

| Permission path | FabricOps observes | Result |
| --- | --- | --- |
| **Workspace roles** | Fabric Workspace role assignments | Workspace grants retain their origin and list the applicable data channels: SQL for Viewer, and SQL plus OneLake for elevated Lakehouse roles. |
| **OneLake Security roles** | `dataAccessRoles` for discovered Lakehouses | Explicit users and security groups resolve to people; supported table and schema paths remain a distinct OneLake surface. |
| **SQL endpoint grants** | SQL permission catalogue views | Direct grants and database-role grants expand across their database, schema, table, or column scope without becoming OneLake file access. |

Security groups expand recursively from `group_membership_df`. FabricOps detects cycles, removes duplicate edges, preserves distinct inheritance paths, and does not treat distribution-list membership as access-bearing. `identity_map_df` supplies the Object ID, display name, UPN, principal type, and group type needed for readable results without Microsoft Graph.

## Under the hood

<details class="fabricops-solution-details" markdown="1">
<summary><strong>How the effective access scan combines permission surfaces</strong></summary>

![How FabricOps scans effective data access](../assets/effective-data-access-implementation.svg){ .fabricops-solution-diagram }

`scan_effective_access()` reuses the lower-level Workspace, SQL endpoint, and OneLake scanning foundations while owning discovery, identity resolution, group expansion, and consolidation:

- Fabric REST discovers workspaces, supported items, Workspace roles, Lakehouse tables, and OneLake `dataAccessRoles` visible to the caller.
- The existing read-only SQL endpoint connector discovers Warehouse or schema-enabled Lakehouse tables and reads SQL grants and explicit database-role permissions.
- Caller-supplied mappings resolve principal Object IDs and recursively expand security groups to individual users.
- FabricOps consolidates one row per person, table, and access surface while retaining grant provenance and inheritance paths.

The returned `coverage` DataFrame records inaccessible scopes, unresolved identities, incomplete group expansion, unsupported permissions, restrictions, applied denies, and scan errors. Automatic OneLake item-permission selectors are never reported as people; when non-admin APIs cannot enumerate direct item shares, that limitation remains explicit in `coverage`.

The scan is read-only with respect to permissions and results: it does not grant, revoke, change, or persist anything.

</details>

## Example

<details class="fabricops-solution-details" markdown="1">
<summary><strong>One table, multiple access paths</strong></summary>

![One governed table can have access through multiple permission paths](../assets/effective-data-access-example.svg){ .fabricops-solution-diagram }

```python
from fabricops_kit import scan_effective_access

result = scan_effective_access(
    identity_map_df=identity_map_df,
    group_membership_df=group_membership_df,
)

display(result["access"])
display(result["coverage"])
```

`identity_map_df` contains `object_id`, `display_name`, `user_principal_name`, `principal_type`, and `group_type`. `group_membership_df` contains `group_object_id` and `member_object_id`.

If the caller can inspect Workspace and SQL permissions but cannot inspect OneLake Security, FabricOps returns the visible Workspace and SQL results and records the OneLake failure in `coverage`.

</details>

## Go deeper

For the one-call contract, lower-level scanner behavior, and optional metadata snapshots, see:

- [`scan_effective_access()`](../api/reference/scan_effective_access.md)
- [`scan_workspace_access()`](../api/reference/scan_workspace_access.md)
- [`scan_onelake_access()`](../api/reference/scan_onelake_access.md)
- [`scan_sql_access()`](../api/reference/scan_sql_access.md)
- [`METADATA_DATA_ACCESS`](../reference/metadata/metadata_data_access.md)

For the wider Governance and Engineering model, see [How FabricOps Works](../how-fabricops-works.md).
