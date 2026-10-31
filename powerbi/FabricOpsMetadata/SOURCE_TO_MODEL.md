# FabricOps metadata source-to-model mapping

This mapping records the authoritative row grain, imported scalar projection, model keys and safe relationships used by the dashboard.

The canonical implementation is [`src/fabricops_kit/config/metadata_schemas.py`](../../src/fabricops_kit/config/metadata_schemas.py). The generated table references under [`docs/reference/metadata/`](../../docs/reference/metadata/) supply the documented grains and application-enforced relationships.

## Canonical tables

| Canonical table | Authoritative row grain | Canonical key | Semantic use |
| --- | --- | --- | --- |
| `METADATA_DATA_STEWARD` | One registered Data Steward. | `steward_id` | Steward inventory and active Steward coverage. |
| `METADATA_DATA_AGREEMENT` | One version of a Data Agreement. | `agreement_id` + `agreement_version` | Agreement versions, domains, accountable parties and expiry. |
| `METADATA_DATA_CONTRACT` | One Draft or Frozen version of a Data Contract for a table. | `contract_id` + `contract_version` | Contract inventory and exact version filtering. `contract_payload_json` remains a scalar JSON string and is imported but hidden from report visuals. |
| `METADATA_DATA_CATALOGUE` | One current table or column observation in one workspace. | `workspace_id` + `table_id` + `column_id` | Current table/column inventory, physical context, writer context and profile freshness. Native STRUCT columns are omitted from the SQL projection. |
| `METADATA_DATA_PROFILED` | One column's statistics from one profiling snapshot. | `profile_id` | Historical null, distinct and distribution statistics. |
| `METADATA_DATA_PROFILED_FREQUENCY` | One recorded value and its frequency for a column in a profiling snapshot. | `frequency_id` | Ranked frequent-value detail. `profile_id` is optional for independently scheduled Frequency Profiling. |
| `METADATA_DATA_LINEAGE` | One table's participation as a source or target in a pipeline operation. | `lineage_id` | Source/target participation only; no transformation graph is inferred. |
| `METADATA_DATA_ACCESS` | One observed permission for a principal or access selector on a table during one scan. | `access_id` | Observed principal, level, state, role and permission-source reporting; not effective access. |
| `METADATA_PIPELINE_REGISTRY` | One central authority row containing native registrations, approvals, selections, ownership and reservations. | `authority_id` | Scalar authority identity and token only. Nested Registry inventory is outside the SQL endpoint reporting boundary. |
| `METADATA_PIPELINE_RUN` | One row per execution with native operations, stages, profiling and safe failures. | `run_id` | Scalar run header, timing, status, mode, activation revision and completion boundary. Native operation detail is not flattened. |
| `METADATA_GUARDRAIL_RESULTS` | One saved Guardrail outcome for an exact Data Contract version. | `guardrail_result_id` | Aggregate outcome, continuation decision, severity and rule context. Failed business rows are not present in this table or report. |
| `METADATA_PROCESSING_STATE` | One source snapshot partition/header, source-to-target progress member, or exact target publication receipt. | `record_id` | Typed observation, checkpoint, baseline and receipt status. |

## Model-only keys

Power BI relationships accept one column per relationship. Power Query creates deterministic composite text keys in memory so the model respects canonical composite grains.

| Model key | Definition | Used by |
| --- | --- | --- |
| `workspace_table_key` | `workspace_id` + `|` + `table_id` | `DimTable`, Catalogue, Profile, Frequency, Lineage, Access and Guardrail Results. |
| `workspace_column_key` | `workspace_id` + `|` + `table_id` + `|` + `column_id` | Catalogue, Profile and Frequency for exact column identity. It is retained for analysis but not used to join Profile to Frequency. |
| `contract_key` | `contract_id` + `|` + `contract_version` | Data Contract to Guardrail Results. |
| `agreement_key` | `agreement_id` + `|` + `agreement_version` | Exact-version Agreement measures. |
| `workspace_pipeline_key` | `workspace_id` + `|` + `pipeline_id` | `DimPipeline`, Pipeline Run and Processing State. |
| `source_workspace_table_key` | `workspace_id` + `|` + `source_table_id` | Active Processing State source relationship. |
| `target_workspace_table_key` | `workspace_id` + `|` + `target_table_id` | Inactive Processing State target relationship for explicit target analysis. |

Null key members become empty segments only inside the semantic model. They do not alter canonical IDs or write back to Delta.

