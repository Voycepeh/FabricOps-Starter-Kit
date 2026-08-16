# List of Metadata Tables

FabricOps metadata tables capture the governance, engineering, quality, and contract information created as data moves through the workflow.

The diagram below shows how the FabricOps metadata tables relate to one another across agreement, source observation, profiling, lineage, guardrails, and contracts.

![FabricOps metadata model](../assets/fabricops-metadata-model.png)

## Data Agreement versus Data Contract

A Data Agreement defines why data may be shared, who is accountable, the approved purpose and usage, and the period the agreement applies to.

A Data Contract defines the specific data covered by that agreement: what it is, how it is structured, its sensitivity, quality requirements, schema, freshness, and approved uses.

One Data Agreement can govern multiple Data Contracts.

!!! note "About the identities below"
    Identity describes how FabricOps recognizes the logical record or snapshot. Links to shows the shared keys used to connect metadata across the model. The underlying Delta tables do not enforce relational primary or foreign key constraints.

<div class="metadata-workflow-list">

<a class="metadata-workflow-row" href="metadata/metadata_data_steward.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">01</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_DATA_STEWARD</strong>
      <span>Know who is responsible for the data.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One steward record</span>
    <span><b>Identity</b> <code>steward_id</code></span>
    <span><b>Links to</b> None</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_data_agreement.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">02</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_DATA_AGREEMENT</strong>
      <span>Capture why data is shared, with whom, and under what conditions.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One agreement version</span>
    <span><b>Identity</b> <code>agreement_id</code> + <code>agreement_version</code></span>
    <span><b>Links to</b> Provider and recipient steward → Data Steward</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_source_observation.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">03</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_SOURCE_OBSERVATION</strong>
      <span>See whether source data has arrived and changed as expected.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One source partition observation</span>
    <span><b>Identity</b> Table + partition + observation time</span>
    <span><b>Links to</b> <code>metadata_table_key</code> → Data Catalogue</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_data_catalogue.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">04</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_DATA_CATALOGUE</strong>
      <span>Understand what data is available and how it is structured.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One column in one observed table schema</span>
    <span><b>Identity</b> Environment + table + column + schema fingerprint</span>
    <span><b>Links to</b> <code>metadata_table_key</code>, <code>metadata_column_key</code></span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_data_profiled.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">05</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_DATA_PROFILED</strong>
      <span>Understand the shape, completeness, and characteristics of the data.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One column in one profile snapshot</span>
    <span><b>Identity</b> <code>metadata_column_key</code> + <code>profiled_at</code></span>
    <span><b>Links to</b> <code>metadata_table_key</code>, <code>metadata_column_key</code> → Data Catalogue</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_data_profiled_frequency.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">06</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_DATA_PROFILED_FREQUENCY</strong>
      <span>See how values are distributed across the data.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One distinct value in one profiled column snapshot</span>
    <span><b>Identity</b> Column + profile time + frequency rank</span>
    <span><b>Links to</b> <code>metadata_column_key</code> + <code>profiled_at</code> → Data Profiled</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_data_lineage.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">07</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_DATA_LINEAGE</strong>
      <span>See where the data came from and where it ends up.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One source or target table in one Fabric activity</span>
    <span><b>Identity</b> <code>lineage_event_id</code></span>
    <span><b>Links to</b> <code>metadata_table_key</code> → Data Catalogue</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_enrichment.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">08</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_ENRICHMENT</strong>
      <span>Add business and governance context to the data.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One enrichment entry</span>
    <span><b>Identity</b> <code>enrichment_id</code></span>
    <span><b>Links to</b> <code>metadata_key</code> → Data Catalogue table or column</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_guardrail.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">09</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_GUARDRAIL</strong>
      <span>Define the expectations that data used in the ETL pipeline should meet.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One append-only guardrail lifecycle record</span>
    <span><b>Identity</b> Logical rule IDs plus lifecycle/version context</span>
    <span><b>Links to</b> <code>metadata_table_key</code>, <code>metadata_column_key</code> → Data Catalogue</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_guardrail_results.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">10</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_GUARDRAIL_RESULTS</strong>
      <span>See whether the data in an ETL pipeline run met those expectations.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One guardrail result in one pipeline run</span>
    <span><b>Identity</b> <code>guardrail_result_id</code></span>
    <span><b>Links to</b> <code>guardrail_rule_id</code> → Guardrail; <code>metadata_table_key</code> → Data Catalogue</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_guardrail_row_results.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">11</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_GUARDRAIL_ROW_RESULTS</strong>
      <span>See which records caused a data quality check to fail.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One failed source row × failed DQ rule</span>
    <span><b>Identity</b> <code>guardrail_row_result_id</code></span>
    <span><b>Links to</b> <code>guardrail_result_id</code> → Guardrail Results; <code>guardrail_rule_id</code> → Guardrail</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_data_contract.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">12</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_DATA_CONTRACT</strong>
      <span>Define what the data is, how it is structured, its sensitivity, quality requirements, schema, freshness, and approved uses, and link it to the Data Agreement.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One table membership in one saved contract inventory</span>
    <span><b>Identity</b> Agreement + table within one save activity</span>
    <span><b>Links to</b> <code>agreement_id</code> → Data Agreement; <code>metadata_table_key</code> → Data Catalogue</span>
  </span>
</a>

<a class="metadata-workflow-row" href="metadata/metadata_data_access.md">
  <span class="metadata-workflow-row__main">
    <span class="metadata-workflow-row__step">13</span>
    <span class="metadata-workflow-row__content">
      <strong>METADATA_DATA_ACCESS</strong>
      <span>Record who can use the data and how they are allowed to use it.</span>
    </span>
  </span>
  <span class="metadata-workflow-row__facts">
    <span><b>Grain</b> One access record</span>
    <span><b>Identity</b> Not formally defined yet</span>
    <span><b>Links to</b> <code>metadata_table_key</code>, <code>metadata_column_key</code> → Data Catalogue</span>
  </span>
</a>

</div>
