# List of Metadata Tables

These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

<figure class="metadata-model-image">
  <img src="../../assets/fabricops-metadata-model.png" alt="FabricOps metadata model" />
</figure>

<div class="fabricops-table-wide" markdown="1">

<table class="metadata-tables-overview">
  <colgroup>
    <col class="metadata-tables-overview__name" />
    <col class="metadata-tables-overview__purpose" />
    <col class="metadata-tables-overview__step" />
  </colgroup>
  <thead>
    <tr>
      <th>Metadata table</th>
      <th>Purpose</th>
      <th>Primary template step</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="metadata-data-access.md"><code>METADATA_DATA_ACCESS</code></a></td>
      <td>Externally collected access inventory for workspace, object, schema, and table access review.</td>
      <td>External inventory ingestion / governance access review.</td>
    </tr>
    <tr>
      <td><a href="metadata-data-agreement.md"><code>METADATA_DATA_AGREEMENT</code></a></td>
      <td>Agreement records that describe approved use, steward, recipient, and lifecycle context.</td>
      <td>01_agreement.ipynb, 02_pipeline.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-data-agreement-evidence.md"><code>METADATA_DATA_AGREEMENT_EVIDENCE</code></a></td>
      <td>Supporting agreement files and evidence metadata captured during agreement intake.</td>
      <td>01_agreement.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-data-catalogue.md"><code>METADATA_DATA_CATALOGUE</code></a></td>
      <td>Observed table and column profile evidence. This is runtime evidence, not approved guardrail intent.</td>
      <td>02_pipeline.ipynb, 03_governance.ipynb, 99_explore.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-data-lineage-table.md"><code>METADATA_DATA_LINEAGE_TABLE</code></a></td>
      <td>Source-to-target lineage evidence written by pipeline runs.</td>
      <td>02_pipeline.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-data-steward.md"><code>METADATA_DATA_STEWARD</code></a></td>
      <td>Active and historical data steward records used by agreement intake.</td>
      <td>01_agreement.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-enrichment-rules.md"><code>METADATA_ENRICHMENT_RULES</code></a></td>
      <td>Append-only enrichment and business metadata intent authored and reviewed through governance workflows.</td>
      <td>02_pipeline.ipynb, 03_governance.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-guardrail-results.md"><code>METADATA_GUARDRAIL_RESULTS</code></a></td>
      <td>Runtime guardrail outcomes written by pipeline enforcement.</td>
      <td>02_pipeline.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-guardrail-rules.md"><code>METADATA_GUARDRAIL_RULES</code></a></td>
      <td>Approved or pending schema, freshness, profile behavior, and DQ guardrail intent.</td>
      <td>02_pipeline.ipynb, 03_governance.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-notebook-registry.md"><code>METADATA_NOTEBOOK_REGISTRY</code></a></td>
      <td>Active notebook registration records linking notebooks to agreement, environment, dataset, and pipeline context.</td>
      <td>02_pipeline.ipynb</td>
    </tr>
    <tr>
      <td><a href="metadata-pipeline-runs.md"><code>METADATA_PIPELINE_RUNS</code></a></td>
      <td>Pipeline run summary evidence for execution, guardrail, lineage, and catalogue status.</td>
      <td>02_pipeline.ipynb</td>
    </tr>
  </tbody>
</table>

</div>
