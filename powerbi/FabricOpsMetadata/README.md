# FabricOps Metadata Dashboard

This Power BI Desktop Project provides a portable, Import-mode operational dashboard over the canonical FabricOps metadata tables.

Open [`FabricOpsMetadata.pbip`](FabricOpsMetadata.pbip) in Power BI Desktop. The project contains a PBIR report definition and a TMDL semantic model; it does not contain cached data, deployment identifiers, or a reporting copy of FabricOps metadata.

## What is included

The report has six pages:

1. **01 — Overview** summarizes registered assets, workspaces, frozen Contract versions, pipeline runs and Data Quality indicators.
2. **02 — Data Catalogue** provides workspace, layer, store, table and column inventory with writer and profile-freshness context.
3. **03 — Governance** covers Data Stewards, Data Agreements, Data Contract versions and persisted Guardrail status.
4. **04 — Data Quality** shows null and distinct statistics, Profile history, frequent values and Guardrail outcomes.
5. **05 — Pipeline Operations** covers scalar run headers and Processing State outcomes.
6. **06 — Lineage & Access** shows source/target pipeline participation and observed permissions.

The report deliberately describes `METADATA_DATA_LINEAGE` as pipeline participation. It does not claim transformation-level lineage. `METADATA_DATA_ACCESS` contains observed permissions and does not resolve effective access.

## Prerequisites

- Power BI Desktop with Power BI Project (`.pbip`), PBIR and TMDL support enabled.
- Read access to the Fabric Metadata Lakehouse SQL analytics endpoint.
- Permission to read the configured Governance and Engineering schemas.
- The 12 canonical metadata tables created by the current FabricOps Starter Kit.

Use a recent Power BI Desktop release. In older builds, enable **Power BI Project save option**, **Store semantic model using TMDL format**, and **Store reports using enhanced metadata format (PBIR)** under Preview features, then restart Desktop.

## Configure the connection

The project uses four deployment-neutral parameters and one compatibility switch. No workspace or Lakehouse ID is stored in the project.

| Parameter | Default | Set it to |
| --- | --- | --- |
| `pSqlEndpoint` | placeholder | The SQL analytics endpoint server, such as `abc123.datawarehouse.fabric.microsoft.com`. |
| `pDatabaseName` | placeholder | The Metadata Lakehouse SQL endpoint database name. Copy the value shown by Fabric rather than assuming it always matches the display name. |
| `pGovernanceSchema` | `governance` | The configured `governance_metadata_schema`. |
| `pEngineeringSchema` | `engineering` | The configured `engineering_metadata_schema`. |
| `pLoadComplexBearingTables` | `true` | Whether to query scalar projections from the three tables that also contain native complex columns. |

In Power BI Desktop:

1. Open `FabricOpsMetadata.pbip`.
2. Select **Transform data > Manage parameters**.
3. Replace `pSqlEndpoint` and `pDatabaseName`; adjust schema parameters only if the FabricOps deployment uses non-default schema names.
4. Keep `pLoadComplexBearingTables` set to `true` for the first refresh.
5. Select **Refresh** and authenticate with an **Organizational account** that can read the Lakehouse SQL analytics endpoint.
6. Confirm that all 12 canonical queries load and that the Overview cards populate.

The shared `FabricOpsSqlTable` Power Query function uses `Sql.Database` and a native `SELECT` that names only supported scalar columns. Each semantic table is configured with `mode: import`.

## Native ARRAY and STRUCT boundary

FabricOps keeps native ARRAY and STRUCT values in the authoritative Delta tables. The Lakehouse connector used by Power BI Import mode reads through the Lakehouse SQL analytics endpoint, whose relational surface does not expose native Spark ARRAY and STRUCT values as normal Power BI columns.

The model therefore excludes only these complex columns from its SQL projections:

| Table | Native columns retained only in Delta |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | `load_strategy_parameters_json`, `scheduled_refresh_json`, `profile_key_candidates_json` (their implemented types are STRUCT despite the historical suffix) |
| `METADATA_PIPELINE_REGISTRY` | `registrations`, `revisions`, `approvals`, `selections`, `table_ownership`, `reservations` |
| `METADATA_PIPELINE_RUN` | `operations`, `profiling`, `failures` |

No source table, schema, or complex value is changed, flattened, serialized, or copied by this project.

Some SQL analytics endpoint versions omit an entire Delta table when any unsupported complex column is present. If refresh reports that one of the three tables is unavailable, set `pLoadComplexBearingTables` to `false`. The model then creates explicit empty, typed projections for those three tables while continuing to refresh the nine fully scalar tables. This compatibility mode is intentionally user-selected; it is not applied silently.

When compatibility mode is required:

- Data Catalogue inventory, Pipeline Registry authority and Pipeline Run header visuals that depend on those tables are empty.
- Governance, Profile, Guardrail, Processing State, Lineage and Access reporting continues where its source tables are exposed.
- Nested Registry approvals and ownership, Run Read/Write modes, stages, source associations, and loaded/already-loaded/skipped operation outcomes are not claimed by the report.

Do not create flattened persisted reporting tables to work around this connector boundary. Re-enable `pLoadComplexBearingTables` when the endpoint exposes scalar projection from mixed-type tables.

## Refresh and publish

After a successful Desktop refresh:

1. Save the project and publish the report to the target Fabric workspace.
2. In the published semantic model settings, open **Data source credentials** and authenticate the SQL analytics endpoint with OAuth2/Organizational account.
3. Confirm the parameter values in the service.
4. Configure **Scheduled refresh** at the operational cadence required by the deployment.
5. Run **Refresh now** once and inspect refresh history before enabling the schedule.

The SQL analytics endpoint is a cloud source, so an on-premises gateway is normally unnecessary. Tenant policy, private networking, conditional access, or a managed private endpoint can still require deployment-specific connectivity configuration.

Publishing creates the normal Power BI semantic model and report artifacts. It does not create another FabricOps metadata persistence layer. Refresh imports the current scalar reporting projection into the Power BI semantic model cache.

## Model behavior

The semantic model uses workspace-table and exact Contract composite keys generated during Power Query evaluation. These keys exist only inside the imported model. Dimensions filter facts one way, and facts are not joined directly to one another, preventing Profile, Frequency, Guardrail, Processing State and run grains from multiplying each other.

`Date` is a model-only calculated dimension. `DimTable`, `DimWorkspace`, and `DimPipeline` are semantic dimensions derived from imported canonical queries. See [`SOURCE_TO_MODEL.md`](SOURCE_TO_MODEL.md) for the full grain, relationship and complex-column mapping.

The **Frozen contracts** KPI counts immutable Frozen Data Contract versions. It is not labelled as activated Contracts because pipeline activation authority lives inside the native `METADATA_PIPELINE_REGISTRY.approvals` and `table_ownership` arrays.

## Validation boundary

Run the repository validator from the repository root:

```bash
PYTHONPATH=src python scripts/validate_fabricops_powerbi_project.py
```

The validator checks project layout, JSON, the 12 canonical table definitions, scalar source mappings, Import partitions, complex-column exclusions, relationships, measure references and six-page visual field references.

The following checks require Power BI Desktop and a signed-in Fabric environment:

- Power Query authentication and endpoint discovery.
- Actual table visibility for the tenant's SQL analytics endpoint version.
- Data type coercion against deployed rows.
- DAX evaluation with representative metadata.
- Visual rendering, interactions and accessibility in Desktop.
- Publication, credential binding and scheduled refresh in the Power BI service.

## Expected result

After configuration and refresh, another FabricOps deployment can open, refresh, publish and schedule this dashboard without editing source code or supplying any maintainer environment identifier.
