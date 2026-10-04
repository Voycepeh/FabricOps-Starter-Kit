# Scan Effective Data Access

<span class="fabricops-release-status fabricops-release-status--preview">Preview</span>

![Effective data access scan](../assets/EffectiveAccessScan.png)

## The problem

Access to governed data in Microsoft Fabric is not represented by one permission list. A person or group can receive access through the workspace, through OneLake Security, or through the SQL analytics endpoint.

Looking at only one of those surfaces can give Governance an incomplete picture of who can reach a governed table.

## The solution

FabricOps scans the three supported permission paths and normalizes the observations against governed table identities:

1. **Workspace roles** — access inherited from Fabric workspace roles.
2. **OneLake Security roles** — access granted through OneLake data access roles for Lakehouse targets.
3. **SQL endpoint grants** — direct SQL permissions and permissions inherited through explicit database roles.

The scanners write normalized observations to `METADATA_DATA_ACCESS`, giving Governance one place to review table-level access evidence across the supported paths.

!!! important "A scan is only as complete as the execution identity can see"
    FabricOps uses the credentials available to the notebook or pipeline that runs the scan. If that execution identity cannot read a permission surface, the scanner cannot report permissions hidden behind it. **A missing access row is therefore not proof that no access exists.**

## How it works

| Permission path | What FabricOps observes | How it is mapped |
| --- | --- | --- |
| **Workspace roles** | Fabric workspace role assignments | Workspace access is expanded across active governed tables in the scanned workspace. Viewer is normalized to `READ`; Admin, Member, and Contributor are normalized to `READWRITE`. |
| **OneLake Security roles** | OneLake data access roles for configured Lakehouses | Supported table and schema paths are mapped to registered FabricOps `table_id` values. Explicit members and automatic item-access selectors are preserved as observed. |
| **SQL endpoint grants** | SQL permission catalogue views for configured Warehouse and Lakehouse SQL analytics endpoints | Object permissions map to a table; schema and database permissions expand to active governed tables in scope. Direct grants and explicit database-role inheritance remain distinguishable. |

Each scanner preserves evidence from its own permission surface rather than pretending one scanner represents all Fabric authorization.

Groups are also preserved as groups where the underlying permission surface returns them. FabricOps does not use Microsoft Graph to expand group membership into individual users, so the access snapshot should be read as normalized permission evidence, not as a fully flattened identity graph.

<details markdown="1">
<summary><strong>Under the hood: permission paths and visibility</strong></summary>

### Workspace access

`scan_workspace_access()` reads workspace role assignments for the workspaces containing the configured targets. Each unique workspace is scanned once, and the observed role is retained alongside the normalized access level.

### OneLake access

`scan_onelake_access()` reads the Fabric `dataAccessRoles` endpoint for configured Lakehouse targets. It preserves explicit Entra members and automatic Fabric item-membership selectors, then maps supported OneLake table or schema paths back to governed tables.

### SQL access

`scan_sql_access()` reads SQL permission catalogue views through the existing read-only SQL endpoint connector. It captures both direct permissions and permissions inherited through explicit database-role membership, then maps the observed SQL objects back to canonical FabricOps `table_id` values.

### Why execution identity matters

The scanners do not run with a separate privileged governance identity. They use the authentication available to the current Fabric runtime.

That means two executions can observe different permission evidence if their identities have different rights to inspect Fabric APIs or SQL permission metadata. FabricOps can normalize what it can observe, but it cannot infer permissions that the execution identity is not authorized to read.

Treat scanner failures, unmatched observations, and unavailable permission surfaces as visibility signals that need investigation. Do not convert absence of evidence into evidence of no access.

The scanners are read-only with respect to permissions: they inventory access but do not grant, revoke, or change it.

</details>

## Example

<details markdown="1">
<summary><strong>Example: one governed table, multiple access paths</strong></summary>

Suppose `orders` is a governed Production table.

A workspace scan may show that a workspace **Viewer** can read the table through the workspace role. A OneLake scan may separately observe a OneLake Security role that includes the table. A SQL scan may also find a `SELECT` permission granted directly or through an explicit database role.

FabricOps maps those observations back to the same governed table identity so Governance can review the supported permission paths together.

If the execution identity can read the workspace assignments and SQL catalogue views but cannot read OneLake Security roles, the resulting snapshot is **partial**. The absence of a OneLake row does not mean the table has no OneLake access; it means that permission surface was not observable to that execution.

</details>

## Go deeper

For exact scanner behaviour, inputs, outputs, and failure conditions, see:

- [`scan_workspace_access()`](../api/reference/scan_workspace_access.md)
- [`scan_onelake_access()`](../api/reference/scan_onelake_access.md)
- [`scan_sql_access()`](../api/reference/scan_sql_access.md)
- [`METADATA_DATA_ACCESS`](../reference/metadata/metadata_data_access.md)

For the wider Governance and Engineering model, see [How FabricOps Works](../how-fabricops-works.md).
