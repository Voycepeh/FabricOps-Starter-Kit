# FabricOps glossary

Searchable source of truth for FabricOps documentation wording and page-level glossary references.

## Data engineering concepts

<div class="glossary-definition-list">

<section class="glossary-definition-card" id="append">
<p class="glossary-definition-title">append</p>
<p>Write mode that adds rows to existing data.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use append for write mode.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> add when mode meant</p>
</section>

<section class="glossary-definition-card" id="dashboard">
<p class="glossary-definition-title">dashboard</p>
<p>Visual summary of metrics, status, or review evidence.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use dashboard for visual summary.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> report when dashboard meant</p>
</section>

<section class="glossary-definition-card" id="data-quality-rule">
<p class="glossary-definition-title">data quality rule</p>
<p>Executable expectation that checks data values, completeness, or relationships.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `DQ rule`, `DQ rules`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use data quality rule in narrative; DQ rule after introduced.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> rule when ambiguous</p>
</section>

<section class="glossary-definition-card" id="dataframe">
<p class="glossary-definition-title">DataFrame</p>
<p>Spark tabular data structure held in memory during processing.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `DataFrames`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use DataFrame for Spark object.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> data frame</p>
</section>

<section class="glossary-definition-card" id="deterministic-logic">
<p class="glossary-definition-title">deterministic logic</p>
<p>Logic that produces the same result for the same inputs.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use deterministic logic for reproducible behavior.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> AI-generated logic when deterministic matters</p>
</section>

<section class="glossary-definition-card" id="distinct-value">
<p class="glossary-definition-title">distinct value</p>
<p>Unique value observed in a column.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use distinct value/distinct values.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> unique value when DQ unique rule meant</p>
</section>

<section class="glossary-definition-card" id="distribution">
<p class="glossary-definition-title">distribution</p>
<p>Shape or frequency of values in data.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use distribution for value spread.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> profile summary when distribution meant</p>
</section>

<section class="glossary-definition-card" id="dq">
<p class="glossary-definition-title">DQ</p>
<p>Short form of data quality.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use DQ only after data quality is clear.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> quality only when ambiguous</p>
</section>

<section class="glossary-definition-card" id="freshness">
<p class="glossary-definition-title">freshness</p>
<p>Measure of whether data is recent enough for its expected use.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use freshness for recency checks.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> timeliness when check is freshness</p>
</section>

<section class="glossary-definition-card" id="lineage">
<p class="glossary-definition-title">lineage</p>
<p>Trace of how data moves from sources through transformations to targets.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use lineage for data movement trace.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> dependency list when lineage meant</p>
</section>

<section class="glossary-definition-card" id="null">
<p class="glossary-definition-title">null</p>
<p>Missing or unknown value in a column.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use null for missing values.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> blank when null meant</p>
</section>

<section class="glossary-definition-card" id="overwrite">
<p class="glossary-definition-title">overwrite</p>
<p>Write mode that replaces existing data.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use overwrite for write mode.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> replace when write mode meant</p>
</section>

<section class="glossary-definition-card" id="partitioning">
<p class="glossary-definition-title">partitioning</p>
<p>Organizing data into partitions for storage or processing.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use partitioning for partition design.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> sharding</p>
</section>

<section class="glossary-definition-card" id="pipeline">
<p class="glossary-definition-title">pipeline</p>
<p>Sequence of steps that reads source data, transforms it, checks it, and writes outputs.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `pipelines`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use pipeline for end-to-end processing.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> workflow if processing pipeline meant</p>
</section>

<section class="glossary-definition-card" id="repartitioning">
<p class="glossary-definition-title">repartitioning</p>
<p>Changing DataFrame partitions before processing or writing.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use repartitioning for Spark partition changes.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> partitioning when action is repartition</p>
</section>

<section class="glossary-definition-card" id="row-count">
<p class="glossary-definition-title">row count</p>
<p>Number of rows in a DataFrame or table.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use row count for counts.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> records when exact rows meant</p>
</section>

