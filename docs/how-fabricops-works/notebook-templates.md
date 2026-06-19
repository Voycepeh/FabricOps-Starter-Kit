# Template Notebooks

Template Notebooks is the canonical user guide for what each FabricOps notebook contains and what users can configure. Use it when you need notebook-level detail. Use the [Guided Demo](../guided-demo.md) for the run sequence, and use the [API Reference](../reference/index.md) for reusable functions and classes.

## Notebook roles

| Notebook | Primary role | Production workflow step? |
| -------- | ------------ | ------------------------- |
| `00_env_config` | Configure environment, paths, metadata routing, runtime validation, and audit settings. | Yes. Run first. |
| `01_agreement` | Capture business agreement, ownership, purpose, readiness, and supporting evidence. | Yes. Run before pipeline work. |
| `02_pipeline` | Implement engineering data loading, transformation, validation, publishing, lineage, and run evidence. | Yes. Run for delivery. |
| `03_governance` | Review metadata, complete enrichment, approve guardrails, and assess promotion readiness. | Yes. Run for review and lifecycle decisions. |
| `99_explore` | Inspect and troubleshoot metadata or data context. | No. Helper only. |
| `example_pipeline_demo` | Generate deterministic demo source scenarios. | No. Demo helper only. |
| `example_dq_rule_smoke_test` | Validate DQ rule behavior in a smoke-test context. | No. Validation helper only. |

## `00_env_config`

[Source notebook](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb)

**Purpose**

Centralizes environment, workspace, path, metadata routing, runtime validation, and audit settings so every later notebook uses the same configured targets.

**When to use it**

Run it first in every workspace setup, demo, or delivery flow. Revisit it when workspace item names, schemas, metadata targets, validation behavior, or audit values change.

**What the notebook contains**

- Environment selection.
- Workspace, lakehouse, warehouse, and schema settings.
- Metadata lakehouse routing for `METADATA_*` tables.
- Runtime validation defaults.
- Audit and notebook registration settings.
- Metadata table setup and validation cells.

**User-editable configuration**

- Environment name.
- Workspace and Fabric item names.
- Source, unified, metadata, and warehouse route settings.
- Schema names and default table names for the workflow.
- Runtime validation flags and audit values.

**Advanced configuration**

- Environment-specific route dictionaries.
- Metadata table registry behavior.
- Optional warehouse publishing routes.
- Audit fields used to explain notebook ownership and execution context.

**What users should normally not edit**

- Helper imports and setup calls.
- Metadata table names unless intentionally changing the governed metadata model.
- Shared object names expected by downstream notebooks, such as `CONFIG` and `ENV`.

**What it validates**

- Required environment keys and configured paths.
- Metadata routing through the configured metadata lakehouse rather than a default attached lakehouse.
- Availability of metadata table definitions used by later notebooks.

**What it creates or updates**

- A reusable `CONFIG` object.
- The selected `ENV` value.
- Required metadata tables in the configured metadata target.
- Notebook registration or audit context where configured.

**Downstream dependencies**

`01_agreement`, `02_pipeline`, `03_governance`, and `99_explore` depend on the routes and runtime context from this notebook.

## `01_agreement`

[Source notebook](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_agreement.ipynb)

**Purpose**

Captures business agreement, ownership, purpose, readiness, and supporting evidence before engineering execution begins.

**When to use it**

Run it when a new governed delivery needs steward details, agreement scope, business purpose, readiness notes, or evidence that explains why the work is approved to proceed.

**What the notebook contains**

- Steward entry and review cells.
- Agreement details for business context and delivery scope.
- Evidence capture for readiness, approvals, or supporting notes.
- Save cells that write agreement metadata through configured metadata routing.

**User-editable configuration**

- Steward and owner details.
- Agreement name, purpose, scope, status, and business context.
- Evidence labels, notes, and links that are safe to publish.
- Readiness or support notes used by downstream reviewers.

**Advanced configuration**

- Additional evidence rows for larger handover packages.
- Agreement status or lifecycle values when the team has an established review process.

**What users should normally not edit**

- Metadata write helpers.
- Generated identifiers unless the notebook explicitly asks for a stable existing value.
- Metadata table routing inherited from `00_env_config`.

**What it validates**

- Required agreement and steward fields.
- Public-safe evidence values.
- The configured metadata target can receive agreement rows.

**What it creates or updates**

- Steward metadata.
- Data agreement metadata.
- Agreement evidence metadata.

**Downstream dependencies**

`02_pipeline`, `03_governance`, and `99_explore` use the selected agreement context to connect technical evidence to ownership and purpose.

## `02_pipeline`

[Source notebook](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb)

**Purpose**

Provides the engineering implementation notebook for data loading, transformation, validation, publishing, lineage, and run evidence.

**When to use it**

Run it after `00_env_config` and `01_agreement` when source-to-target processing is ready to execute under an approved agreement context.

**What the notebook contains**

- Agreement selection.
- Source reads from configured Fabric routes.
- Visible transformation cells that teams adapt for their delivery.
- Profile, schema, freshness, DQ, and guardrail checks.
- Output writes to configured targets.
- Lineage, pipeline output, and pipeline run summary capture.

**User-editable configuration**

- Source table names and read settings.
- Target table names and write mode.
- Transformation logic.
- Pipeline run labels and operational notes.
- Pipeline-specific validation choices exposed by the template.

**Advanced configuration**

- Multiple source or target table configs.
- DQ enforcement choices tied to approved metadata rules.
- Optional warehouse publication.
- Custom lineage or output registration details when needed for support handover.

**What users should normally not edit**

