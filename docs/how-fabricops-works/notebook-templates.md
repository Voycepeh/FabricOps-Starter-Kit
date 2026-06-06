# Notebook Templates

FabricOps Starter Kit uses five notebook templates. Each template has one clear responsibility in the workflow.

The templates are available in the [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder.

!!! note "Notebook preview"
The notebook templates are optimized for Microsoft Fabric execution. GitHub may not always render `.ipynb` files reliably.

```
Open the template in Microsoft Fabric, VS Code, or Jupyter if the GitHub preview fails.

The `%run 00_env_config` bootstrap cell is intentionally active so the templates remain plug-and-play. Do not edit it unless you are intentionally customizing the framework setup.
```

## Template overview

| Notebook        | Main owner                | Purpose                                                                                                   |
| --------------- | ------------------------- | --------------------------------------------------------------------------------------------------------- |
| `00_env_config` | Engineer                  | Defines environment paths and creates or validates all active metadata tables.                            |
| `01_da`         | Governance                | Maintains data stewards, data agreements, and supporting evidence.                                        |
| `02_ex`         | Analyst or data scientist | Explores and profiles source data within one or more selected data agreements.                            |
| `03_pc`         | Engineer                  | Runs production with notebook-scoped guardrails, output writes, profile evidence, lineage, and run summaries. |
| `04_gov`        | Governance                | Reviews profile evidence and commits column context, DQ expectations, and classifications.                |

## Role-based notebook flow

![Role-based notebook workflow from environment configuration through governance review](../assets/fabricops-role-workflow.png){ .full-width }

| Step | Owner                     | Notebook or action                                   | Result                                                                                                             |
| ---- | ------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 0    | Engineer                  | Configure and run `00_env_config`.                   | Environment paths and all active metadata table schemas are ready.                                                 |
| 1    | Governance                | Use `01_da`.                                         | Steward, agreement, and agreement-evidence records are stored.                                                     |
| 2    | Analyst or data scientist | Use `02_ex` in Engineering Dev.                      | Data is explored and profiled, and the notebook is linked to one or more data agreements.                          |
| 3    | Engineer                  | Build and run `03_pc`.                               | Production guardrails run, outputs are written after required checks pass, and profile, lineage, and run evidence are recorded. |
| 4    | Governance                | Use `04_gov`.                                        | Column context, DQ expectations, sensitivity labels, and PII classifications are reviewed and committed as metadata. |
| 5    | Engineer                  | Store the approved production notebook for handover. | The production implementation and supporting metadata remain available for support and future enhancement.         |

Reviewed DQ expectations and classifications from `04_gov` are not automatically enforced in v1.0.0. Production enforcement comes from checks implemented in `03_pc`.

## What each template owns

### `00_env_config`

Configure this notebook first in each environment.

It defines the environment-specific workspace, lakehouse, warehouse, and metadata paths used by all other notebooks.

On its first run, `00_env_config` creates every active metadata table with its expected schema. Later runs validate the existing schemas before any workflow notebook reads or writes metadata.

The active metadata setup includes:

* `METADATA_DATA_STEWARD`
* `METADATA_DATA_AGREEMENT`
* `METADATA_DATA_AGREEMENT_EVIDENCE`
* `METADATA_NOTEBOOK_REGISTRY`
* `METADATA_DATA_LINEAGE_TABLE`
* `METADATA_DATA_CATALOGUE`
* `METADATA_DATA_ACCESS`
* `METADATA_COLUMN_CONTEXT`
* `METADATA_DQ_RULES`
* `METADATA_COLUMN_CLASSIFICATION`

Downstream notebooks append or read records. They do not own physical metadata table creation.

### `01_da`

Run this notebook in the Governance workspace.

It provides the widget workflow for maintaining:

* data stewards;
* versioned data agreements;
* supporting agreement evidence.

FabricOps supports two layouts:

* **Option A:** a compact combined application using `widget_render_agreement_intake_app(...)`;
* **Option B:** separate widgets using `widget_render_data_steward(...)`, `widget_render_data_agreement(...)`, and `widget_render_agreement_evidence(...)`.

Both layouts write to the same metadata tables.

Creating an agreement generates a stable `agreement_id` and its first version. Updating an agreement appends a new version instead of overwriting its previous record.

Organisation-specific intake fields should be configured in `00_env_config` and stored in `custom_fields_json`.

Governance classification, business context, and DQ-rule review do not belong in `01_da`.

### `02_ex`

Run this notebook in Engineering Dev.

Analysts and data scientists use it for less-structured exploration of source or unified data.

The notebook can:

* read supported source tables or files;
* profile the selected data;
* perform focused exploratory checks;
* link the notebook to one or more data agreements.

`METADATA_NOTEBOOK_REGISTRY` stores the relationships between the notebook and its selected agreements.

Each notebook-agreement relationship has its own registry row. Removing an agreement from a notebook marks that relationship inactive or superseded while preserving its history.

The base `02_ex` template does not own catalogue writes or governance approvals.

### `03_pc`

Run this notebook in Engineering Dev and Engineering Prod.

Data engineers use it to implement repeatable source-to-target pipelines.

The base template:

1. loads `00_env_config`;
2. links the notebook to one or more data agreements;
3. reads the configured source;
4. validates the source schema;
5. monitors source data changes;
6. applies deterministic transformations;
7. validates the proposed target schema;
8. monitors proposed target changes;
9. writes the target;
10. writes source and target profiling evidence to `METADATA_DATA_CATALOGUE`;
11. records table-level lineage in `METADATA_DATA_LINEAGE_TABLE`.

Schema and data-drift guardrails remain inside the pipeline notebook.

Schema presets include:

* `strict`
* `allow_new_columns`
* `monitor_only`

Data-change presets include:

* `changing_data`
* `fixed_data`
* `monitor_changing_data`
* `monitor_fixed_data`

The pipeline notebook is the executable source of truth for its expected schema, drift settings, threshold overrides, and blocking behaviour.

Separate data contracts are not part of the v1.0.0 operating model; the notebook owns these production settings.

#### Catalogue ownership

`03_pc` writes one catalogue row per profiled column per successful source or target profile.

The catalogue combines:

* stable table and column identity;
* table context;
* column profiling metrics;
* pipeline and profile-run context;
* baseline and drift-monitoring evidence.

`04_gov` later uses this catalogue to select a table for governance review.

#### Lineage ownership

Table-level lineage belongs to the notebook, not to an individual data-agreement registration.

A notebook may be linked to several agreements, but it has one current table-level lineage definition.

The lineage record stores its source and target tables as JSON arrays containing stable catalogue table keys.

This avoids duplicating the same lineage for every agreement linked to the notebook.

#### Runtime audit columns

Output rows include runtime audit fields identifying:

* the pipeline run;
* pipeline name;
* environment;
* source table;
* load timestamp;
* producing notebook;
* user or service that executed the pipeline.

Hash and bucket columns remain optional implementation choices and are not part of the standard pipeline path.

The base `03_pc` enforces only the checks implemented in the notebook. Reviewed DQ expectations from `04_gov` are not automatically enforced in v1.0.0.

### `04_gov`

Run this notebook in the Governance workspace after `03_pc` has written catalogue evidence.

`04_gov` is a governance review workflow for catalogue evidence. It does not enforce production rules or require a data agreement for every reviewed table.

The workflow is:

1. load `00_env_config`;
2. select a table from `METADATA_DATA_CATALOGUE`;
3. load the latest successful column profile for that table;
4. review and commit business context;
5. review and commit DQ expectations;
6. review and commit sensitivity and PII classifications.

#### Business context

Governance users review each column and enter its business meaning.

Optional AI assistance may use `ai.generate_response(...)` to suggest a description from available column names, datatypes, and profiling evidence.

AI output remains advisory. A human must review, edit, and explicitly commit the final value.

Approved context is stored in:

```text
METADATA_COLUMN_CONTEXT
```

#### Data-quality rules

Governance users can review column-level or table-level DQ expectations such as:

* not-null checks;
* uniqueness;
* accepted values;
* numeric ranges;
* regular expressions;
* datatype requirements;
* referential-integrity checks;
* custom expressions.

AI may suggest expectations, but it cannot approve or save them automatically.

Reviewed expectations are stored in:

```text
METADATA_DQ_RULES
```

#### Column classification

Governance users review:

* confidentiality level;
* sensitivity;
* personal-data classification;
* direct or indirect PII status;
* masking or handling requirements;
* reviewer notes.

AI may suggest classifications, but a human must commit the final decision.

Approved classifications are stored in:

```text
METADATA_COLUMN_CLASSIFICATION
```

#### Enforcement boundary

For v1.0.0, `04_gov` authors and stores reviewed governance metadata. It does not enforce production rules.

The base `03_pc` does not automatically read these metadata tables for enforcement. Future versions may add optional metadata-driven DQ rule execution, rule promotion workflows, and richer operational monitoring.

### Data access capture

`METADATA_DATA_ACCESS` is part of the active product metadata model but is not owned by a standard numbered notebook template.

It stores table-level access assignments captured from an access-export process, administrator workflow, or future access-review notebook.

Each access row links a user or group principal to a catalogue table and records:

* access level;
* granted date;
* expiry date;
* active status.

One catalogue table can have many access assignments.

## Notebook and metadata ownership

| Notebook or process    | Reads                                                  | Writes                                                      |
| ---------------------- | ------------------------------------------------------ | ----------------------------------------------------------- |
| `00_env_config`        | Existing metadata schemas                              | Creates and validates all active metadata tables            |
| `01_da`                | Existing stewards and agreements                       | Steward, agreement, and evidence metadata                   |
| `02_ex`                | Agreement metadata and source data                     | Notebook-to-agreement registry relationships                |
| `03_pc`                | Agreement metadata, previous profiles, and source data | Notebook registry, catalogue, lineage, and business outputs |
| `04_gov`               | Catalogue and existing governance metadata             | Column context, DQ expectations, and classifications         |
| Access capture process | Catalogue and platform access assignments              | Data access metadata                                        |

## Next step

Continue to [Metadata Tables](metadata-tables.md) for the product-truth data model, logical keys, relationships, and active metadata schemas.