Power Query also derives hidden date-only columns from event timestamps. This prevents timestamp time components from breaking relationships to the daily `Date` dimension.

## Relationships

All relationships filter from a one-side dimension or exact-version authority to the many-side observation table. Cross-filter direction remains single.

| One side | Many side | State | Reason |
| --- | --- | --- | --- |
| `DimWorkspace.workspace_id` | `DimTable.workspace_id` | Active | Workspace filters current Catalogue table identities. |
| `DimWorkspace.workspace_id` | `METADATA_PIPELINE_RUN.workspace_id` | Active | Run headers have their own workspace scope. |
| `DimTable.workspace_table_key` | Catalogue, Profile, Frequency, Lineage, Access and Guardrail `workspace_table_key` | Active | Preserves the workspace-scoped table identity for each independent fact grain. |
| `DimTable.workspace_table_key` | Processing State `source_workspace_table_key` | Active | Default Processing State exploration follows source participation. |
| `DimTable.workspace_table_key` | Processing State `target_workspace_table_key` | Inactive | Avoids two simultaneous paths to the same Processing State row. |
| `DimPipeline.workspace_pipeline_key` | Pipeline Run and Processing State `workspace_pipeline_key` | Active | Filters independent execution and processing facts without joining them together. |
| Data Contract `contract_key` | Guardrail Results `contract_key` | Active | Uses the exact composite Contract version rather than `contract_id` alone. |
| Data Steward `steward_id` | Agreement `provider_steward_id` | Active | Default accountable-provider analysis. |
| Data Steward `steward_id` | Agreement `recipient_steward_id` | Inactive | Prevents ambiguous dual Steward paths; measures can opt in with `USERELATIONSHIP`. |
| `Date.Date` | Primary event date on each fact | Active | Consistent time filtering without fact-to-fact joins. |

The model intentionally does not relate Profile to Frequency on `profile_id`: independently scheduled Frequency Profiling can leave that field null, and both tables already share the workspace/table dimensions. It also does not relate Pipeline Run directly to Guardrail Results or Processing State; doing so alongside shared dimensions would create ambiguous paths and encourage fan-out.

## Date roles

The active event dates are:

| Table | Active model date |
| --- | --- |
| Pipeline Run | `run_date`, derived from `started_at` |
| Profile and Profile Frequency | `profile_date` / `frequency_profile_date`, derived from `_committed_at` |
| Guardrail Results | `guardrail_date`, derived from `_committed_at` |
| Processing State | `observation_date`, derived from `observed_at` |
| Data Access, Data Lineage, Data Catalogue and Data Contract | Date-only columns derived from `_committed_at` |
| Data Agreement | `start_date` |

Completion, acceptance, publication and expiry dates remain available in their source tables for explicit measures. They are not activated as competing relationships.

## Complex-column handling

The semantic model names every scalar source column explicitly in native SQL. It never issues `SELECT *`, which prevents connector inference from flattening or coercing native structures.

| Table | Excluded complex columns | Reporting consequence |
| --- | --- | --- |
| Catalogue | `load_strategy_parameters_json`, `scheduled_refresh_json`, `profile_key_candidates_json` | Current scalar identity, type, writer and freshness fields remain reportable when the endpoint exposes scalar projection. |
| Pipeline Registry | `registrations`, `revisions`, `approvals`, `selections`, `table_ownership`, `reservations` | Registration inventory, approvals, activated ownership and reservations cannot be shown from the SQL endpoint. |
| Pipeline Run | `operations`, `profiling`, `failures` | Read/Write modes, operation outcomes, stages, source associations and safe failure arrays cannot be shown. Scalar run headers remain reportable when exposed. |

`contract_payload_json`, `supporting_documents_json`, `approved_usage_json`, `custom_fields_json`, `result_payload_json`, and `warnings_json` are canonical scalar string columns. They are imported as strings but are not parsed into a second authoritative model.

## Fan-out controls

- KPI measures use distinct canonical IDs or count dimension rows at their actual grain.
- Facts connect through dimensions, not through other facts.
- Contract and Agreement versions use exact composite keys.
- Catalogue joins use workspace plus table identity, never `table_id` alone.
- Frequency rows are not assumed to have a parent Profile row.
- Source and target Processing State relationships are not active simultaneously.
- Activation is not inferred from Frozen Contract status. The report labels Frozen versions and documents the Registry boundary.
