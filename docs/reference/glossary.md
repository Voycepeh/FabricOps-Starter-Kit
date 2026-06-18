# FabricOps glossary

Searchable source of truth for FabricOps documentation wording and inline glossary chips.

## Data engineering concepts

### append

Write mode that adds rows to existing data.

**Preferred usage:** Use append for write mode.

**Avoid usage:** add when mode meant

### dashboard

Visual summary of metrics, status, or review evidence.

**Preferred usage:** Use dashboard for visual summary.

**Avoid usage:** report when dashboard meant

### data quality rule

Executable expectation that checks data values, completeness, or relationships.

**Aliases:** `DQ rule`, `DQ rules`

**Preferred usage:** Use data quality rule in narrative; DQ rule after introduced.

**Avoid usage:** rule when ambiguous

### DataFrame

Spark tabular data structure held in memory during processing.

**Aliases:** `DataFrames`

**Preferred usage:** Use DataFrame for Spark object.

**Avoid usage:** data frame

### deterministic logic

Logic that produces the same result for the same inputs.

**Preferred usage:** Use deterministic logic for reproducible behavior.

**Avoid usage:** AI-generated logic when deterministic matters

### distinct value

Unique value observed in a column.

**Preferred usage:** Use distinct value/distinct values.

**Avoid usage:** unique value when DQ unique rule meant

### distribution

Shape or frequency of values in data.

**Preferred usage:** Use distribution for value spread.

**Avoid usage:** profile summary when distribution meant

### DQ

Short form of data quality.

**Preferred usage:** Use DQ only after data quality is clear.

**Avoid usage:** quality only when ambiguous

### freshness

Measure of whether data is recent enough for its expected use.

**Preferred usage:** Use freshness for recency checks.

**Avoid usage:** timeliness when check is freshness

### lineage

Trace of how data moves from sources through transformations to targets.

**Preferred usage:** Use lineage for data movement trace.

**Avoid usage:** dependency list when lineage meant

### null

Missing or unknown value in a column.

**Preferred usage:** Use null for missing values.

**Avoid usage:** blank when null meant

### overwrite

Write mode that replaces existing data.

**Preferred usage:** Use overwrite for write mode.

**Avoid usage:** replace when write mode meant

### partitioning

Organizing data into partitions for storage or processing.

**Preferred usage:** Use partitioning for partition design.

**Avoid usage:** sharding

### pipeline

Sequence of steps that reads source data, transforms it, checks it, and writes outputs.

**Aliases:** `pipelines`

**Preferred usage:** Use pipeline for end-to-end processing.

**Avoid usage:** workflow if processing pipeline meant

### repartitioning

Changing DataFrame partitions before processing or writing.

**Preferred usage:** Use repartitioning for Spark partition changes.

**Avoid usage:** partitioning when action is repartition

### row count

Number of rows in a DataFrame or table.

**Preferred usage:** Use row count for counts.

**Avoid usage:** records when exact rows meant

### runtime

Execution period and environment where notebook or pipeline code runs.

**Preferred usage:** Use runtime for execution context.

**Avoid usage:** run time unless prose needs it

### schema

Column names and data types for a DataFrame or table.

**Preferred usage:** Use schema for structure.

**Avoid usage:** layout when schema is meant

### source

Input side of a data flow.

**Aliases:** `sources`

**Preferred usage:** Use source for generic input side.

**Avoid usage:** upstream when source is clearer

### stage

Named part of a pipeline such as source, transformation, or target.

**Preferred usage:** Use stage for the part of a pipeline being checked.

**Avoid usage:** phase when stage is the configured term

### target

Output side of a data flow.

**Aliases:** `targets`

**Preferred usage:** Use target for generic output side.

**Avoid usage:** destination when target is clearer

### transformation

Logic that changes source data into pipeline outputs.

**Preferred usage:** Use transformation for data-changing logic.

**Avoid usage:** mapping if broader

### watermark

Column or value used to group or measure incremental data recency.

**Preferred usage:** Use watermark for incremental grouping/recency.

**Avoid usage:** timestamp only when generic