<section class="glossary-definition-card" id="runtime">
<p class="glossary-definition-title">runtime</p>
<p>Execution period and environment where notebook or pipeline code runs.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use runtime for execution context.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> run time unless prose needs it</p>
</section>

<section class="glossary-definition-card" id="schema">
<p class="glossary-definition-title">schema</p>
<p>Column names and data types for a DataFrame or table.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use schema for structure.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> layout when schema is meant</p>
</section>

<section class="glossary-definition-card" id="source">
<p class="glossary-definition-title">source</p>
<p>Input side of a data flow.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `sources`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use source for generic input side.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> upstream when source is clearer</p>
</section>

<section class="glossary-definition-card" id="stage">
<p class="glossary-definition-title">stage</p>
<p>Named part of a pipeline such as source, transformation, or target.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use stage for the part of a pipeline being checked.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> phase when stage is the configured term</p>
</section>

<section class="glossary-definition-card" id="target">
<p class="glossary-definition-title">target</p>
<p>Output side of a data flow.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `targets`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use target for generic output side.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> destination when target is clearer</p>
</section>

<section class="glossary-definition-card" id="transformation">
<p class="glossary-definition-title">transformation</p>
<p>Logic that changes source data into pipeline outputs.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use transformation for data-changing logic.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> mapping if broader</p>
</section>

<section class="glossary-definition-card" id="watermark">
<p class="glossary-definition-title">watermark</p>
<p>Column or value used to group or measure incremental data recency.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use watermark for incremental grouping/recency.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> timestamp only when generic</p>
</section>

</div>

## Data governance concepts

<div class="glossary-definition-list">

<section class="glossary-definition-card" id="agreement-evidence">
<p class="glossary-definition-title">agreement evidence</p>
<p>Metadata that proves which agreement context was selected, reviewed, or used.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use agreement evidence for stored agreement proof.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> agreement logs</p>
</section>

<section class="glossary-definition-card" id="approval">
<p class="glossary-definition-title">approval</p>
<p>Decision that accepts evidence, intent, or a lifecycle change.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use approval as general decision term.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> acceptance when approval is meant</p>
</section>

<section class="glossary-definition-card" id="audit">
<p class="glossary-definition-title">audit</p>
<p>Reviewable trail of evidence, decisions, and runtime outcomes.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use audit for traceability.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> logging only</p>
</section>

<section class="glossary-definition-card" id="business-meaning">
<p class="glossary-definition-title">business meaning</p>
<p>Plain-language explanation of what data represents and why it matters.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use business meaning in enrichment guidance.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> business description</p>
</section>

<section class="glossary-definition-card" id="classification">
<p class="glossary-definition-title">classification</p>
<p>Controlled label for data type, sensitivity, or governance grouping.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use classification for controlled labels.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> class label</p>
</section>

<section class="glossary-definition-card" id="data-agreement">
<p class="glossary-definition-title">data agreement</p>
<p>FabricOps agreement record that captures ownership, steward context, usage, and expectations.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `data agreements`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use data agreement for FabricOps workflow context.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> contract when agreement is meant</p>
</section>

<section class="glossary-definition-card" id="data-contract">
<p class="glossary-definition-title">data contract</p>
<p>Documented expectations for data structure, meaning, quality, ownership, and use.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use when describing formal expectations.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> informal agreement</p>
</section>

<section class="glossary-definition-card" id="data-steward">
<p class="glossary-definition-title">data steward</p>
<p>Person or role accountable for reviewing and maintaining data context and decisions.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `data stewards`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use data steward for accountable reviewer role.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> owner when stewardship is meant</p>
</section>

<section class="glossary-definition-card" id="deactivation">
<p class="glossary-definition-title">deactivation</p>
<p>Lifecycle action that makes an active rule or record inactive.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use deactivation for turning off governed intent.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> delete when record remains</p>
</section>

<section class="glossary-definition-card" id="evidence">
<p class="glossary-definition-title">evidence</p>
<p>Stored proof that a profile, decision, result, or relationship existed at a point in time.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `catalogue evidence`, `profile evidence`, `accepted catalogue profile evidence`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use evidence for reviewable proof.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> catalogue evidence in narrative docs</p>
</section>

