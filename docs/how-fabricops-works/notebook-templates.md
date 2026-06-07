# Notebook Templates

FabricOps Starter Kit uses four delivery templates plus one optional support template. The required delivery path is Agreement → Pipeline → Review after environment configuration.

The templates are available in the [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder.

!!! note "Notebook preview"
The notebook templates are optimized for Microsoft Fabric execution. GitHub may not always render `.ipynb` files reliably.

```
Open the template in Microsoft Fabric, VS Code, or Jupyter if the GitHub preview fails.

The `%run 00_env_config` bootstrap cell is intentionally active so the templates remain plug-and-play. Do not edit it unless you are intentionally customizing the framework setup.
```

## Template overview

| Notebook | Main owner | Purpose |
| -------- | ---------- | ------- |
| `00_env_config` | Engineer | Defines environment paths and creates or validates all active metadata tables. |
| `01_agreement` | Governance | Defines what should be built, who owns it, what rules apply, and what readiness means. |
| `02_pipeline` | Engineer | Builds, transforms, validates, and publishes the data product while recording profile evidence, lineage, and run summaries. |
| `03_review` | Governance | Checks evidence, metadata, ownership, rules, readiness, and handover quality. |
| `99_explore` | Analyst or data scientist | Optional support for discovery, profiling, troubleshooting, investigation, and ad hoc analysis. |

## Role-based notebook flow

![Role-based notebook workflow from environment configuration through governance review](../assets/fabricops-role-workflow.png){ .full-width }

| Step | Owner | Notebook or action | Result |
| ---- | ----- | ------------------ | ------ |
| 0 | Engineer | Configure and run `00_env_config`. | Environment paths and all active metadata table schemas are ready. |
| 1 | Governance | Use `01_agreement`. | Steward, agreement, rules, readiness, ownership, and agreement-evidence records are stored. |
| 2 | Engineer | Build and run `02_pipeline`. | The data product is built, transformed, validated, published, and recorded with profile, lineage, and run evidence. |
| 3 | Governance | Use `03_review`. | Evidence, metadata, ownership, rules, readiness, handover quality, column context, DQ expectations, sensitivity labels, and PII classifications are reviewed. |
| Support | Analyst, data scientist, or engineer | Use `99_explore` only when helpful. | Optional discovery, profiling, troubleshooting, investigation, and ad hoc analysis support the delivery path without becoming a required gate. |
| Handover | Engineer | Store the approved production notebook for handover. | The production implementation and supporting metadata remain available for support and future enhancement. |

Reviewed DQ expectations and classifications from `03_review` are not automatically enforced in v1.0.0. Production enforcement comes from checks implemented in `02_pipeline`.

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

### `01_agreement`

Run this notebook in the Governance workspace.

It provides the widget workflow for maintaining:

* data stewards;
* versioned data agreements;
* supporting agreement evidence.

FabricOps uses separate Fabric-friendly widget cells:

* `widget_render_data_steward(...)` for steward maintenance.
* `widget_render_data_agreement(...)` for agreement maintenance.
* `widget_render_agreement_evidence(...)` for optional evidence file-reference metadata.

All cells write to the same metadata tables.

Creating an agreement generates a stable `agreement_id` and its first version. Updating an agreement appends a new version instead of overwriting its previous record.

Organisation-specific intake fields should be configured in `00_env_config` and stored in `custom_fields_json`.

Governance classification, business context, and DQ-rule review do not belong in `01_agreement`.

### `02_pipeline`

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

`02_pipeline` writes one catalogue row per profiled column per successful source or target profile.

The catalogue combines:

* stable table and column identity;
* table context;
* column profiling metrics;
* pipeline and profile-run context;
* baseline and drift-monitoring evidence.

`03_review` later uses this catalogue to select a table for governance review.

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

The base `02_pipeline` enforces only the checks implemented in the notebook. Reviewed DQ expectations from `03_review` are not automatically enforced in v1.0.0.

### `03_review`

Run this notebook in the Governance workspace after `02_pipeline` has written catalogue evidence.

`03_review` is a governance review workflow for catalogue evidence. It does not enforce production rules or require a data agreement for every reviewed table.

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

For v1.0.0, `03_review` authors and stores reviewed governance metadata. It does not enforce production rules.

The base `02_pipeline` does not automatically read these metadata tables for enforcement. Future versions may add optional metadata-driven DQ rule execution, rule promotion workflows, and richer operational monitoring.

### `99_explore`

Run this notebook only when optional support is useful. Analysts, data scientists, and engineers use it for less-structured discovery, profiling, troubleshooting, investigation, and ad hoc analysis of source or unified data.

The notebook can:

* read supported source tables or files;
* profile the selected data;
* perform focused exploratory checks;
* link the notebook to one or more data agreements.

`METADATA_NOTEBOOK_REGISTRY` stores the relationships between the notebook and its selected agreements.

Each notebook-agreement relationship has its own registry row. Removing an agreement from a notebook marks that relationship inactive or superseded while preserving its history.

The base `99_explore` template does not own catalogue writes or governance approvals, and it is not required before `01_agreement`, `02_pipeline`, or `03_review`.


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

| Notebook or process | Reads | Writes |
| ------------------- | ----- | ------ |
| `00_env_config` | Existing metadata schemas | Creates and validates all active metadata tables |
| `01_agreement` | Existing stewards and agreements | Steward, agreement, and evidence metadata |
| `02_pipeline` | Agreement metadata, previous profiles, and source data | Notebook registry, catalogue, lineage, and business outputs |
| `03_review` | Catalogue and existing governance metadata | Column context, DQ expectations, and classifications |
| `99_explore` | Agreement metadata and source data | Optional notebook-to-agreement registry relationships |
| Access capture process | Catalogue and platform access assignments | Data access metadata |

## Next step

Continue to [Metadata Tables](metadata-tables.md) for the product-truth data model, logical keys, relationships, and active metadata schemas.
