<div class="fabricops-product-page" markdown="1">

# Governance

**Define what trustworthy data means, record the decision in a Data Contract, validate it against the real pipeline, and control where that exact version can be used.**

<div class="fabricops-status-row">
  <span class="fabricops-release-status fabricops-release-status--live">Stewards and Agreements: Live</span>
  <span class="fabricops-release-status fabricops-release-status--preview">Contract authoring and activation: Preview</span>
  <span class="fabricops-release-status fabricops-release-status--preview">Governed execution: gated</span>
</div>

![Governance lifecycle from accountability to approved deployment](assets/governance-lifecycle.svg){ .fabricops-section-evidence }

## What is a Data Contract?

![Anatomy of a frozen Data Contract](assets/data-contract-anatomy.svg){ .fabricops-section-evidence }

A FabricOps Data Contract is the versioned definition for one governed `table_id`. It combines the observed table and column structure with the decisions Governance owns:

- business descriptions and information classification;
- the expected schema and required columns;
- the approved processing strategy;
- Grain, Freshness, Source Drift, Data Quality and Sensitive Data Guardrails.

Saving keeps a draft editable. **Freezing creates an immutable version.** Engineering can select that exact frozen payload in Dry Run and validate it against real reads, transformations and prepared writes. Later profile observations never silently rewrite the frozen contract.

