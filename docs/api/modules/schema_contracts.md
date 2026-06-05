# `schema_contracts` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 10</span><span class="reference-chip">Internal helpers: 13</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns dataset-level schema contract suggestions, review state, versioned persistence, validation, enforcement, and evidence.

## Module manifest

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Module name</td>
      <td><code>schema_contracts</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns dataset-level schema contract suggestions, review state, versioned persistence, validation, enforcement, and evidence.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>10</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>13</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>fabric_input_output</code></td>
    </tr>
  </tbody>
</table>

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
      <td><a href="../../reference/build_schema_validation_evidence/"><code>build_schema_validation_evidence</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build structured schema-drift evidence rows for metadata storage.</td>
      <td><a href="../../reference/internal/schema_contracts/_now_utc_iso/"><code>_now_utc_iso</code></a> (internal), <a href="../../reference/internal/schema_contracts/_required_identity/"><code>_required_identity</code></a> (internal), <a href="../../reference/internal/schema_contracts/_validate_dataset_role/"><code>_validate_dataset_role</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/enforce_schema_result/"><code>enforce_schema_result</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Apply observe, warn, or fail behavior to a schema validation result.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_schema_contract/"><code>load_schema_contract</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load the latest approved schema contract for one specific source or target dataset.</td>
      <td><a href="../../reference/internal/schema_contracts/_bool/"><code>_bool</code></a> (internal), <a href="../../reference/internal/schema_contracts/_coerce_rows/"><code>_coerce_rows</code></a> (internal), <a href="../../reference/internal/schema_contracts/_get_any/"><code>_get_any</code></a> (internal), <a href="../../reference/internal/schema_contracts/_identity_matches/"><code>_identity_matches</code></a> (internal), <a href="../../reference/internal/schema_contracts/_required_identity/"><code>_required_identity</code></a> (internal), <a href="../../reference/internal/schema_contracts/_validate_dataset_role/"><code>_validate_dataset_role</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/suggest_schema_contract/"><code>suggest_schema_contract</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Draft dataset-level schema-contract column rows from profile metadata or a Spark DataFrame without writing metadata.</td>
      <td><a href="../../reference/internal/schema_contracts/_now_utc_iso/"><code>_now_utc_iso</code></a> (internal), <a href="../../reference/internal/schema_contracts/_required_identity/"><code>_required_identity</code></a> (internal), <a href="../../reference/internal/schema_contracts/_schema_rows/"><code>_schema_rows</code></a> (internal), <a href="../../reference/internal/schema_contracts/_validate_dataset_role/"><code>_validate_dataset_role</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Validate a Spark DataFrame shape against approved dataset-level schema contract columns without writing metadata or stopping the pipeline.</td>
      <td><a href="../../reference/internal/schema_contracts/_bool/"><code>_bool</code></a> (internal), <a href="../../reference/internal/schema_contracts/_coerce_rows/"><code>_coerce_rows</code></a> (internal), <a href="../../reference/internal/schema_contracts/_get_any/"><code>_get_any</code></a> (internal), <a href="../../reference/internal/schema_contracts/_schema_rows_from_dataframe/"><code>_schema_rows_from_dataframe</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_schema_contract/"><code>write_schema_contract</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Persist a versioned approved source or target dataset schema contract and normalized column rows.</td>
      <td><a href="../../reference/internal/schema_contracts/_bool/"><code>_bool</code></a> (internal), <a href="../../reference/internal/schema_contracts/_coerce_rows/"><code>_coerce_rows</code></a> (internal), <a href="../../reference/internal/schema_contracts/_next_contract_version/"><code>_next_contract_version</code></a> (internal), <a href="../../reference/internal/schema_contracts/_now_utc_iso/"><code>_now_utc_iso</code></a> (internal), <a href="../../reference/internal/schema_contracts/_required_identity/"><code>_required_identity</code></a> (internal), <a href="../../reference/internal/schema_contracts/_validate_dataset_role/"><code>_validate_dataset_role</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_schema_validation_evidence/"><code>write_schema_validation_evidence</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Append schema validation evidence through the configured metadata lakehouse route.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/build_schema_contract_review_state/"><code>build_schema_contract_review_state</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Normalize non-UI schema-contract review state for tests and notebooks.</td>
      <td><a href="../../reference/internal/schema_contracts/_bool/"><code>_bool</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/review_schema_contract/"><code>review_schema_contract</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Render a lightweight schema-contract approval widget and return editable approved settings and column rows.</td>
      <td><a href="../../reference/internal/schema_contracts/_latest_profile_for_dataset/"><code>_latest_profile_for_dataset</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>schema_contracts</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/build_schema_contract_review_state/"><code>build_schema_contract_review_state</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_bool"><code>_bool</code></a>, <a class="reference-chip" href="#normalize_spark_data_type"><code>normalize_spark_data_type</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/build_schema_validation_evidence/"><code>build_schema_validation_evidence</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="#_required_identity"><code>_required_identity</code></a>, <a class="reference-chip" href="#_validate_dataset_role"><code>_validate_dataset_role</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/enforce_schema_result/"><code>enforce_schema_result</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/load_schema_contract/"><code>load_schema_contract</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_bool"><code>_bool</code></a>, <a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_get_any"><code>_get_any</code></a>, <a class="reference-chip" href="#_identity_matches"><code>_identity_matches</code></a>, <a class="reference-chip" href="#_required_identity"><code>_required_identity</code></a>, <a class="reference-chip" href="#_validate_dataset_role"><code>_validate_dataset_role</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/review_schema_contract/"><code>review_schema_contract</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_latest_profile_for_dataset"><code>_latest_profile_for_dataset</code></a>, <a class="reference-chip" href="../../reference/build_schema_contract_review_state/"><code>build_schema_contract_review_state</code></a>, <a class="reference-chip" href="../../reference/suggest_schema_contract/"><code>suggest_schema_contract</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/suggest_schema_contract/"><code>suggest_schema_contract</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="#_required_identity"><code>_required_identity</code></a>, <a class="reference-chip" href="#_schema_rows"><code>_schema_rows</code></a>, <a class="reference-chip" href="#_validate_dataset_role"><code>_validate_dataset_role</code></a>, <a class="reference-chip" href="#normalize_spark_data_type"><code>normalize_spark_data_type</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/validate_schema/"><code>validate_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_bool"><code>_bool</code></a>, <a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_get_any"><code>_get_any</code></a>, <a class="reference-chip" href="#_schema_rows_from_dataframe"><code>_schema_rows_from_dataframe</code></a>, <a class="reference-chip" href="#normalize_spark_data_type"><code>normalize_spark_data_type</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/write_schema_contract/"><code>write_schema_contract</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_bool"><code>_bool</code></a>, <a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_next_contract_version"><code>_next_contract_version</code></a>, <a class="reference-chip" href="#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="#_required_identity"><code>_required_identity</code></a>, <a class="reference-chip" href="#_validate_dataset_role"><code>_validate_dataset_role</code></a>, <a class="reference-chip" href="#normalize_spark_data_type"><code>normalize_spark_data_type</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/write_schema_validation_evidence/"><code>write_schema_validation_evidence</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