<section class="glossary-definition-card" id="governance-review">
<p class="glossary-definition-title">governance review</p>
<p>Human review of profiles, enrichment, guardrails, agreements, and lifecycle decisions.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `governance reviews`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use governance review for reviewer workflow.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> guardrail governance</p>
</section>

<section class="glossary-definition-card" id="lifecycle">
<p class="glossary-definition-title">lifecycle</p>
<p>Sequence of states a governed record moves through from proposal to review, activation, replacement, or deactivation.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use lifecycle for governed state movement.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> status flow</p>
</section>

<section class="glossary-definition-card" id="metadata">
<p class="glossary-definition-title">metadata</p>
<p>Data that describes datasets, rules, agreements, lineage, and operations.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use metadata for descriptive and operational records.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> data about data jargon when possible</p>
</section>

<section class="glossary-definition-card" id="ownership">
<p class="glossary-definition-title">ownership</p>
<p>Accountability for a dataset, rule, agreement, or decision.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use ownership for accountability.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> owner text</p>
</section>

<section class="glossary-definition-card" id="rejection">
<p class="glossary-definition-title">rejection</p>
<p>Decision that declines evidence, intent, or a lifecycle change.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use rejection as general decision term.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> denial</p>
</section>

<section class="glossary-definition-card" id="replacement">
<p class="glossary-definition-title">replacement</p>
<p>Lifecycle action that creates a newer approved record for an older one.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use replacement for intentional succession.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> overwrite when governance state changes</p>
</section>

<section class="glossary-definition-card" id="review-history">
<p class="glossary-definition-title">review history</p>
<p>Chronological record of governance review decisions and changes.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use review history for decision chronology.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> approval history only</p>
</section>

<section class="glossary-definition-card" id="sensitivity">
<p class="glossary-definition-title">sensitivity</p>
<p>Indication of how carefully data should be handled based on risk or confidentiality.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use sensitivity for handling concern.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> PII only when specific</p>
</section>

<section class="glossary-definition-card" id="support-readiness">
<p class="glossary-definition-title">support readiness</p>
<p>State showing whether enough context exists for operations and handover.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use support readiness for handover confidence.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> operational maturity</p>
</section>

<section class="glossary-definition-card" id="usage-context">
<p class="glossary-definition-title">usage context</p>
<p>Explanation of how data is expected to be used and by whom.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use usage context in enrichment guidance.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> use case only</p>
</section>

</div>

## FabricOps concepts

<div class="glossary-definition-list">

<section class="glossary-definition-card" id="activationstate">
<p class="glossary-definition-title">activation_state</p>
<p>Metadata field that records whether a rule or record is active, inactive, or pending review.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the field name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> activation state when referring to column</p>
</section>

<section class="glossary-definition-card" id="active-pending-governance-review">
<p class="glossary-definition-title">active pending governance review</p>
<p>Activation state for a guardrail that is active but still awaiting governance review.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use when documenting rule lifecycle states.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> pending active</p>
</section>

<section class="glossary-definition-card" id="agreement-selection">
<p class="glossary-definition-title">agreement selection</p>
<p>Notebook workflow step that selects the data agreement and steward context for review or execution.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use agreement selection for the workflow step.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> contract picker</p>
</section>

<section class="glossary-definition-card" id="cancontinue">
<p class="glossary-definition-title">can_continue</p>
<p>Boolean result that tells downstream notebook code whether processing can keep running.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the returned field name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> continue flag</p>
</section>

<section class="glossary-definition-card" id="changingdata">
<p class="glossary-definition-title">changing_data</p>
<p>Profile mode for data expected to change by watermark group.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the literal mode value.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> changing data</p>
</section>

<section class="glossary-definition-card" id="enforcement">
<p class="glossary-definition-title">enforcement</p>
<p>Running active guardrails and deciding whether a pipeline can continue, warn, or stop.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `runtime enforcement`, `enforce`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use enforcement for runtime checks.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> runtime enforcement</p>
</section>