- Metadata routing inherited from `00_env_config`.
- Guardrail result and lineage write helpers.
- Shared run-context setup unless intentionally changing the pipeline contract.

**What it validates**

- Agreement context is selected.
- Source data can be read.
- Schema, freshness, profile, DQ, and load behavior meet configured or approved expectations.
- Outputs are written to the intended configured targets.

**What it creates or updates**

- Observed table and column profiles in the data catalogue metadata.
- Guardrail runtime results.
- Pipeline output records.
- Lineage records.
- Pipeline run summaries.
- Governed output tables.

**Downstream dependencies**

`03_governance` reviews the observed metadata and proposed guardrail context from pipeline runs. Later `02_pipeline` runs can enforce active rules approved through governance review.

## `03_governance`

[Source notebook](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_governance.ipynb)

**Purpose**

Supports governance and metadata enrichment review: complete business metadata, review DQ checks and other guardrails, record lifecycle decisions, and assess promotion readiness.

**When to use it**

Run it after pipeline evidence exists, or whenever reviewers need to approve, reject, replace, deactivate, or update enrichment and guardrail intent.

**What the notebook contains**

- Review context selection.
- Catalogue and enrichment review widgets.
- Guardrail and DQ rule review widgets.
- Lifecycle decision capture.
- Notes that help reviewers decide whether the workflow is ready to promote.

**User-editable configuration**

- Review notes and decision values.
- Business descriptions, classifications, and stewardship context.
- Guardrail rule fields exposed by the widgets.
- Approval, rejection, replacement, and deactivation choices.

**Advanced configuration**

- Replacement or deactivation workflows for existing rules.
- Promotion-readiness review notes.
- Coordinated enrichment updates across table and column metadata.

**What users should normally not edit**

- Widget helper calls unless changing the review workflow intentionally.
- Append-only metadata write behavior.
- Metadata table routing inherited from `00_env_config`.

**What it validates**

- Reviewed records exist in the configured metadata target.
- Required review fields are complete.
- DQ rules and guardrails are shaped for downstream enforcement.
- Enrichment decisions remain separate from observed catalogue profiles.

**What it creates or updates**

- Enrichment lifecycle records.
- Approved, rejected, replaced, or inactive guardrail intent.
- Review evidence for promotion readiness.

**Downstream dependencies**

Future `02_pipeline` runs use active guardrail intent from governance metadata. Support and review users use the decisions to explain why checks are active.

## `99_explore`

[Source notebook](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb)

**Purpose**

Provides inspection and troubleshooting helpers for users who need to understand data, metadata, or helper behavior without changing governed workflow state.

**When to use it**

Use it before or after the governed flow when you need read-only discovery, scratch profiling, troubleshooting, or support investigation.

**What the notebook contains**

- Agreement and context selection helpers.
- Read-only metadata inspection cells.
- Optional local profiling or scratch checks.
- Troubleshooting notes for support users.

**User-editable configuration**

- The table or agreement context to inspect.
- Scratch analysis cells and temporary display logic.

**Advanced configuration**

- Additional read-only inspection cells for support scenarios.

**What users should normally not edit**

- Do not turn this notebook into a production pipeline.
- Do not write governed metadata from this notebook.
- Do not replace `02_pipeline` transformations or `03_governance` approvals with exploration cells.

**What it validates**

It does not validate production workflow state. It can help users inspect whether metadata or source data looks as expected.

**What it creates or updates**

Nothing required. Outputs are ad hoc notebook displays unless a user intentionally saves separate scratch artifacts outside the governed workflow.

**Downstream dependencies**

No production notebook depends on `99_explore`. Treat it as an inspection and troubleshooting helper, not a workflow step.

## `example_pipeline_demo`

[Source notebook](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_pipeline_demo.ipynb)

**Purpose**

Generates deterministic demo source tables for the guided demo.

**When to use it**

Use it only for demos, training, and local validation of the starter workflow.

**What the notebook contains**

- Demo data generation cells.
- Scenario tables for happy path and guardrail examples.
- Demo-scoped source writes.

**User-editable configuration**

- Demo schema and table prefix when needed.
- Scenario choices exposed by the notebook.

**Advanced configuration**

- Additional demo scenarios for training, if kept public-safe and deterministic.

**What users should normally not edit**

- Do not use it to generate production source data.
- Do not mix real data into demo tables.

**What it validates**

It helps validate that the demo can produce repeatable source inputs for `02_pipeline`.

**What it creates or updates**

Demo source tables in the configured source lakehouse.

**Downstream dependencies**

The guided demo version of `02_pipeline` reads the generated demo source tables.

## `example_dq_rule_smoke_test`

[Source notebook](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_dq_rule_smoke_test.ipynb)

**Purpose**

Demonstrates DQ rule evaluation, warning behavior, and blocking behavior in a smoke-test context.

**When to use it**

Use it when validating helper behavior or learning supported DQ rule outcomes. It is not a production delivery notebook.

**What the notebook contains**

- Smoke-test data setup.
- Example DQ rule definitions.
- DQ enforcement calls and expected outcomes.

**User-editable configuration**

- Smoke-test rule examples and toy input values.

**Advanced configuration**

- Additional smoke-test scenarios for supported DQ rules.

**What users should normally not edit**

- Do not treat smoke-test rules as approved production guardrails.
- Do not write production metadata from this notebook.

**What it validates**

Supported DQ rule behavior in a controlled smoke-test scenario.

**What it creates or updates**

Only smoke-test artifacts expected by the notebook. It does not define production workflow evidence.

**Downstream dependencies**

No production notebook depends on this smoke test. Use [DQ Rules](../reference/dq-rules/index.md) for rule syntax and supported behavior.