## Data governance concepts

### agreement evidence

Metadata that proves which agreement context was selected, reviewed, or used.

**Preferred usage:** Use agreement evidence for stored agreement proof.

**Avoid usage:** agreement logs

### approval

Decision that accepts evidence, intent, or a lifecycle change.

**Preferred usage:** Use approval as general decision term.

**Avoid usage:** acceptance when approval is meant

### audit

Reviewable trail of evidence, decisions, and runtime outcomes.

**Preferred usage:** Use audit for traceability.

**Avoid usage:** logging only

### business meaning

Plain-language explanation of what data represents and why it matters.

**Preferred usage:** Use business meaning in enrichment guidance.

**Avoid usage:** business description

### classification

Controlled label for data type, sensitivity, or governance grouping.

**Preferred usage:** Use classification for controlled labels.

**Avoid usage:** class label

### data agreement

FabricOps agreement record that captures ownership, steward context, usage, and expectations.

**Aliases:** `data agreements`

**Preferred usage:** Use data agreement for FabricOps workflow context.

**Avoid usage:** contract when agreement is meant

### data contract

Documented expectations for data structure, meaning, quality, ownership, and use.

**Preferred usage:** Use when describing formal expectations.

**Avoid usage:** informal agreement

### data steward

Person or role accountable for reviewing and maintaining data context and decisions.

**Aliases:** `data stewards`

**Preferred usage:** Use data steward for accountable reviewer role.

**Avoid usage:** owner when stewardship is meant

### deactivation

Lifecycle action that makes an active rule or record inactive.

**Preferred usage:** Use deactivation for turning off governed intent.

**Avoid usage:** delete when record remains

### evidence

Stored proof that a profile, decision, result, or relationship existed at a point in time.

**Aliases:** `catalogue evidence`, `profile evidence`, `accepted catalogue profile evidence`

**Preferred usage:** Use evidence for reviewable proof.

**Avoid usage:** catalogue evidence in narrative docs

### governance review

Human review of profiles, enrichment, guardrails, agreements, and lifecycle decisions.

**Aliases:** `governance reviews`

**Preferred usage:** Use governance review for reviewer workflow.

**Avoid usage:** guardrail governance

### lifecycle

Sequence of states a governed record moves through from proposal to review, activation, replacement, or deactivation.

**Preferred usage:** Use lifecycle for governed state movement.

**Avoid usage:** status flow

### metadata

Data that describes datasets, rules, agreements, lineage, and operations.

**Preferred usage:** Use metadata for descriptive and operational records.

**Avoid usage:** data about data jargon when possible

### ownership

Accountability for a dataset, rule, agreement, or decision.

**Preferred usage:** Use ownership for accountability.

**Avoid usage:** owner text

### rejection

Decision that declines evidence, intent, or a lifecycle change.

**Preferred usage:** Use rejection as general decision term.

**Avoid usage:** denial

### replacement

Lifecycle action that creates a newer approved record for an older one.

**Preferred usage:** Use replacement for intentional succession.

**Avoid usage:** overwrite when governance state changes

### review history

Chronological record of governance review decisions and changes.

**Preferred usage:** Use review history for decision chronology.

**Avoid usage:** approval history only

### sensitivity

Indication of how carefully data should be handled based on risk or confidentiality.

**Preferred usage:** Use sensitivity for handling concern.

**Avoid usage:** PII only when specific

### support readiness

State showing whether enough context exists for operations and handover.

**Preferred usage:** Use support readiness for handover confidence.

**Avoid usage:** operational maturity

### usage context

Explanation of how data is expected to be used and by whom.

**Preferred usage:** Use usage context in enrichment guidance.

**Avoid usage:** use case only

## FabricOps concepts

### activation_state

Metadata field that records whether a rule or record is active, inactive, or pending review.

**Preferred usage:** Use as the field name.

**Avoid usage:** activation state when referring to column

### active pending governance review

Activation state for a guardrail that is active but still awaiting governance review.

**Preferred usage:** Use when documenting rule lifecycle states.

**Avoid usage:** pending active