<section class="glossary-definition-card" id="enrichment">
<p class="glossary-definition-title">enrichment</p>
<p>Reviewed descriptive metadata that adds business meaning, ownership, sensitivity, classification, and usage context.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `metadata enrichment`, `enrich metadata`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use enrichment for reviewed descriptive metadata.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> metadata enrichment</p>
</section>

<section class="glossary-definition-card" id="fabricops-starter-kit">
<p class="glossary-definition-title">FabricOps Starter Kit</p>
<p>Governed, quality-checked Microsoft Fabric notebook workflows for profiling, review, guardrails, enforcement, and handover.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the public project name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> full data product platform</p>
</section>

<section class="glossary-definition-card" id="governance-approved">
<p class="glossary-definition-title">governance-approved</p>
<p>Review state showing an authorized governance reviewer approved the evidence or intent.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the literal review state.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> approved by governance</p>
</section>

<section class="glossary-definition-card" id="guardrail-result">
<p class="glossary-definition-title">guardrail result</p>
<p>Runtime outcome from evaluating a guardrail, including pass/fail/warn details.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `guardrail results`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use guardrail result/guardrail results.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> rule result</p>
</section>

<section class="glossary-definition-card" id="guardrail-target-selection">
<p class="glossary-definition-title">guardrail target selection</p>
<p>Notebook workflow step that chooses the profiled table or pipeline output whose guardrails will be reviewed.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use guardrail target selection for the workflow step.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> target picker</p>
</section>

<section class="glossary-definition-card" id="guardrails">
<p class="glossary-definition-title">guardrails</p>
<p>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `guardrail`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use guardrails for governed checks; use singular only for grammar.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> guardrail governance</p>
</section>

<section class="glossary-definition-card" id="lineage-relationship">
<p class="glossary-definition-title">lineage relationship</p>
<p>Recorded link between source data, transformations, and pipeline outputs.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use lineage relationship when documenting stored lineage.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> dependency edge</p>
</section>

<section class="glossary-definition-card" id="metadata-lakehouse">
<p class="glossary-definition-title">metadata lakehouse</p>
<p>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `metadata target`, `metadata route`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use metadata lakehouse for configured metadata storage.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> metadata target; metadata route</p>
</section>

<section class="glossary-definition-card" id="metadata-tables">
<p class="glossary-definition-title">metadata tables</p>
<p>FabricOps tables that store profiles, guardrail intent, runtime outcomes, agreements, lineage, and operating evidence.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use metadata tables for the collection.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> metadata stores</p>
</section>

<section class="glossary-definition-card" id="notebook-registry">
<p class="glossary-definition-title">notebook registry</p>
<p>Metadata inventory of notebooks and responsibilities used for handover and operating context.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use notebook registry for the inventory.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> notebook catalogue</p>
</section>

<section class="glossary-definition-card" id="notebook-template">
<p class="glossary-definition-title">notebook template</p>
<p>Reusable starter notebook workflow that shows where and how FabricOps helpers are used for a FabricOps phase such as environment setup, agreement selection, pipeline execution, governance review, or exploration.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `notebook templates`, `starter notebook`, `starter notebooks`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use notebook template for reusable starter notebook workflows.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> notebook registry when the reusable notebook file is meant</p>
</section>

<section class="glossary-definition-card" id="pipeline-output">
<p class="glossary-definition-title">pipeline output</p>
<p>A DataFrame or table produced by a pipeline and checked before publishing.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `pipeline outputs`, `output`, `target output`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use pipeline output/pipeline outputs for produced data.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> governed outputs</p>
</section>

<section class="glossary-definition-card" id="profile">
<p class="glossary-definition-title">profile</p>
<p>Reusable measurements about source data or pipeline outputs, such as schema, row count, nulls, distinct values, and distributions.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `profiles`, `profiling`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use profile/profiles for measured facts.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> profile evidence; catalogue evidence</p>
</section>

<section class="glossary-definition-card" id="profile-mode">
<p class="glossary-definition-title">profile mode</p>
<p>Configured behavior mode for profile guardrails: static_data, changing_data, or skip.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `profile behavior`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use profile mode when describing static_data/changing_data/skip.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> profile behavior mode</p>
</section>

