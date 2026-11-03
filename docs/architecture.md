# Architecture

**Governance defines expectations, Engineering produces and validates data, and shared metadata connects both without hiding project-owned transformations.**

![FabricOps operating model showing Governance, Engineering Development, Engineering Production, shared metadata and consumers](assets/fabricops-operating-model-overview.png){ .fabricops-section-evidence }

## Workspace operating model

FabricOps uses Microsoft Fabric workspaces to separate responsibilities and execution scope while keeping the logical Bronze, Silver and Gold roles aligned.

| Area | Responsibility | FabricOps assets |
| --- | --- | --- |
| **Governance Workspace** | Owns stewards, agreements and governed table definitions. | `00_env_config`, `01_governance`, shared Metadata Lakehouse |
| **Engineering Development** | Builds the notebook pipeline, observes real tables, profiles data and tests changes. | `00_env_config`, `02_pipeline`, Development Lakehouses/Warehouses |
| **Engineering Production** | Runs the promoted pipeline against Production stores. | The same logical notebook flow with Production configuration |
| **Project-Specific Consumer** | Uses approved Production data through native Fabric interfaces. | SQL, Spark, notebooks, reports or AI workloads |

`00_env_config` maps logical store names to environment-specific Fabric workspaces and items. The pipeline therefore addresses a configured logical store instead of assuming the notebook's default Lakehouse. Promotion moves the reviewed notebook; it does not make metadata rows or Fabric permissions appear automatically.

??? info "Under the Hood — workspace and store resolution"

    `setup_notebook()` loads the environment configuration and resolves the caller workspace. Internal `resolve_fabric_context()`, `get_store()` and `resolve_store()` select the configured Lakehouse or Warehouse. Lakehouse access resolves OneLake paths; Warehouse access uses the Fabric Spark connector. Unknown workspaces and missing permissions fail rather than falling back to another store.

    Configuration is stored in `00_env_config`, not a metadata table. The shared metadata target is configured independently and every `METADATA_*` read or write routes through it.

    A central configuration notebook can be selected with `config_workspace_id`, but that does not grant cross-workspace access. Native Fabric identity and item permissions still apply.

## Governance ↔ Engineering cycle

![FabricOps Governance and Engineering cycle around shared metadata](assets/fabricops-roles.png){ .fabricops-section-evidence }

**The cycle is joined by the stable `table_id`, not by a workspace name.** A table has one global Data Contract version history; workspace observations, profiles and activation choices remain workspace-specific.

1. Engineering registers physical table identity and records observations, profiles and lineage.
2. Governance uses that evidence to author Enrichment and Guardrails in a versioned Data Contract.
3. Freezing makes the exact `contract_payload_json` immutable for review and testing.
4. Engineering selects the frozen version in Dry Run and evaluates the real Read → Transform → Write path without publication.
5. Activation is a separate, workspace-scoped Preview decision. Production enforcement remains blocked until trusted deployment verification is integrated.
6. Consumers use published data through native Fabric permissions; FabricOps metadata supplies context but does not replace access controls.

