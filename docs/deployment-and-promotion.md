# Deployment and promotion
![Deployment](assets/deployment.png)

## Enterprise-friendly promotion model

FabricOps Starter Kit supports both Git-integrated and deployment-pipeline-centered workflows in Microsoft Fabric.

For restricted Fabric environments, the recommended operating model is:

**Dev workspace**  
build, test, experiment  
↓  
**Fabric Deployment Pipeline**  
promote approved notebook item  
↓  
**Production workspace**  
run approved `03_pc` notebooks  
↓  
**FabricOps release registry**  
store audit, version, and rollback evidence

> FabricOps treats Deployment Pipeline as the promotion mechanism, not the full source control system. Production `03_pc` notebooks are promoted from Dev to Production through Fabric Deployment Pipeline, configured through `00_env_config`, and recorded in a FabricOps release registry. Notebook Version History can support diff and restore, while FabricOps keeps frozen release snapshots and metadata in the lakehouse for audit and rollback.

## Recommended operating model: two environments

Keep the operating model simple for restricted environments. Fabric supports more pipeline stages, but FabricOps recommends Dev and Production for this workflow.

| Environment | Purpose |
| --- | --- |
| Dev | Build, test, profile, explore, and prepare notebooks |
| Production | Run approved recurring notebooks |

Dev does not require strict versioning.
Production does.

Core rule:

- Dev is working space.
- Production is controlled runtime space.

## Keep names aligned across environments

Use the same logical structure in both environments.

**Dev workspace**

- Source lakehouse
- Unified lakehouse
- Product lakehouse

**Production workspace**

- Source lakehouse
- Unified lakehouse
- Product lakehouse

Use the same table names across environments where possible.

This allows the same `03_pc` notebook logic to move from dev to production without rewriting business logic.

## Use `00_env_config` as the environment switch

Production notebooks should not hardcode dev or production paths.

Instead, notebooks should load:

```python
%run 00_env_config
```

Then resolve environment-specific paths through config, for example:

```python
ENV = "DE"
lh_in = get_path(ENV, "Source")
lh_out = get_path(ENV, "Unified")
```

This keeps notebook logic stable while config controls whether runtime points to dev or production lakehouses.

## Use Deployment Pipeline to promote notebook items

Deployment Pipeline is the controlled promotion mechanism:

Dev `03_pc` notebook  
↓  
Deploy  
↓  
Production `03_pc` notebook

Deployment promotes the notebook item. It does not replace production config, release records, or rollback evidence.

### Deployment Pipeline limitations

Deployment Pipeline promotes supported Fabric items and dependencies, but it is not source control. It does not version lakehouse table/file data, and it does not replace release records, contract records, DQ versions, classification versions, or smoke-test evidence.


## Version production `03_pc` notebooks

### Production notebook safety warning

Fabric notebook frozen cell status is not preserved during deployment. Production `03_pc` notebooks must not depend on frozen cells for runtime safety. Remove, comment out, or guard exploration/diagnostic/one-time checks behind an explicit config flag before promotion.

Strong versioning is required for production runtime notebooks, especially `03_pc_*` notebooks that run on schedule and create production data.

Each production promotion should create a release record that includes:

- `release_id`
- `notebook_name`
- `notebook_version`
- `deployed_by`
- `deployed_at`
- `source_workspace`
- `target_workspace`
- `contract_version`
- `dq_rule_version`
- `classification_version`
- `validation_status`
- `release_notes`

## Store release snapshots in the lakehouse

Even when Deployment Pipeline and Notebook Version History are available, FabricOps should keep its own release evidence.

Recommended structure:

```text
Files/
  fabricops_repository/
    notebooks/
      03_pc_student_events_to_curated/
        v001/
          notebook.ipynb
          manifest.json
          release_notes.md
        v002/
          notebook.ipynb
          manifest.json
          release_notes.md
```

This becomes the controlled manual repository for restricted environments.
Release snapshots should include:

- exported notebook `.ipynb`
- `manifest.json` with `release_id`, `notebook_name`, `source_workspace`, `target_workspace`, `deployed_at`, `deployed_by`, `contract_version`, `dq_rule_version`, `classification_version`
- `release_notes.md`
- smoke-test result or `validation_status`


## Audit comes from three sources

| Source | What it gives you |
| --- | --- |
| Deployment Pipeline history | Who deployed, when, which stage, and success/failure status |
| Notebook Version History | Notebook checkpoints, deployed versions, restore, and diff |
| FabricOps release registry | Business release evidence, contract version, DQ version, and governance version |

Fabric gives operational history. FabricOps stores governed release evidence.

## Rollback flow

Rollback should be simple and controlled:

Find previous approved version  
↓  
Restore notebook from Notebook Version History, or import frozen lakehouse copy  
↓  
Update active release registry  
↓  
Run smoke test  
↓  
Resume production schedule

Do not rely only on UI history. The lakehouse release copy is the controlled fallback.

## What not to do

- Do not run production from dev notebooks.
- Do not let production notebooks read dev lakehouses.
- Do not hardcode dev workspace IDs inside production notebooks.
- Do not treat Deployment Pipeline as a full Git replacement.
- Do not version every exploratory notebook.

## Related controls

Deployment does not remove the need to provision and validate target environments. Teams still need explicit setup and validation for:

- target workspaces
- lakehouses / warehouses
- default lakehouse bindings
- Fabric environments / libraries
- permissions
- metadata tables
- contract records
- schedules / orchestration
- deployment rules

Contract records and related metadata are operational controls and should be promoted through governed processes. For contract model and metadata table guidance, see [Metadata and Contracts](metadata-and-contracts/).

Normal `03_pc` notebooks should remain single-environment. When cross-environment operations are required, use explicit admin notebooks (for example `90_admin_promote_contract_dev_to_prod`, `90_admin_compare_contract_dev_prod`, and `90_admin_validate_prod_setup`) to keep changes intentional and auditable.