<section class="glossary-definition-card" id="reviewstate">
<p class="glossary-definition-title">review_state</p>
<p>Metadata field that records review outcome such as self-approved or governance-approved.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the field name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> review status</p>
</section>

<section class="glossary-definition-card" id="run-summary">
<p class="glossary-definition-title">run summary</p>
<p>Concise record of a pipeline run, including status, checks, and handover signals.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `run summaries`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use run summary/run summaries.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> pipeline summary</p>
</section>

<section class="glossary-definition-card" id="self-approved">
<p class="glossary-definition-title">self-approved</p>
<p>Review state showing a rule or agreement was approved by the same operating context that proposed it.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the literal review state.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> auto approved</p>
</section>

<section class="glossary-definition-card" id="skip">
<p class="glossary-definition-title">skip</p>
<p>Profile mode that records a profile without enforcing profile behavior.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the literal mode value.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> skip enforcement</p>
</section>

<section class="glossary-definition-card" id="source-data">
<p class="glossary-definition-title">source data</p>
<p>Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `source table`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use source data for inputs readers inspect or transform.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> source table when file inputs are possible</p>
</section>

<section class="glossary-definition-card" id="staticdata">
<p class="glossary-definition-title">static_data</p>
<p>Profile mode for data expected to remain stable against an approved baseline.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the literal mode value.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> static data</p>
</section>

<section class="glossary-definition-card" id="superseded">
<p class="glossary-definition-title">superseded</p>
<p>Lifecycle state showing a newer record replaced an older record.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use superseded for replaced records.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> deprecated</p>
</section>

<section class="glossary-definition-card" id="target-dataframe">
<p class="glossary-definition-title">target DataFrame</p>
<p>The in-memory Spark DataFrame produced by pipeline logic before it is written.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use only when distinguishing in-memory Spark data from a written table.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> target output when DataFrame precision is needed</p>
</section>

<section class="glossary-definition-card" id="target-table">
<p class="glossary-definition-title">target table</p>
<p>A written table produced by a pipeline output.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `target tables`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use only for persisted table outputs.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> target DataFrame when written-table precision is needed</p>
</section>

</div>

## File and configuration concepts

<div class="glossary-definition-list">

<section class="glossary-definition-card" id="configuration">
<p class="glossary-definition-title">configuration</p>
<p>Settings that control environment targets, behavior, and helper options.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use configuration for settings.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> config in narrative docs</p>
</section>

<section class="glossary-definition-card" id="csv">
<p class="glossary-definition-title">CSV</p>
<p>Comma-separated values file format.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use CSV for the file format.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> csv in prose</p>
</section>

<section class="glossary-definition-card" id="excel">
<p class="glossary-definition-title">Excel</p>
<p>Spreadsheet workbook file format read by supported helpers.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Excel for workbook format.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> xlsx unless extension needed</p>
</section>

<section class="glossary-definition-card" id="flag">
<p class="glossary-definition-title">flag</p>
<p>Boolean or enum setting that turns behavior on, off, or into a mode.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use flag for switches.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> toggle if flag meant</p>
</section>

<section class="glossary-definition-card" id="json">
<p class="glossary-definition-title">JSON</p>
<p>Structured text format for objects and arrays.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use JSON for format.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> json in prose</p>
</section>

<section class="glossary-definition-card" id="parameter">
<p class="glossary-definition-title">parameter</p>
<p>Named input that changes helper or notebook behavior.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use parameter for inputs.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> argument when user-facing docs mean parameter</p>
</section>

<section class="glossary-definition-card" id="parquet">
<p class="glossary-definition-title">Parquet</p>
<p>Columnar file format commonly used in data lake workloads.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Parquet for file format.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> parquet in prose</p>
</section>

<section class="glossary-definition-card" id="yaml">
<p class="glossary-definition-title">YAML</p>
<p>Human-readable structured configuration format.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use YAML for format.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> yml unless extension needed</p>
</section>

</div>

## Metadata table names