</ul>
</section>

### Related internal helpers

<details>
<summary>Show internal helpers</summary>

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
      <td><a href="../../reference/internal/schema_contracts/_bool/"><code>_bool</code></a></td>
      <td><a href="../../reference/build_schema_contract_review_state/"><code>build_schema_contract_review_state</code></a>, <a href="../../reference/load_schema_contract/"><code>load_schema_contract</code></a>, <a href="../../reference/validate_schema/"><code>validate_schema</code></a>, <a href="../../reference/write_schema_contract/"><code>write_schema_contract</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_coerce_rows/"><code>_coerce_rows</code></a></td>
      <td><a href="../../reference/load_schema_contract/"><code>load_schema_contract</code></a>, <a href="../../reference/validate_schema/"><code>validate_schema</code></a>, <a href="../../reference/write_schema_contract/"><code>write_schema_contract</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_get_any/"><code>_get_any</code></a></td>
      <td><a href="../../reference/load_schema_contract/"><code>load_schema_contract</code></a>, <a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_identity_matches/"><code>_identity_matches</code></a></td>
      <td><a href="../../reference/load_schema_contract/"><code>load_schema_contract</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_latest_profile_for_dataset/"><code>_latest_profile_for_dataset</code></a></td>
      <td><a href="../../reference/review_schema_contract/"><code>review_schema_contract</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_next_contract_version/"><code>_next_contract_version</code></a></td>
      <td><a href="../../reference/write_schema_contract/"><code>write_schema_contract</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_now_utc_iso/"><code>_now_utc_iso</code></a></td>
      <td><a href="../../reference/build_schema_validation_evidence/"><code>build_schema_validation_evidence</code></a>, <a href="../../reference/suggest_schema_contract/"><code>suggest_schema_contract</code></a>, <a href="../../reference/write_schema_contract/"><code>write_schema_contract</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_required_identity/"><code>_required_identity</code></a></td>
      <td><a href="../../reference/build_schema_validation_evidence/"><code>build_schema_validation_evidence</code></a>, <a href="../../reference/load_schema_contract/"><code>load_schema_contract</code></a>, <a href="../../reference/suggest_schema_contract/"><code>suggest_schema_contract</code></a>, <a href="../../reference/write_schema_contract/"><code>write_schema_contract</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_row_dict/"><code>_row_dict</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_schema_rows/"><code>_schema_rows</code></a></td>
      <td><a href="../../reference/suggest_schema_contract/"><code>suggest_schema_contract</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_schema_rows_from_dataframe/"><code>_schema_rows_from_dataframe</code></a></td>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_schema_rows_from_profile/"><code>_schema_rows_from_profile</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/schema_contracts/_validate_dataset_role/"><code>_validate_dataset_role</code></a></td>
      <td><a href="../../reference/build_schema_validation_evidence/"><code>build_schema_validation_evidence</code></a>, <a href="../../reference/load_schema_contract/"><code>load_schema_contract</code></a>, <a href="../../reference/suggest_schema_contract/"><code>suggest_schema_contract</code></a>, <a href="../../reference/write_schema_contract/"><code>write_schema_contract</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_bool"><code>_bool</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_row_dict"><code>_row_dict</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_any"><code>_get_any</code></a>