??? info "Under the Hood — implementation hand-off"

    | Handoff | Functions | Persisted state |
    | --- | --- | --- |
    | Governance context | [`widget_render_data_steward()`](api/reference/widget_render_data_steward.md), [`widget_render_data_agreement()`](api/reference/widget_render_data_agreement.md) | `METADATA_DATA_STEWARD`, `METADATA_DATA_AGREEMENT` |
    | Observe and profile | [`orchestrate_read()`](api/reference/orchestrate_read.md), [`orchestrate_write()`](api/reference/orchestrate_write.md), [`profile_table()`](api/reference/profile_table.md) | `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, `METADATA_DATA_LINEAGE` |
    | Author and freeze | [`widget_data_contract()`](api/reference/widget_data_contract.md) | `METADATA_DATA_CONTRACT.contract_payload_json` |
    | Preview enforcement | [`setup_pipeline()`](api/reference/setup_pipeline.md), [`orchestrate_read()`](api/reference/orchestrate_read.md), [`orchestrate_write()`](api/reference/orchestrate_write.md) | Dry Run keeps results in memory and commits no target or operational state |
    | Persistent pipeline state | [`finalize_pipeline()`](api/reference/finalize_pipeline.md) and orchestration internals | `METADATA_PIPELINE_RUN`, `METADATA_GUARDRAIL_RESULTS`, `METADATA_PROCESSING_STATE`, `METADATA_PIPELINE_REGISTRY` |

    Guardrail Results store aggregate outcomes and continuation decisions, not full failed business rows. DQ `failed_values` and token `support_mapping` are returned to the caller and are not automatically persisted.

## Shared metadata model

<a class="fabricops-metadata-preview fabricops-metadata-preview--compact" href="reference/metadata/" aria-label="Explore the interactive FabricOps metadata relationship map">
  <span class="fabricops-metadata-preview__body">
    <span class="fabricops-metadata-preview__eyebrow">Interactive relationship map</span>
    <strong class="fabricops-metadata-preview__title">Twelve canonical tables, one traceable model</strong>
    <span class="fabricops-metadata-preview__description">Inspect keys, columns, writer functions and Governance ↔ Engineering relationships.</span>
    <span class="fabricops-metadata-preview__action">Open metadata explorer <span aria-hidden="true">→</span></span>
  </span>
  <span class="fabricops-metadata-preview__image" aria-hidden="true"><img src="../assets/fabricops-metadata-approved.svg" alt="" loading="lazy" decoding="async"></span>
</a>

The configured Metadata Lakehouse holds three Governance-owned tables and nine Engineering-owned tables. The ownership boundary identifies authoritative writers; it does not imply separate physical Lakehouses.

| Group | Canonical tables |
| --- | --- |
| Governance | `METADATA_DATA_STEWARD`, `METADATA_DATA_AGREEMENT`, `METADATA_DATA_CONTRACT` |
| Engineering and operations | `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, `METADATA_DATA_LINEAGE`, `METADATA_DATA_ACCESS`, `METADATA_PIPELINE_REGISTRY`, `METADATA_PIPELINE_RUN`, `METADATA_GUARDRAIL_RESULTS`, `METADATA_PROCESSING_STATE` |

??? info "Under the Hood — identity, timing and transaction boundaries"

    `METADATA_DATA_CATALOGUE` is the canonical table/column and physical-location record. Profile snapshots link back through `table_id` and `column_id`; lineage records a table's pipeline participation. `METADATA_DATA_CONTRACT` stores one exact authored payload per version.

    Pipeline publication and metadata progress are deliberately separate boundaries. FabricOps accepts incremental checkpoints, Source Drift baselines and publication receipts in `METADATA_PROCESSING_STATE` only after it can verify publication. The Pipeline Registry coordinates managed mutations in a Serializable transaction, but multiple target writes are not one cross-target atomic transaction.

    The [Metadata Reference](reference/metadata.md) is generated from `src/fabricops_kit/config/metadata_schemas.py` and writer ownership metadata. Use it instead of inferring columns from a diagram.

## Data Contracts and consumers

A Data Contract is the table-level governed definition: observed table identity and processing, descriptive Enrichment, and executable Guardrails. Governance can freeze an immutable version; Engineering can preview that exact payload against real data. The contract does not deploy notebooks, grant access or prove executable integrity.

Consumers receive access through native Fabric controls. A Warehouse can provide a useful SQL consumption boundary and Query Insights, but query history is not a complete table-level access audit. Direct Lake, Spark and other paths can bypass Warehouse SQL history. FabricOps records observed access metadata where supported; it does not replace Fabric security administration.

<div class="fabricops-cta-row" markdown="1">
[Explore Engineering](engineering.md){ .md-button .md-button--primary }
[Explore Governance](governance.md){ .md-button }
[Run the lifecycle](guided-demo.md){ .md-button }
</div>