<div class="glossary-definition-list">

<section class="glossary-definition-card" id="metadataagreementevidence">
<p class="glossary-definition-title">METADATA_AGREEMENT_EVIDENCE</p>
<p>Table that stores evidence linking agreement selection and review context to runs or decisions.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> agreement evidence table</p>
</section>

<section class="glossary-definition-card" id="metadatadataaccess">
<p class="glossary-definition-title">METADATA_DATA_ACCESS</p>
<p>Table that stores data access context for governed datasets.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> access table</p>
</section>

<section class="glossary-definition-card" id="metadatadataagreements">
<p class="glossary-definition-title">METADATA_DATA_AGREEMENTS</p>
<p>Table that stores data agreements and lifecycle states.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> agreements table</p>
</section>

<section class="glossary-definition-card" id="metadatadatacatalogue">
<p class="glossary-definition-title">METADATA_DATA_CATALOGUE</p>
<p>Table that stores profiles and descriptive metadata about observed datasets and pipeline outputs.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> data catalogue shorthand</p>
</section>

<section class="glossary-definition-card" id="metadatadatalineagetable">
<p class="glossary-definition-title">METADATA_DATA_LINEAGE_TABLE</p>
<p>Table that stores lineage relationships between sources, transformations, and outputs.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> lineage table</p>
</section>

<section class="glossary-definition-card" id="metadatadatastewards">
<p class="glossary-definition-title">METADATA_DATA_STEWARDS</p>
<p>Table that stores data steward records and responsibilities.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> stewards table</p>
</section>

<section class="glossary-definition-card" id="metadataenrichmentrules">
<p class="glossary-definition-title">METADATA_ENRICHMENT_RULES</p>
<p>Table that stores approved enrichment controls and allowed values.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> enrichment rules table</p>
</section>

<section class="glossary-definition-card" id="metadataguardrailresults">
<p class="glossary-definition-title">METADATA_GUARDRAIL_RESULTS</p>
<p>Table that stores runtime guardrail outcomes from pipeline enforcement.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> guardrail results table</p>
</section>

<section class="glossary-definition-card" id="metadataguardrailrules">
<p class="glossary-definition-title">METADATA_GUARDRAIL_RULES</p>
<p>Table that stores approved guardrail and data quality rule intent.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> guardrail rules table</p>
</section>

<section class="glossary-definition-card" id="metadatanotebookregistry">
<p class="glossary-definition-title">METADATA_NOTEBOOK_REGISTRY</p>
<p>Table that stores notebook registry entries for handover and operations.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> notebook registry table</p>
</section>

<section class="glossary-definition-card" id="metadatapipelineruns">
<p class="glossary-definition-title">METADATA_PIPELINE_RUNS</p>
<p>Table that stores run summaries for pipeline executions.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as literal table name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> pipeline runs table</p>
</section>

</div>

## Microsoft Fabric concepts

<div class="glossary-definition-list">

<section class="glossary-definition-card" id="delta-table">
<p class="glossary-definition-title">Delta table</p>
<p>Table stored in Delta format and read by Spark or Fabric engines.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Delta table for storage format.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> table when format matters</p>
</section>

<section class="glossary-definition-card" id="engineering-dev-workspace">
<p class="glossary-definition-title">Engineering Dev workspace</p>
<p>Workspace pattern for development engineering workflows.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as environment role name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> dev workspace if ambiguous</p>
</section>

<section class="glossary-definition-card" id="engineering-prod-workspace">
<p class="glossary-definition-title">Engineering Prod workspace</p>
<p>Workspace pattern for production engineering workflows.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as environment role name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> prod workspace if ambiguous</p>
</section>

<section class="glossary-definition-card" id="fabric-environment">
<p class="glossary-definition-title">Fabric environment</p>
<p>Named environment configuration that maps notebooks to workspace and item targets.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use for environment-specific config.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> environment alone if ambiguous</p>
</section>

<section class="glossary-definition-card" id="fabric-item-target">
<p class="glossary-definition-title">Fabric item target</p>
<p>Configured Fabric item that a helper reads from or writes to.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use when docs discuss target config generally.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> Fabric target when item precision needed</p>
</section>