### agreement selection

Notebook workflow step that selects the data agreement and steward context for review or execution.

**Preferred usage:** Use agreement selection for the workflow step.

**Avoid usage:** contract picker

### can_continue

Boolean result that tells downstream notebook code whether processing can keep running.

**Preferred usage:** Use as the returned field name.

**Avoid usage:** continue flag

### changing_data

Profile mode for data expected to change by watermark group.

**Preferred usage:** Use as the literal mode value.

**Avoid usage:** changing data

### enforcement

Running active guardrails and deciding whether a pipeline can continue, warn, or stop.

**Aliases:** `runtime enforcement`, `enforce`

**Preferred usage:** Use enforcement for runtime checks.

**Avoid usage:** runtime enforcement

### enrichment

Reviewed descriptive metadata that adds business meaning, ownership, sensitivity, classification, and usage context.

**Aliases:** `metadata enrichment`, `enrich metadata`

**Preferred usage:** Use enrichment for reviewed descriptive metadata.

**Avoid usage:** metadata enrichment

### FabricOps Starter Kit

Governed, quality-checked Microsoft Fabric notebook workflows for profiling, review, guardrails, enforcement, and handover.

**Preferred usage:** Use as the public project name.

**Avoid usage:** full data product platform

### governance-approved

Review state showing an authorized governance reviewer approved the evidence or intent.

**Preferred usage:** Use as the literal review state.

**Avoid usage:** approved by governance

### guardrail result

Runtime outcome from evaluating a guardrail, including pass/fail/warn details.

**Aliases:** `guardrail results`

**Preferred usage:** Use guardrail result/guardrail results.

**Avoid usage:** rule result

### guardrail target selection

Notebook workflow step that chooses the profiled table or pipeline output whose guardrails will be reviewed.

**Preferred usage:** Use guardrail target selection for the workflow step.

**Avoid usage:** target picker

### guardrails

Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.

**Aliases:** `guardrail`

**Preferred usage:** Use guardrails for governed checks; use singular only for grammar.

**Avoid usage:** guardrail governance

### lineage relationship

Recorded link between source data, transformations, and pipeline outputs.

**Preferred usage:** Use lineage relationship when documenting stored lineage.

**Avoid usage:** dependency edge

### metadata lakehouse

Configured Fabric Lakehouse target where FabricOps stores metadata tables.

**Aliases:** `metadata target`, `metadata route`

**Preferred usage:** Use metadata lakehouse for configured metadata storage.

**Avoid usage:** metadata target; metadata route

### metadata tables

FabricOps tables that store profiles, guardrail intent, runtime outcomes, agreements, lineage, and operating evidence.

**Preferred usage:** Use metadata tables for the collection.

**Avoid usage:** metadata stores

### notebook registry

Metadata inventory of notebooks and responsibilities used for handover and operating context.

**Aliases:** `notebook template`

**Preferred usage:** Use notebook registry for the inventory.

**Avoid usage:** notebook catalogue

### pipeline output

A DataFrame or table produced by a pipeline and checked before publishing.

**Aliases:** `pipeline outputs`, `output`, `target output`

**Preferred usage:** Use pipeline output/pipeline outputs for produced data.

**Avoid usage:** governed outputs

### profile

Reusable measurements about source data or pipeline outputs, such as schema, row count, nulls, distinct values, and distributions.

**Aliases:** `profiles`, `profiling`

**Preferred usage:** Use profile/profiles for measured facts.

**Avoid usage:** profile evidence; catalogue evidence

### profile mode

Configured behavior mode for profile guardrails: static_data, changing_data, or skip.

**Aliases:** `profile behavior`

**Preferred usage:** Use profile mode when describing static_data/changing_data/skip.

**Avoid usage:** profile behavior mode

### review_state

Metadata field that records review outcome such as self-approved or governance-approved.

**Preferred usage:** Use as the field name.

**Avoid usage:** review status

### run summary

Concise record of a pipeline run, including status, checks, and handover signals.

**Aliases:** `run summaries`

**Preferred usage:** Use run summary/run summaries.

