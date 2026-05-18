# `metadata` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 3</span></div>

## Module purpose

Owns metadata/contract store access, evidence persistence, agreement metadata, notebook evidence, and contract assembly inputs.

## Public callables

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Callable</th>
      <th>Tier</th>
      <th>Type</th>
      <th>Summary</th>
      <th>Related helpers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load notebook registration metadata rows for agreement notebook traceability.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Register current notebook metadata evidence for agreement traceability.</td>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a> (internal), <a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a> (internal), <a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Advanced dependency sections


### Related internal helpers

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Helper</th>
      <th>Related public callables</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_extract_columns_from_profile/"><code>_extract_columns_from_profile</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_key_part/"><code>_key_part</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_now_utc_iso/"><code>_now_utc_iso</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_resolve_action_by/"><code>_resolve_action_by</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_sha256_key/"><code>_sha256_key</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

### Callable relationships

<div class="module-mermaid-scroll module-diagram-desktop">
```mermaid
flowchart TB
  classDef currentModule fill:#ffe8cc,stroke:#e65100,stroke-width:4px,color:#3e2723;
  classDef externalModule fill:#f7f7f7,stroke:#b0bec5,stroke-width:1px,color:#607d8b;
  classDef currentCallable fill:#ffd180,stroke:#ef6c00,stroke-width:2px;
  classDef externalCallable fill:#eceff1,stroke:#b0bec5,stroke-width:1px,color:#455a64;
  subgraph m_metadata[metadata]
    fabricops_kit_metadata__context_get["_context_get"]
    fabricops_kit_metadata__key_part["_key_part"]
    fabricops_kit_metadata__now_utc_iso["_now_utc_iso"]
    fabricops_kit_metadata__resolve_action_by["_resolve_action_by"]
    fabricops_kit_metadata__runtime_context["_runtime_context"]
    fabricops_kit_metadata__safe_str["_safe_str"]
    fabricops_kit_metadata__sha256_key["_sha256_key"]
    fabricops_kit_metadata_build_dq_rule_key["build_dq_rule_key"]
    fabricops_kit_metadata_build_evidence_row["build_evidence_row"]
    fabricops_kit_metadata_build_metadata_column_key["build_metadata_column_key"]
    fabricops_kit_metadata_build_metadata_table_key["build_metadata_table_key"]
    fabricops_kit_metadata_column_context_rows_for_spark["column_context_rows_for_spark"]
    fabricops_kit_metadata_register_current_notebook["register_current_notebook"]
    fabricops_kit_metadata_write_column_business_context["write_column_business_context"]
    fabricops_kit_metadata_write_column_governance_context["write_column_governance_context"]
    fabricops_kit_metadata_write_metadata_rows["write_metadata_rows"]
  end
  subgraph m_business_context[business_context]
    fabricops_kit_business_context_review_business_context["review_business_context"]
    fabricops_kit_business_context_write_business_context["write_business_context"]
  end
  subgraph m_data_governance[data_governance]
    fabricops_kit_data_governance__approved_widget_rows["_approved_widget_rows"]
    fabricops_kit_data_governance_review_governance["review_governance"]
  end
  subgraph m_data_quality[data_quality]
    fabricops_kit_data_quality__attach_rule_metadata_keys["_attach_rule_metadata_keys"]
    fabricops_kit_data_quality__build_dq_rule_deactivation_metadata_df["_build_dq_rule_deactivation_metadata_df"]
    fabricops_kit_data_quality__build_dq_rule_deactivations["_build_dq_rule_deactivations"]
    fabricops_kit_data_quality__build_dq_rule_history["_build_dq_rule_history"]
    fabricops_kit_data_quality__build_dq_rules_metadata_df["_build_dq_rules_metadata_df"]
  end
  subgraph m_fabric_input_output[fabric_input_output]
    fabricops_kit_fabric_input_output_write_lakehouse_table["write_lakehouse_table"]
  end
  fabricops_kit_business_context_review_business_context --> fabricops_kit_metadata_build_metadata_column_key
  fabricops_kit_business_context_review_business_context --> fabricops_kit_metadata_build_metadata_table_key
  fabricops_kit_business_context_write_business_context --> fabricops_kit_metadata_write_column_business_context
  fabricops_kit_data_governance__approved_widget_rows --> fabricops_kit_metadata__resolve_action_by
  fabricops_kit_data_governance_review_governance --> fabricops_kit_metadata__now_utc_iso
  fabricops_kit_data_governance_review_governance --> fabricops_kit_metadata_build_metadata_column_key
  fabricops_kit_data_governance_review_governance --> fabricops_kit_metadata_build_metadata_table_key
  fabricops_kit_data_quality__attach_rule_metadata_keys --> fabricops_kit_metadata_build_dq_rule_key
  fabricops_kit_data_quality__attach_rule_metadata_keys --> fabricops_kit_metadata_build_metadata_column_key
  fabricops_kit_data_quality__attach_rule_metadata_keys --> fabricops_kit_metadata_build_metadata_table_key
  fabricops_kit_data_quality__build_dq_rule_deactivation_metadata_df --> fabricops_kit_metadata__now_utc_iso
  fabricops_kit_data_quality__build_dq_rule_deactivation_metadata_df --> fabricops_kit_metadata__resolve_action_by
  fabricops_kit_data_quality__build_dq_rule_deactivations --> fabricops_kit_metadata__resolve_action_by
  fabricops_kit_data_quality__build_dq_rule_history --> fabricops_kit_metadata__resolve_action_by
  fabricops_kit_data_quality__build_dq_rules_metadata_df --> fabricops_kit_metadata__now_utc_iso
  fabricops_kit_data_quality__build_dq_rules_metadata_df --> fabricops_kit_metadata__resolve_action_by
  fabricops_kit_metadata__resolve_action_by --> fabricops_kit_metadata__context_get
  fabricops_kit_metadata__resolve_action_by --> fabricops_kit_metadata__runtime_context
  fabricops_kit_metadata__runtime_context --> fabricops_kit_metadata__context_get
  fabricops_kit_metadata__sha256_key --> fabricops_kit_metadata__key_part
  fabricops_kit_metadata_build_dq_rule_key --> fabricops_kit_metadata__sha256_key
  fabricops_kit_metadata_build_evidence_row --> fabricops_kit_metadata__now_utc_iso
  fabricops_kit_metadata_build_metadata_column_key --> fabricops_kit_metadata__sha256_key
  fabricops_kit_metadata_build_metadata_table_key --> fabricops_kit_metadata__sha256_key
  fabricops_kit_metadata_register_current_notebook --> fabricops_kit_metadata__context_get
  fabricops_kit_metadata_register_current_notebook --> fabricops_kit_metadata__runtime_context
  fabricops_kit_metadata_register_current_notebook --> fabricops_kit_metadata__safe_str
  fabricops_kit_metadata_register_current_notebook --> fabricops_kit_metadata_write_metadata_rows
  fabricops_kit_metadata_write_column_business_context --> fabricops_kit_metadata_write_metadata_rows
  fabricops_kit_metadata_write_column_governance_context --> fabricops_kit_metadata_write_metadata_rows
  fabricops_kit_metadata_write_metadata_rows --> fabricops_kit_fabric_input_output_write_lakehouse_table
  fabricops_kit_metadata_write_metadata_rows --> fabricops_kit_metadata_column_context_rows_for_spark
  linkStyle 16,17,18,19,20,21,22,23,24,25,26,27,28,29,31 stroke:#ef6c00,stroke-width:2.2px;
  linkStyle 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,30 stroke:#90a4ae,stroke-width:1.2px,stroke-dasharray: 4 2;
  class m_metadata currentModule;
  class m_business_context,m_data_governance,m_data_quality,m_fabric_input_output externalModule;
  class fabricops_kit_metadata__context_get,fabricops_kit_metadata__key_part,fabricops_kit_metadata__now_utc_iso,fabricops_kit_metadata__resolve_action_by,fabricops_kit_metadata__runtime_context,fabricops_kit_metadata__safe_str,fabricops_kit_metadata__sha256_key,fabricops_kit_metadata_build_dq_rule_key,fabricops_kit_metadata_build_evidence_row,fabricops_kit_metadata_build_metadata_column_key,fabricops_kit_metadata_build_metadata_table_key,fabricops_kit_metadata_column_context_rows_for_spark,fabricops_kit_metadata_register_current_notebook,fabricops_kit_metadata_write_column_business_context,fabricops_kit_metadata_write_column_governance_context,fabricops_kit_metadata_write_metadata_rows currentCallable;
  class fabricops_kit_business_context_review_business_context,fabricops_kit_business_context_write_business_context,fabricops_kit_data_governance__approved_widget_rows,fabricops_kit_data_governance_review_governance,fabricops_kit_data_quality__attach_rule_metadata_keys,fabricops_kit_data_quality__build_dq_rule_deactivation_metadata_df,fabricops_kit_data_quality__build_dq_rule_deactivations,fabricops_kit_data_quality__build_dq_rule_history,fabricops_kit_data_quality__build_dq_rules_metadata_df,fabricops_kit_fabric_input_output_write_lakehouse_table externalCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/metadata/#_resolve_action_by"><code>_resolve_action_by</code></a> → <a class="reference-chip" href="../modules/metadata/#_context_get"><code>_context_get</code></a>
<a class="reference-chip" href="../modules/metadata/#_resolve_action_by"><code>_resolve_action_by</code></a> → <a class="reference-chip" href="../modules/metadata/#_runtime_context"><code>_runtime_context</code></a>
<a class="reference-chip" href="../modules/metadata/#_runtime_context"><code>_runtime_context</code></a> → <a class="reference-chip" href="../modules/metadata/#_context_get"><code>_context_get</code></a>
<a class="reference-chip" href="../modules/metadata/#_sha256_key"><code>_sha256_key</code></a> → <a class="reference-chip" href="../modules/metadata/#_key_part"><code>_key_part</code></a>
<a class="reference-chip" href="../modules/metadata/#build_dq_rule_key"><code>build_dq_rule_key</code></a> → <a class="reference-chip" href="../modules/metadata/#_sha256_key"><code>_sha256_key</code></a>
<a class="reference-chip" href="../modules/metadata/#build_evidence_row"><code>build_evidence_row</code></a> → <a class="reference-chip" href="../modules/metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>
<a class="reference-chip" href="../modules/metadata/#build_metadata_column_key"><code>build_metadata_column_key</code></a> → <a class="reference-chip" href="../modules/metadata/#_sha256_key"><code>_sha256_key</code></a>
<a class="reference-chip" href="../modules/metadata/#build_metadata_table_key"><code>build_metadata_table_key</code></a> → <a class="reference-chip" href="../modules/metadata/#_sha256_key"><code>_sha256_key</code></a>
<a class="reference-chip" href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a> → <a class="reference-chip" href="../modules/metadata/#_context_get"><code>_context_get</code></a>
<a class="reference-chip" href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a> → <a class="reference-chip" href="../modules/metadata/#_runtime_context"><code>_runtime_context</code></a>
<a class="reference-chip" href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a> → <a class="reference-chip" href="../modules/metadata/#_safe_str"><code>_safe_str</code></a>
<a class="reference-chip" href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a> → <a class="reference-chip" href="../modules/metadata/#write_metadata_rows"><code>write_metadata_rows</code></a>
<a class="reference-chip" href="../modules/metadata/#write_column_business_context"><code>write_column_business_context</code></a> → <a class="reference-chip" href="../modules/metadata/#write_metadata_rows"><code>write_metadata_rows</code></a>
<a class="reference-chip" href="../modules/metadata/#write_column_governance_context"><code>write_column_governance_context</code></a> → <a class="reference-chip" href="../modules/metadata/#write_metadata_rows"><code>write_metadata_rows</code></a>
<a class="reference-chip" href="../modules/metadata/#write_metadata_rows"><code>write_metadata_rows</code></a> → <a class="reference-chip" href="../modules/metadata/#column_context_rows_for_spark"><code>column_context_rows_for_spark</code></a>
</div>
#### Used by other modules

<div class="callable-chip-group">
<span class="reference-chip"><code>business_context</code> (3)</span>
<span class="reference-chip"><code>data_governance</code> (4)</span>
<span class="reference-chip"><code>data_quality</code> (9)</span>
</div>
#### Uses other modules

<div class="callable-chip-group">
<span class="reference-chip"><code>fabric_input_output</code> (1)</span>
</div>
</div>