</li>
<li>
<a class="reference-chip" href="#_identity_matches"><code>_identity_matches</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_any"><code>_get_any</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_profile_for_dataset"><code>_latest_profile_for_dataset</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_get_any"><code>_get_any</code></a>
</li>
<li>
<a class="reference-chip" href="#_next_contract_version"><code>_next_contract_version</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_any"><code>_get_any</code></a>
</li>
<li>
<a class="reference-chip" href="#_now_utc_iso"><code>_now_utc_iso</code></a>
</li>
<li>
<a class="reference-chip" href="#_required_identity"><code>_required_identity</code></a>
</li>
<li>
<a class="reference-chip" href="#_row_dict"><code>_row_dict</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema_rows"><code>_schema_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_schema_rows_from_dataframe"><code>_schema_rows_from_dataframe</code></a>, <a class="reference-chip" href="#_schema_rows_from_profile"><code>_schema_rows_from_profile</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema_rows_from_dataframe"><code>_schema_rows_from_dataframe</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#normalize_spark_data_type"><code>normalize_spark_data_type</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema_rows_from_profile"><code>_schema_rows_from_profile</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_bool"><code>_bool</code></a>, <a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_get_any"><code>_get_any</code></a>, <a class="reference-chip" href="#normalize_spark_data_type"><code>normalize_spark_data_type</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_dataset_role"><code>_validate_dataset_role</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_required_identity"><code>_required_identity</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>