**Avoid usage:** pipeline summary

### self-approved

Review state showing a rule or agreement was approved by the same operating context that proposed it.

**Preferred usage:** Use as the literal review state.

**Avoid usage:** auto approved

### skip

Profile mode that records a profile without enforcing profile behavior.

**Preferred usage:** Use as the literal mode value.

**Avoid usage:** skip enforcement

### source data

Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.

**Aliases:** `source table`

**Preferred usage:** Use source data for inputs readers inspect or transform.

**Avoid usage:** source table when file inputs are possible

### static_data

Profile mode for data expected to remain stable against an approved baseline.

**Preferred usage:** Use as the literal mode value.

**Avoid usage:** static data

### superseded

Lifecycle state showing a newer record replaced an older record.

**Preferred usage:** Use superseded for replaced records.

**Avoid usage:** deprecated

### target DataFrame

The in-memory Spark DataFrame produced by pipeline logic before it is written.

**Preferred usage:** Use only when distinguishing in-memory Spark data from a written table.

**Avoid usage:** target output when DataFrame precision is needed

### target table

A written table produced by a pipeline output.

**Aliases:** `target tables`

**Preferred usage:** Use only for persisted table outputs.

**Avoid usage:** target DataFrame when written-table precision is needed

## File and configuration concepts

### configuration

Settings that control environment targets, behavior, and helper options.

**Preferred usage:** Use configuration for settings.

**Avoid usage:** config in narrative docs

### CSV

Comma-separated values file format.

**Preferred usage:** Use CSV for the file format.

**Avoid usage:** csv in prose

### Excel

Spreadsheet workbook file format read by supported helpers.

**Preferred usage:** Use Excel for workbook format.

**Avoid usage:** xlsx unless extension needed

### flag

Boolean or enum setting that turns behavior on, off, or into a mode.

**Preferred usage:** Use flag for switches.

**Avoid usage:** toggle if flag meant

### JSON

Structured text format for objects and arrays.

**Preferred usage:** Use JSON for format.

**Avoid usage:** json in prose

### parameter

Named input that changes helper or notebook behavior.

**Preferred usage:** Use parameter for inputs.

**Avoid usage:** argument when user-facing docs mean parameter

### Parquet

Columnar file format commonly used in data lake workloads.

**Preferred usage:** Use Parquet for file format.

**Avoid usage:** parquet in prose

### YAML

Human-readable structured configuration format.

**Preferred usage:** Use YAML for format.

**Avoid usage:** yml unless extension needed

## Metadata table names

### METADATA_AGREEMENT_EVIDENCE

Table that stores evidence linking agreement selection and review context to runs or decisions.

**Preferred usage:** Use as literal table name.

**Avoid usage:** agreement evidence table

### METADATA_DATA_ACCESS

Table that stores data access context for governed datasets.

**Preferred usage:** Use as literal table name.

**Avoid usage:** access table

### METADATA_DATA_AGREEMENTS

Table that stores data agreements and lifecycle states.

**Preferred usage:** Use as literal table name.

**Avoid usage:** agreements table

### METADATA_DATA_CATALOGUE

Table that stores profiles and descriptive metadata about observed datasets and pipeline outputs.

**Preferred usage:** Use as literal table name.

**Avoid usage:** data catalogue shorthand

### METADATA_DATA_LINEAGE_TABLE

Table that stores lineage relationships between sources, transformations, and outputs.

**Preferred usage:** Use as literal table name.

**Avoid usage:** lineage table

### METADATA_DATA_STEWARDS

Table that stores data steward records and responsibilities.

**Preferred usage:** Use as literal table name.

**Avoid usage:** stewards table

### METADATA_ENRICHMENT_RULES

Table that stores approved enrichment controls and allowed values.

**Preferred usage:** Use as literal table name.

**Avoid usage:** enrichment rules table

### METADATA_GUARDRAIL_RESULTS

Table that stores runtime guardrail outcomes from pipeline enforcement.

**Preferred usage:** Use as literal table name.

**Avoid usage:** guardrail results table

### METADATA_GUARDRAIL_RULES

