# Deployment and promotion

This guide is for Fabric environments where GitHub CI/CD is unavailable,
restricted, or not yet adopted. In that setup, use **Fabric deployment
pipelines** for notebook promotion and production metadata for audit
reconstruction.

<figure markdown>
  ![FabricOps deployment and promotion flow showing Dev workspace promotion through Fabric deployment pipelines into Production workspace, with versioning, audit, and storage records](assets/deployment.png){ .full-width }
  <figcaption>Fabric deployment pipelines promote approved notebook definitions. Production runs create the real production outputs and write audit evidence to the production metadata lakehouse.</figcaption>
</figure>

## What this guide helps you do

- Promote approved notebook code without GitHub CI/CD.
- Avoid copying dev output as production data.
- Run production notebooks against production config and storage.
- Keep enough evidence to explain historical datasets.

## Step 1: Prepare production once

Before promoting notebooks, production must already have or be provisioned with:

- production workspace
- production lakehouse or warehouse
- metadata lakehouse
- required metadata tables
- production `00_env_config`
- permissions
- Fabric environment or libraries
- schedules or orchestration

For metadata evidence ownership and required metadata concepts, see
[Metadata and Contracts](metadata-and-contracts/index.md).

## Step 2: Promote approved notebooks

Use Fabric deployment pipelines to promote selected approved notebooks from Dev
or Test to Prod. Fabric deployment pipelines promote notebook definitions and
other supported Fabric item definitions; they do not build the full production
data platform state.

Usually promote:

- approved `03_pc_*` pipeline contract notebooks
- shared helper notebooks, if the framework uses them

Usually do not promote blindly:

- `00_env_config`
- exploratory `02_ex_*` notebooks
- dev output data
- temporary debug notebooks

`00_env_config` should normally remain environment-local because Prod must point
to the production lakehouse, production warehouse, and production metadata
lakehouse. For notebook stage roles, see
[Notebook Structure](notebook-structure.md).

## Step 3: Validate production bindings

Before running the promoted notebook in production, check that:

- the notebook is using the production config
- output paths point to production storage
- metadata writes point to the production metadata lakehouse
- required metadata tables exist
- permissions and libraries are available
- schedules or triggers are correct

## Step 4: Run in production

Promotion only moves the notebook definition. The production dataset is created
only when the promoted notebook is run in the production workspace.

The normal pattern is:

1. run the promoted `03_pc_*` notebook in production;
2. write output tables or files to the production lakehouse or warehouse; and
3. write run evidence to the production metadata lakehouse.

## Step 5: Archive the notebook version used

When GitHub CI/CD is unavailable, keep a production **notebook version archive**.
For each production-ready notebook version, store:

- notebook name
- notebook path
- version id or release tag
- exported source or snapshot
- checksum or hash, if available
- promoted by
- approved by
- promotion timestamp

The archive proves what code was approved and available. The production run
summary must reference the archived notebook version that was actually used.

## Step 6: Record run evidence

For each production run, store a run summary in the metadata lakehouse with:

- run id
- run timestamp
- notebook name
- archived notebook version used
- output table, path, or snapshot
- contract version
- DQ rule version
- schema/profile evidence version
- approval reference
- run status
- row counts or quality result summary, if available

## Step 7: Reconstruct a historical dataset

If someone asks how a dataset was produced days, months, or years ago, start from
the run id or output table and retrieve:

- output data or snapshot
- run summary
- archived notebook version used
- contract version
- DQ rule version
- schema/profile evidence
- approvals
- production config reference

The run summary is the join point: it links one production run to the output
data, notebook version, rule version, contract version, and metadata evidence
used at that time.

## Minimal audit table

| Record | Stored in | Purpose |
| --- | --- | --- |
| Notebook version | Production lakehouse archive | Shows the code version approved for production |
| Run summary | Metadata lakehouse | Links one production run to code, rules, contract, and output |
| DQ rule version | Metadata lakehouse | Shows validation rules active at that time |
| Contract version | Metadata lakehouse | Shows expected schema, ownership, and controls |
| Output dataset/snapshot | Production lakehouse or warehouse | Shows what was produced |
