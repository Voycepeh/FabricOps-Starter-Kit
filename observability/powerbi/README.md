# FabricOps Observability v1

This directory contains a source-controlled Power BI Project (PBIP), not a design-only specification. Open [`FabricOpsObservability/FabricOpsObservability.pbip`](FabricOpsObservability/FabricOpsObservability.pbip) in Power BI Desktop with the Power BI Project save format enabled.

## What is included

- Four visible pages: **Overview**, **Engineering — Pipelines**, **Governance — Tables**, and **Data Owner — Tables**.
- Two hidden native drillthrough pages: **Pipeline Detail** (workspace-aware Pipeline Key, with an on-page Run selector) and **Table Detail** (workspace-aware Table Key).
- An Import semantic model in TMDL with explicit SQL projection, selective JSON extraction, DAX diagnostics, and workspace-aware composite keys.
- Explicit `DataFilter` interactions for every data-bearing visual pair. This forces cross-filtering rather than relying on a report default.
- A light, teal-accented report theme, an [all-page static preview](assets/all-pages-preview.svg), and a [semantic-model preview](assets/semantic-model-preview.svg). Preview values are explicitly illustrative.

## Connect to Fabric metadata

1. Open the `.pbip` in Power BI Desktop.
2. In **Transform data > Edit parameters**, set:
   - `MetadataServer`: the Fabric Lakehouse or Warehouse SQL analytics endpoint.
   - `MetadataDatabase`: the metadata Lakehouse or Warehouse database name.
   - `GovernanceSchema`: normally `governance`.
   - `EngineeringSchema`: normally `engineering`.
   - `WorkspaceFilter`: optional exact physical workspace ID. Blank keeps all workspaces.
   - `HistoryWindowDays`: pipeline/Guardrail history retained for trends; default `180`.
3. Sign in with an organizational account that has read access to the SQL endpoint.
4. Apply changes and refresh.
5. Confirm that the configured metadata target is the same target used by `00_env_config`; FabricOps does not assume the attached/default Lakehouse.

Schema parameters are restricted to letters, numbers, and underscore before they are inserted as identifiers. Workspace values are SQL-escaped. Every query explicitly names its source columns; no query uses `SELECT *`.

## Storage-mode decision

Import is intentional for v1. Direct Lake was evaluated, but the report needs selective relational extraction from JSON string columns (`operations`, `stages`, `failures`, and contract payload fragments). The SQL endpoint allows projection and filtering to occur before data reaches the model while keeping the PBIP portable. DirectQuery remains a possible deployment-specific alternative where latency requirements outweigh interactive performance. No persisted reporting tables or views are introduced.

## Navigation and descriptive semantics

Right-click a pipeline/run row on Engineering and choose **Drill through > Pipeline Detail**. Right-click a physical table on Governance or Data Owner and choose **Drill through > Table Detail**. Power BI supplies its native Back action for drillthrough. Detail-page selectors also provide a deliberate fallback and allow selection of one run. Selecting a run filters operations, stages, failures, and participating tables.

Governance shows all registered physical workspace/Table IDs. Data Owner uses the same table foundation; selecting a Steward filters provider/recipient Agreement participation through the exact Agreement version and latest physical Contract Activation. The model never treats Agreement participation as definitive table ownership.

Run outcomes remain descriptive and mutually distinguish **Successful**, **Failed**, and **Incomplete** records. Sequential stage output shows only what was recorded; an absent later stage is not inferred to have passed or failed. Duration is compared with the historical median without predicting a regression. There is no composite health score, automated recommendation, or RLS.

FabricOps supports `governed`, `ungoverned`, and `dry_run` modes. Ordinary Dry Run is session-only and is not guaranteed to be present in durable `METADATA_PIPELINE_RUN` history. Activation is different: every accepted submission carries a complete Dry Run inside `METADATA_PIPELINE_ACTIVATION.package_json`, and Governance appends its independent import/decision records. Engineering and Pipeline Detail show a selective summary of the submitted evidence alongside its decision status and review note. It is never added to Run Count because activation decisions and production runs have different grains; an imported record is not labelled as independently approved.

Table Detail reports the latest recorded access snapshot from existing `METADATA_DATA_ACCESS` rows. It does not run an access scan or claim to calculate effective access.

Pipeline Detail exposes conditional Fabric web links for recorded governed notebooks and Lakehouse/Warehouse destinations. URLs are constructed only when the required physical workspace/item IDs and a supported item kind are present; otherwise the link is blank. No notebook or runtime identifier is invented.

## Regeneration

Run `python observability/powerbi/tools/build_pbip.py` after editing the generator, then `python observability/powerbi/tools/validate_pbip.py`. Generated PBIP files are committed so reviewers do not need Python to open the project.