Table that stores approved guardrail and data quality rule intent.

**Preferred usage:** Use as literal table name.

**Avoid usage:** guardrail rules table

### METADATA_NOTEBOOK_REGISTRY

Table that stores notebook registry entries for handover and operations.

**Preferred usage:** Use as literal table name.

**Avoid usage:** notebook registry table

### METADATA_PIPELINE_RUNS

Table that stores run summaries for pipeline executions.

**Preferred usage:** Use as literal table name.

**Avoid usage:** pipeline runs table

## Microsoft Fabric concepts

### Delta table

Table stored in Delta format and read by Spark or Fabric engines.

**Preferred usage:** Use Delta table for storage format.

**Avoid usage:** table when format matters

### Engineering Dev workspace

Workspace pattern for development engineering workflows.

**Preferred usage:** Use as environment role name.

**Avoid usage:** dev workspace if ambiguous

### Engineering Prod workspace

Workspace pattern for production engineering workflows.

**Preferred usage:** Use as environment role name.

**Avoid usage:** prod workspace if ambiguous

### Fabric environment

Named environment configuration that maps notebooks to workspace and item targets.

**Preferred usage:** Use for environment-specific config.

**Avoid usage:** environment alone if ambiguous

### Fabric item target

Configured Fabric item that a helper reads from or writes to.

**Preferred usage:** Use when docs discuss target config generally.

**Avoid usage:** Fabric target when item precision needed

### Fabric notebook

Notebook running in Microsoft Fabric.

**Preferred usage:** Use Fabric notebook for notebook runtime.

**Avoid usage:** Jupyter notebook when Fabric-specific

### Files path

Path under the Lakehouse Files area.

**Preferred usage:** Use Files path for Lakehouse file locations.

**Avoid usage:** file path when Fabric Files matters

### Governance workspace

Workspace pattern for governance notebooks and metadata review activities.

**Preferred usage:** Use as environment role name.

**Avoid usage:** governance area

### Lakehouse

Fabric item that stores files and Delta tables for Spark workloads.

**Preferred usage:** Use Lakehouse for Fabric item type.

**Avoid usage:** lake house

### Lakehouse schema

Named schema area inside a Lakehouse for organizing tables.

**Preferred usage:** Use Lakehouse schema for schema location.

**Avoid usage:** database when Fabric schema meant

### Microsoft Fabric

Microsoft analytics platform used as the runtime for FabricOps notebooks and storage targets.

**Preferred usage:** Use full name on first mention.

**Avoid usage:** Fabric alone when ambiguous

### notebook session

Running notebook execution context with installed packages and Spark resources.

**Aliases:** `notebook sessions`

**Preferred usage:** Use notebook session for runtime context.

**Avoid usage:** kernel when Spark context matters

### product_warehouse

Configured product Warehouse target key.

**Preferred usage:** Use as the literal config target.

**Avoid usage:** product warehouse in code context

### source_lakehouse

Configured source Lakehouse target key.

**Preferred usage:** Use as the literal config target.

**Avoid usage:** source lakehouse in code context

### Spark session

Spark execution session used by Fabric notebooks for distributed DataFrame work.

**Preferred usage:** Use Spark session for Spark runtime object.

**Avoid usage:** spark context unless specific

### table path

Path or identifier for a managed table location.

**Preferred usage:** Use table path for table locations.

**Avoid usage:** path when table context matters

### unified_lakehouse

Configured unified Lakehouse target key.

**Preferred usage:** Use as the literal config target.

**Avoid usage:** unified lakehouse in code context

### Warehouse

Fabric item that provides SQL warehouse storage and querying.

**Preferred usage:** Use Warehouse for Fabric item type.

**Avoid usage:** SQL database when Fabric Warehouse is meant

### wheel

Python package artifact installed into a notebook session.

**Preferred usage:** Use wheel for package artifact.

**Avoid usage:** whl except filename

### workspace

Microsoft Fabric container for notebooks, Lakehouses, Warehouses, and other items.

**Preferred usage:** Use workspace generically.

**Avoid usage:** tenant
