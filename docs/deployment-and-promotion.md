# Deployment and promotion

This page is for Fabric environments where GitHub CI/CD is unavailable,
restricted, or not yet adopted. FabricOps can still work in that setup by using
**Fabric deployment pipelines** for controlled notebook promotion, plus
production-side archival for audit reconstruction.

The fallback pattern is simple: promote approved notebook definitions with
Fabric deployment pipelines, run them in production, and store enough production
evidence to explain what happened days, months, or years later.

<figure markdown>
  ![FabricOps deployment and promotion flow showing Dev workspace promotion through Fabric deployment pipelines into Production workspace, with versioning, audit, and storage records](assets/deployment.png){ .full-width }
  <figcaption>Deployment pipelines promote approved notebook definitions, while production runs create the production data and write audit evidence into the production metadata lakehouse.</figcaption>
</figure>

## What Fabric deployment pipelines are used for

Use Fabric deployment pipelines to promote selected, approved notebooks from Dev
to Test or Prod. They are useful for controlled movement of notebook code and
supported Fabric item definitions between workspaces.

In FabricOps, Fabric deployment pipelines are not treated as the complete release
or audit system. They are one part of the operating model: they move supported
items, while the production workspace creates production results and records the
evidence needed for audit reconstruction.

## What Fabric deployment pipelines do not solve

Fabric deployment pipelines do not magically recreate the full production data
platform state. They can move supported Fabric item definitions, especially
notebooks, but production still needs the following to be built, configured,
validated, and run in the production environment:

- target workspaces
- production lakehouse and warehouse items
- metadata lakehouse
- required metadata tables
- environment config
- permissions
- libraries or Fabric environments
- schedules
- orchestration
- deployment rules
- validation runs
- production data generation

Treat Fabric deployment pipeline promotion as movement of approved definitions,
not as proof that production is ready or that production data already exists.

## Production is where production data is created

Dev notebooks may be promoted, but production datasets must be built by running
the promoted production notebooks inside the production workspace, against
production config, production metadata, and production storage.

Do not copy dev output data as the authoritative production result unless the
organization has a separate approved process for that. The normal FabricOps
pattern is:

1. promote approved notebook definitions;
2. validate the production workspace, metadata lakehouse, bindings, permissions,
   and schedules;
3. run the promoted `03_pc_*` notebooks in production; and
4. write production outputs plus audit evidence from the production run.

For notebook stage ownership and the role of `02_ex_*` and `03_pc_*` notebooks,
see [Notebook Structure](notebook-structure.md).

## Environment local config

`00_env_config` should usually stay environment local.

- Dev config points to dev storage and dev metadata.
- Test config points to test storage and test metadata.
- Prod config points to prod storage and prod metadata.

Promoting config blindly risks cross-environment reads and writes. Keep the
production bindings explicit, reviewed, and local to the production workspace
unless your organization has a controlled config promotion process.

## Notebook version archival

When GitHub CI/CD is unavailable, keep an explicit **notebook version archive**
in the production lakehouse. The archive can be a managed table, file area, or
both, but it should be controlled from production and retained as audit evidence.

When a notebook is promoted or approved for production, store a snapshot of the
notebook source or exported notebook content with:

- notebook name
- notebook path
- version id or release tag
- checksum or hash, if available
- promoted by
- approved by
- promotion timestamp
- source workspace
- target workspace
- related pipeline contract id
- related run id, where applicable

The notebook version archive proves what code was approved and available to run
in production, even when there is no GitHub release record to reconstruct from.

## Metadata and rule archival

Data quality rules, contracts, schema profiles, approvals, lineage summaries, run
summaries, and governance decisions should be stored in the **metadata
lakehouse**. These records should be versioned or time effective so a production
run can reference the exact evidence it used.

A production run should record the exact contract version, DQ rule version,
notebook version, schema/profile evidence, and governance metadata used for that
run. This is what turns a run from “a notebook executed” into an auditable data
product event.

For the metadata evidence model, see
[Metadata and Contracts](metadata-and-contracts/index.md).

## Reconstructing a historical result

Audit reconstruction is the core goal. If someone asks how a dataset was
produced six months ago, the team should be able to retrieve:

- the production output table or snapshot for that run;
- the run summary;
- the contract version;
- the DQ rule version;
- the schema/profile evidence;
- the lineage or transform summary;
- the archived notebook version;
- the production config reference; and
- the approval and promotion records.

That evidence should answer practical audit questions:

1. What dataset or value was produced on the historical run?
2. What production data snapshot or output table existed at that time?
3. What data quality rules, contracts, approvals, schema/profile evidence, and
   governance metadata were active at that time?
4. What notebook code version produced the result?
5. Which environment config and production bindings were used?
6. Who approved or promoted the relevant contract, rule, and code state?

This is the point of the deployment model: not just promoting code, but
preserving enough evidence to understand historical data products.

## Recommended operating flow

### Dev

- Build and test `02_ex_*` and `03_pc_*` notebooks.
- Profile data.
- Draft contracts and DQ rules.
- Capture metadata evidence.
- Get human approval.

### Fabric deployment pipeline

- Promote selected approved notebooks.
- Apply deployment rules for target bindings where supported.
- Do not assume data or metadata state is automatically complete.

### Prod setup

- Provision or validate the production lakehouse, warehouse, metadata store,
  permissions, libraries, schedules, and config.
- Confirm required metadata tables exist in the production metadata lakehouse.
- Confirm production bindings point to production storage and metadata.

### Prod run

- Run promoted `03_pc_*` notebooks in production.
- Write outputs to the production lakehouse or warehouse.
- Write run metadata, rule results, contract references, lineage summaries, and
  audit evidence to the production metadata lakehouse.
- Archive the notebook version used for the run.

## What to store where

| Artifact | Where it lives | Why it matters for audit |
| --- | --- | --- |
| Promoted notebook code | Production notebook archive table or file area | Proves what code ran |
| DQ rules | Metadata lakehouse | Proves what validation logic was active |
| Data contract | Metadata lakehouse | Proves expected schema, ownership, controls, and approvals |
| Run summary | Metadata lakehouse | Links output data, notebook version, rule version, and contract version |
| Output dataset or table snapshot | Production lakehouse or warehouse | Shows what was produced at that time |
| Environment config reference | Production metadata or run summary | Proves which prod bindings were used |

## Admin notebooks

Use explicit admin notebooks for cross-environment operations. Keep them small,
reviewable, and focused on one administrative task at a time.

Examples:

- `90_admin_validate_prod_setup`
- `90_admin_promote_contract_dev_to_prod`
- `90_admin_compare_contract_dev_prod`
- `90_admin_archive_prod_notebook_version`
- `90_admin_reconstruct_run_audit_package`

Admin notebooks should write their approval, comparison, promotion, and archive
records to the metadata lakehouse or notebook version archive so they are part of
the same audit reconstruction trail.
