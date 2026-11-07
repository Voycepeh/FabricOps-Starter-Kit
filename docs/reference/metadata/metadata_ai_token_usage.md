# METADATA_AI_TOKEN_USAGE

Records measured usage for each FabricOps AI Functions request without prompts or generated text.

## Writer functions

* [`widget_data_contract`](../../api/reference/widget_data_contract.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `misc`

**Grain:** One append-only row per provider invocation, identified by usage_id.

**Primary key:** `usage_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

**Implementation details:** Written automatically to the configured misc schema in the Metadata Lakehouse. gpt-5-mini is the default; gpt-5.1 remains an explicit override. Provider status describes response execution, not subsequent suggestion validation. Failed requests retain unavailable counters as NULL. Missing statistics are never inferred. Currency and CU estimates are derived separately from model/token counts. Setup creates this table; writes also create it when missing. Audit failures leave the provider result usable and are reported without replaying the request. Calls made directly to df.ai outside FabricOps helpers are not intercepted.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">35</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">27</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>usage_id</code></td><td><code>string</code></td><td>Unique invocation identifier, also used for idempotent Delta appends.</td></tr>
<tr class="metadata-column--engineering"><td><code>provider</code></td><td><code>string</code></td><td>Fabric AI Functions provider identifier.</td></tr>
<tr class="metadata-column--engineering"><td><code>operation</code></td><td><code>string</code></td><td>FabricOps authoring operation that submitted this request.</td></tr>
<tr class="metadata-column--engineering"><td><code>model</code></td><td><code>string</code></td><td>Configured built-in model deployment; provider-reported models are retained in statistics_json.</td></tr>
<tr class="metadata-column--engineering"><td><code>reasoning_effort</code></td><td><code>string</code></td><td>Requested reasoning effort; NULL delegates to the provider default.</td></tr>
<tr class="metadata-column--engineering"><td><code>verbosity</code></td><td><code>string</code></td><td>Requested response verbosity; NULL delegates to the provider default.</td></tr>
<tr class="metadata-column--engineering"><td><code>status</code></td><td><code>string</code></td><td>Provider request outcome: succeeded, provider_error, or execution_error. Later suggestion validation is separate.</td></tr>
<tr class="metadata-column--engineering"><td><code>statistics_status</code></td><td><code>string</code></td><td>Whether provider statistics were available after result collection.</td></tr>
<tr class="metadata-column--engineering"><td><code>started_at</code></td><td><code>timestamp</code></td><td>UTC instant when provider execution began.</td></tr>
<tr class="metadata-column--engineering"><td><code>completed_at</code></td><td><code>timestamp</code></td><td>UTC instant when provider execution ended, before the audit append.</td></tr>
<tr class="metadata-column--engineering"><td><code>duration_ms</code></td><td><code>long</code></td><td>Elapsed provider execution and statistics collection time in milliseconds; excludes audit storage.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>Originating notebook workspace from runtime audit identity.</td></tr>
<tr class="metadata-column--engineering"><td><code>evidence_workspace_id</code></td><td><code>string</code></td><td>Workspace selected for authoring evidence, when supplied by the widget.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a column across workspace, dataset, table, and column context.</td></tr>
<tr class="metadata-column--engineering"><td><code>contract_id</code></td><td><code>string</code></td><td>Stable identifier for the contract row.</td></tr>
<tr class="metadata-column--engineering"><td><code>contract_version</code></td><td><code>long</code></td><td>Version recorded for the contract row.</td></tr>
<tr class="metadata-column--engineering"><td><code>input_tokens</code></td><td><code>long</code></td><td>Measured input tokens across all reported statistics rows, including cached input; NULL if incomplete.</td></tr>
<tr class="metadata-column--engineering"><td><code>output_tokens</code></td><td><code>long</code></td><td>Measured output tokens, including reasoning; NULL if incomplete.</td></tr>
<tr class="metadata-column--engineering"><td><code>cached_tokens</code></td><td><code>long</code></td><td>Cached input breakdown already included in input_tokens; NULL if unavailable.</td></tr>
<tr class="metadata-column--engineering"><td><code>reasoning_tokens</code></td><td><code>long</code></td><td>Reasoning output breakdown already included in output_tokens; NULL if unavailable.</td></tr>
<tr class="metadata-column--engineering"><td><code>num_successful</code></td><td><code>long</code></td><td>Metadata Ai Token Usage field <code>num_successful</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>num_exceptions</code></td><td><code>long</code></td><td>Metadata Ai Token Usage field <code>num_exceptions</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>num_unevaluated</code></td><td><code>long</code></td><td>Metadata Ai Token Usage field <code>num_unevaluated</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>num_harmful</code></td><td><code>long</code></td><td>Metadata Ai Token Usage field <code>num_harmful</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>error_type</code></td><td><code>string</code></td><td>Exception class only; no exception message or provider response content.</td></tr>
<tr class="metadata-column--engineering"><td><code>statistics_json</code></td><td><code>string</code></td><td>Filtered measured provider statistics, excluding prompts and generated text.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_by</code></td><td><code>string</code></td><td>User principal or runtime identity that committed the metadata row.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_at</code></td><td><code>timestamp</code></td><td>Timestamp when the metadata row was committed.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_id</code></td><td><code>string</code></td><td>Fabric workspace identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_name</code></td><td><code>string</code></td><td>Fabric workspace name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_id</code></td><td><code>string</code></td><td>Fabric notebook identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_name</code></td><td><code>string</code></td><td>Fabric notebook name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_metadata_lakehouse_name</code></td><td><code>string</code></td><td>Configured metadata lakehouse name used for the write.</td></tr>
<tr class="metadata-column--audit"><td><code>_activity_id</code></td><td><code>string</code></td><td>Fabric execution activity identifier for the current notebook or pipeline run.</td></tr>
</tbody></table>
</div>