??? info "Under the Hood — contract identity and immutable payload"

    [`widget_data_contract()`](api/reference/widget_data_contract.md) assembles `contract_payload_json` from the selected table observation, authored Enrichment, Processing and Guardrails. Internal [`freeze_contract()`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_contract/shared.py#L1447) validates the saved payload and changes the version to an immutable frozen candidate.

    [`METADATA_DATA_CONTRACT`](reference/metadata/metadata_data_contract.md) stores the `contract_id`, `contract_version`, globally stable `table_id`, authoring provenance and exact JSON payload. Freezing does not deploy a notebook, grant access, activate a pipeline or prove that deployed code matches reviewed code.

## Is it one contract per workspace, pipeline or table?

**The version history belongs to the table, not to a workspace or notebook.**

| Scope | What FabricOps does |
| --- | --- |
| Table | One global contract history belongs to one stable `table_id`. |
| Workspace | Each workspace can independently select or activate an exact frozen version for that table. Development and Production can therefore reference different versions during a controlled change. |
| Pipeline | A pipeline uses the exact contracts for every participating source and target. A contract is not copied into the pipeline. |
| Authoring evidence | The selected workspace supplies the observed schema, profile and processing evidence used to create the draft. It does not own the global version history. |

An independently activated table contract protects that Table ID and physical destination from Ungoverned publication in the selected workspace. Pipeline approval is a separate decision because it also covers participating tables, readers and writers, destinations, Processing and an effective Data Agreement.

??? info "Under the Hood — workspace activation"

    [`widget_activate_data_contract()`](api/reference/widget_activate_data_contract.md) reviews and activates one exact frozen `contract_id` and `contract_version` for a `table_id` in its physical `workspace_id`. The reviewer also selects the applicable exact Data Agreement. The append-only decision is stored in [`METADATA_DATA_CONTRACT_ACTIVATION`](reference/metadata/metadata_data_contract_activation.md), separately from the global contract definition.

    This action does not activate a pipeline or enable Governed execution. It creates an immutable activation record, prevents casual Ungoverned writes to that protected identity, and leaves historical Pipeline Runs unchanged.

## How do I author, freeze and activate one? { #data-contract-lifecycle }

1. **Record accountability.** Use [`widget_render_data_steward()`](api/reference/widget_render_data_steward.md), then create the versioned Data Agreement with [`widget_render_data_agreement()`](api/reference/widget_render_data_agreement.md) to explain ownership, purpose and approved use.
2. **Collect real Engineering evidence.** Run the pipeline in Ungoverned mode so the Catalogue, profiles, processing definition and pipeline participation describe the real table.
3. **Author the draft.** In [`widget_data_contract()`](api/reference/widget_data_contract.md), deliberately select the table and the workspace whose evidence you want to review. Configure descriptions, Processing and Guardrails.
4. **Save and freeze.** Save until the definition is ready, then freeze the exact immutable candidate.
5. **Validate with Engineering.** Engineering selects the frozen version in Dry Run. FabricOps exercises the real Read → Transform → Write preparation without publishing target rows or committing operational state.
6. **Review the evidence.** Confirm that every participating table used the intended version and that Schema, Grain, Freshness, Source Drift, Data Quality and Sensitive Data outcomes allow continuation.
7. **Activate the physical table contracts.** Use [`widget_activate_data_contract()`](api/reference/widget_activate_data_contract.md) for every source and target in its physical workspace, selecting the applicable Agreement each time.
8. **Approve the saved pipeline submission.** Engineering finalizes a saved Dry Run submission. Governance uses [`widget_activate_pipeline()`](api/reference/widget_activate_pipeline.md) to inspect that exact notebook, its recorded checks and resolved bindings, then approve, reject or revoke it. The decision is stored in [`METADATA_PIPELINE_ACTIVATION`](reference/metadata/metadata_pipeline_activation.md).
9. **Let Engineering deploy the approval.** Engineering uses the controls beneath [`finalize_pipeline()`](api/reference/finalize_pipeline.md) to deploy the exact approved snapshot as a separate Governed notebook, then explicitly rebinds the Fabric schedule. Governance approval alone never creates or deploys a notebook.

!!! warning "Current Governed execution boundary"
    FabricOps can activate exact Contracts, record an independent pipeline decision, and deploy the exact approved notebook snapshot. Governed pipeline admission and publication still fail closed pending the [signed-in Fabric acceptance checklist](maintainer/governed-pipeline-fabric-acceptance.md). Saved-code and hash checks cannot prove the identity of code already executing, and imported dependencies are not frozen.

## What can I configure inside the contract?

| Contract area | Governance decision | Runtime effect |
| --- | --- | --- |
| Table and columns | Stable table identity, observed columns, data types and required/optional presence | Schema checks compare the real DataFrame with the frozen definition. |
| Enrichment | Table and column descriptions plus governed classification | Supplies business context to reviewers and downstream consumers. |
| Processing | Overwrite, Append All, Append New Only, SCD1 or SCD2, including required watermark and key parameters | The proposed Engineering operation must agree with the selected contract. |
| Guardrails | Schema, Grain, Freshness, Source Drift, Data Quality and Sensitive Data | Evaluates the real Read or prepared Write and returns a continuation decision. |

Engineering owns Standard, Grain discovery and Frequency execution through `setup_pipeline()`. See [Shared table profiling](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#shared-table-profiling) for defaults and scope. Data Contracts can be authored, frozen and activated without saved profiles; missing measurements display **Not yet profiled**. Profiling controls never enable, disable or weaken Guardrails.

??? info "Under the Hood — payload structure and profiling state"

    New frozen payloads contain `table`, `enrichment` and `guardrails`. Processing lives under `table.processing`. Historical frozen records retain their original bytes; any historical `profiling` object has no execution authority. Pipeline profiling settings are reviewed and retained in the approved notebook package. Bounded measurements are labelled as sampled and do not establish full-table uniqueness or counts.

    [`orchestrate_read()`](api/reference/orchestrate_read.md) and [`orchestrate_write()`](api/reference/orchestrate_write.md) call the profiling scheduler. Standard results are stored in [`METADATA_DATA_PROFILED`](reference/metadata/metadata_data_profiled.md), Frequency results in [`METADATA_DATA_PROFILED_FREQUENCY`](reference/metadata/metadata_data_profiled_frequency.md), and independent activity events in [`METADATA_PIPELINE_RUN`](reference/metadata/metadata_pipeline_run.md) record when each table, workspace, physical destination, activity and trigger completed. Concurrent runs can both find profiling due, so duplicate snapshots are possible; only a successfully journaled completion advances the schedule.

## How do Guardrails protect pipeline data?

FabricOps applies the checks at the boundary where the decision matters:

| Boundary | Applicable protection |
| --- | --- |
| Read | Freshness, Schema, Grain and Data Quality against the source DataFrame |
| Before Write | Target Schema, Sensitive Data treatment, Source Drift for contributing sources, target Grain and Data Quality |
| After successful publication | Accepted checkpoints, Source Drift baselines, profiles, lineage and run evidence |

Warn/Block is authored policy. [`METADATA_GUARDRAIL_RESULTS`](reference/metadata/metadata_guardrail_results.md) records aggregate outcomes and whether execution can continue; full failing business rows are not automatically copied into governance storage.

### Optional AI authoring and consumption

| Party | Responsibility |
| --- | --- |
| Human Governance | Makes and approves governance decisions |
| Fabric AI Functions | Suggests descriptions, assessments and Data Quality rules |
| FabricOps | Validates suggestions, stages changes and deterministically enforces approved Guardrails |

AI is optional. **Open Data Contract** opens a manual-first editor without AI requests
or AI Functions initialization. Sidebar navigation, column changes, Save, Discard,
Review and Freeze also make no AI requests. Use contextual **Generate**, **Suggest**
or **Re-run** to request one suggestion explicitly; each requested inference consumes
Fabric AI capacity. Successful suggestions remain available during navigation until
reviewed and accepted.
Description, Grain and Row Key, Sensitive Data, Data Quality and all deterministic lifecycle
and Guardrail controls remain available. `GOVERNANCE_CONFIG.ai_enrichment.enabled=False`
disables AI actions. AI Settings and usage reporting remain accessible from the sidebar. See the
[configuration exercise](guided-demo/03-author-and-freeze-data-contract.md#choose-the-ai-settings-or-author-manually).

??? info "Built-in models, reasoning, billing and usage monitoring"

    FabricOps supports `gpt-5-mini` (default) and `gpt-5.1` through the built-in
    Microsoft Fabric AI Functions endpoint on Runtime 2.0. Availability depends on
    Microsoft's supported regions, tenant configuration and eligible paid capacity.
    The selector and editor show the effective configuration before opt-in.

    Microsoft's [PySpark configuration](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/pyspark/configuration)
    documents reasoning `None`, `minimal`, `low`, `medium`, `high` and verbosity
    `None`, `low`, `medium`, `high`. FabricOps defaults to low reasoning and
    provider-default verbosity. Widget arguments override configured values; omitted
    arguments use configuration, then package defaults. Stronger models and higher
    reasoning can increase consumption and latency; service support remains authoritative.

    Built-in model calls consume Fabric capacity under the **Copilot and AI** meter,
    reported as the **AI Functions** operation. **Spark execution is billed separately**
    through the Spark meter. The separate Copilot capacity allocation feature should
    not be confused with AI Functions billing. Azure AI Foundry is a future advanced
    integration with separate Azure billing; this widget does not support custom
    endpoints, API keys or Foundry credentials.

    Microsoft documents `result.ai.stats` for measured row and token statistics:
    successful, exception, unevaluated and harmful counts; input, output, cached and
    reasoning tokens; and model. FabricOps captures these per authoring request where
    available and shows them in the editor's usage disclosure. The one-row AI result
    is persisted while reading response and stats to avoid re-running inference for telemetry.
    Missing statistics are marked unavailable, never replaced with fabricated counts.

    The documented PySpark statistics do not expose measured per-request CU consumption.
    Token counts are displayed under their own names, without conversion to CU or pricing
    estimates. For exact consumption, open the [Fabric Capacity Metrics app](https://learn.microsoft.com/en-us/fabric/enterprise/metrics-app),
    filter by capacity, workspace and time, and inspect **AI Functions** separately from Spark.
    See [Microsoft's AI Functions billing guidance](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/billing)
    for current rates; no pricing figures are pinned here.

    Sources checked on **5 November 2026**: Microsoft's [overview](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview),
    [PySpark generate_response](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/pyspark/generate-response),
    [Runtime 2.0 setup](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/runtime-2-0-workarounds),
    configuration and billing pages. The MicrosoftDocs source was inspected; local mocked
    tests do not establish actual Fabric service compatibility.

### Sensitive data decisions { #sensitive-data-discovery-classification-and-treatment }

![Sensitive Data governance from classification to deterministic treatment](assets/sensitive-data-governance.svg){ .fabricops-section-evidence }

Governance can classify a column as Direct PII, Indirect PII or Not PII, choose **Mask**, **Bucket**, **Tokenize** or **Remove**, and record the post-treatment information classification. AI can suggest from governed schema and bounded profile evidence; a person reviews the decision. Runtime treatment is deterministic and does not call AI.

??? info "Under the Hood — sensitive-data authoring and enforcement"

    The AI authoring path sends a compact single-row `fabricops_prompt` DataFrame to Fabric AI Functions with [`ai.generate_response()`](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/pyspark/generate-response). It does not send the full business table. Returned structured JSON is checked against supported values before it can be staged.

    The approved rule is stored in [`METADATA_DATA_CONTRACT`](reference/metadata/metadata_data_contract.md). During Write orchestration, internal [`check_sensitive_data()`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_sensitive_data.py#L20) prepares the DataFrame before `_row_hash` calculation and publication. Treatment failures always block. Token support mappings remain caller-owned unless a restricted mapping store is configured.

    Use the [Sensitive Data Treatments reference](reference/sensitive-data-treatments.md) for exact parameters.

### Business rules and Data Quality

![Business rules become approved deterministic Data Quality checks](assets/business-rules-data-quality.svg){ .fabricops-section-evidence }

Governance can author supported Data Quality rules directly or ask AI to translate a business requirement into explicit proposals. A person reviews every proposal. Approved rules run deterministically through internal [`check_dq()`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_dq.py#L13); AI is not involved during pipeline execution.

??? info "Under the Hood — rule grammar and results"

    AI receives the requirement, governed schema, optional profile evidence, existing rules and the supported rule grammar. Structured rules are preferred; constrained Custom Expression is used only when the requirement cannot be represented faithfully. Returned rule types, columns, parameters and expression grammar are validated before staging.

    The orchestrator can return `_dq_failed_rules`, `_dq_check_status` and bounded or full `failed_values` diagnostics to Engineering. Persisted Guardrail Results keep aggregate status, continuation, reason and result JSON rather than duplicating all violating rows.

    Use the [Data Quality Rules reference](reference/dq-rules/index.md) for supported rule types and parameters.

## Which Governance tools do I use?

| Tool | What you decide | What it records |
| --- | --- | --- |
| [`widget_render_data_steward()`](api/reference/widget_render_data_steward.md) | Accountable people and steward responsibilities | Versioned [`METADATA_DATA_STEWARD`](reference/metadata/metadata_data_steward.md) records |
| [`widget_render_data_agreement()`](api/reference/widget_render_data_agreement.md) | Provider/recipient purpose, approved use and Agreement version | Versioned [`METADATA_DATA_AGREEMENT`](reference/metadata/metadata_data_agreement.md) records |
| [`widget_data_contract()`](api/reference/widget_data_contract.md) | Table meaning, Processing and Guardrails | Editable drafts and immutable frozen [`METADATA_DATA_CONTRACT`](reference/metadata/metadata_data_contract.md) versions |
| [`widget_activate_data_contract()`](api/reference/widget_activate_data_contract.md) | Select one frozen Contract and applicable Agreement for one physical workspace/table | Reviewed activation history in [`METADATA_DATA_CONTRACT_ACTIVATION`](reference/metadata/metadata_data_contract_activation.md) |
| [`widget_activate_pipeline()`](api/reference/widget_activate_pipeline.md) | Review an exact saved Engineering submission and approve, reject or revoke it independently | Protected decision history and accepted package in [`METADATA_PIPELINE_ACTIVATION`](reference/metadata/metadata_pipeline_activation.md); approval does not deploy |

## How does this govern Engineering pipelines?

| Engineering mode | Governance effect |
| --- | --- |
| Dry Run | Engineering can select frozen candidates and see real validation results without publication or metadata commits. |
| Ungoverned | The pipeline can publish without contract-dependent checks, but it cannot write a Table ID or physical destination already protected by an activation. |
| Governed | Resolves activated Contracts, an approved submission and the deployed notebook identity. It currently fails closed pending signed-in Fabric acceptance. |

Governance therefore controls the definitions, protected physical destinations and independent approval without pretending that approval deploys code. Processing changes, contract mappings, table roles, destinations, source relationships and transformation settings require fresh validation and approval. Engineering separately deploys the exact accepted snapshot and owns schedule rebinding.

## What can I monitor in Power BI?

The Metadata Lakehouse can feed a Power BI semantic model that answers governance questions such as:

- Which governed tables have a frozen contract, and which exact version is activated in each workspace?
- Who is accountable, and which Data Agreement supports the approved use?
- Which Guardrails passed, warned or blocked, and why?
- Which tables are overdue for Standard, Grain or Frequency profiling?
- Which pipelines read or write a governed table, and what was the latest complete run outcome?
- Where are Source Drift, schema, quality or Sensitive Data failures concentrated over time?

This repository does **not** currently ship a `.pbix`, `.pbit` or Power BI project. The source evidence is available, but a maintained Governance dashboard remains a product/documentation gap rather than a Live advertised capability.

??? info "Under the Hood — reporting sources"

    A report developer can model the exact documented sources:

    | Governance question | Exact source |
    | --- | --- |
    | Accountability and approved use | [`METADATA_DATA_STEWARD`](reference/metadata/metadata_data_steward.md), [`METADATA_DATA_AGREEMENT`](reference/metadata/metadata_data_agreement.md) |
    | Frozen contract coverage and content | [`METADATA_DATA_CONTRACT`](reference/metadata/metadata_data_contract.md) |
    | Active Contract and Agreement selections | [`METADATA_DATA_CONTRACT_ACTIVATION`](reference/metadata/metadata_data_contract_activation.md) |
    | Pipeline decisions and accepted submissions | [`METADATA_PIPELINE_ACTIVATION`](reference/metadata/metadata_pipeline_activation.md) |
    | Deployed pipeline versions and notebook identity | [`METADATA_PIPELINE_REGISTRY`](reference/metadata/metadata_pipeline_registry.md) |
    | Table identity and processing | [`METADATA_DATA_CATALOGUE`](reference/metadata/metadata_data_catalogue.md) |
    | Profiling trends | [`METADATA_DATA_PROFILED`](reference/metadata/metadata_data_profiled.md), [`METADATA_DATA_PROFILED_FREQUENCY`](reference/metadata/metadata_data_profiled_frequency.md) |
    | Pipeline participation and outcomes | [`METADATA_DATA_LINEAGE`](reference/metadata/metadata_data_lineage.md), [`METADATA_PIPELINE_RUN`](reference/metadata/metadata_pipeline_run.md) |
    | Guardrail status and continuation | [`METADATA_GUARDRAIL_RESULTS`](reference/metadata/metadata_guardrail_results.md) |
    | Accepted checkpoints and Source Drift baselines | [`METADATA_PROCESSING_STATE`](reference/metadata/metadata_processing_state.md) |

    A Power BI model should use those stable relationships and timestamps rather than parse widget screenshots.

    The [Metadata Tables reference](reference/metadata.md) exists for the report developer who needs exact fields. Governance users do not need to understand the physical table architecture to author or approve a Data Contract.

</div>