<section class="glossary-definition-card" id="fabric-notebook">
<p class="glossary-definition-title">Fabric notebook</p>
<p>Notebook running in Microsoft Fabric.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Fabric notebook for notebook runtime.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> Jupyter notebook when Fabric-specific</p>
</section>

<section class="glossary-definition-card" id="files-path">
<p class="glossary-definition-title">Files path</p>
<p>Path under the Lakehouse Files area.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Files path for Lakehouse file locations.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> file path when Fabric Files matters</p>
</section>

<section class="glossary-definition-card" id="governance-workspace">
<p class="glossary-definition-title">Governance workspace</p>
<p>Workspace pattern for governance notebooks and metadata review activities.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as environment role name.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> governance area</p>
</section>

<section class="glossary-definition-card" id="lakehouse">
<p class="glossary-definition-title">Lakehouse</p>
<p>Fabric item that stores files and Delta tables for Spark workloads.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Lakehouse for Fabric item type.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> lake house</p>
</section>

<section class="glossary-definition-card" id="lakehouse-schema">
<p class="glossary-definition-title">Lakehouse schema</p>
<p>Named schema area inside a Lakehouse for organizing tables.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Lakehouse schema for schema location.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> database when Fabric schema meant</p>
</section>

<section class="glossary-definition-card" id="microsoft-fabric">
<p class="glossary-definition-title">Microsoft Fabric</p>
<p>Microsoft analytics platform used as the runtime for FabricOps notebooks and storage targets.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use full name on first mention.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> Fabric alone when ambiguous</p>
</section>

<section class="glossary-definition-card" id="notebook-session">
<p class="glossary-definition-title">notebook session</p>
<p>Running notebook execution context with installed packages and Spark resources.</p>
<p class="glossary-definition-meta"><strong>Aliases:</strong> `notebook sessions`</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use notebook session for runtime context.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> kernel when Spark context matters</p>
</section>

<section class="glossary-definition-card" id="productwarehouse">
<p class="glossary-definition-title">product_warehouse</p>
<p>Configured product Warehouse target key.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the literal config target.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> product warehouse in code context</p>
</section>

<section class="glossary-definition-card" id="sourcelakehouse">
<p class="glossary-definition-title">source_lakehouse</p>
<p>Configured source Lakehouse target key.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the literal config target.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> source lakehouse in code context</p>
</section>

<section class="glossary-definition-card" id="spark-session">
<p class="glossary-definition-title">Spark session</p>
<p>Spark execution session used by Fabric notebooks for distributed DataFrame work.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Spark session for Spark runtime object.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> spark context unless specific</p>
</section>

<section class="glossary-definition-card" id="table-path">
<p class="glossary-definition-title">table path</p>
<p>Path or identifier for a managed table location.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use table path for table locations.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> path when table context matters</p>
</section>

<section class="glossary-definition-card" id="unifiedlakehouse">
<p class="glossary-definition-title">unified_lakehouse</p>
<p>Configured unified Lakehouse target key.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use as the literal config target.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> unified lakehouse in code context</p>
</section>

<section class="glossary-definition-card" id="warehouse">
<p class="glossary-definition-title">Warehouse</p>
<p>Fabric item that provides SQL warehouse storage and querying.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use Warehouse for Fabric item type.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> SQL database when Fabric Warehouse is meant</p>
</section>

<section class="glossary-definition-card" id="wheel">
<p class="glossary-definition-title">wheel</p>
<p>Python package artifact installed into a notebook session.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use wheel for package artifact.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> whl except filename</p>
</section>

<section class="glossary-definition-card" id="workspace">
<p class="glossary-definition-title">workspace</p>
<p>Microsoft Fabric container for notebooks, Lakehouses, Warehouses, and other items.</p>
<p class="glossary-definition-meta"><strong>Preferred usage:</strong> Use workspace generically.</p>
<p class="glossary-definition-meta"><strong>Avoid usage:</strong> tenant</p>
</section>

</div>
