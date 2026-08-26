<!-- GENERATED FILE: edit docs/reference/_data/glossary.json or scripts/generate_glossary_page.py -->

# FabricOps glossary

Use this page when a FabricOps, Governance, or Engineering term is unfamiliar. Definitions come from the canonical `docs/reference/_data/glossary.json` source.

The order follows the FabricOps operating workflow so you can learn terminology close to where it appears in the Guided Demo.

<details>
<summary>
<strong>FabricOps concepts</strong><br>
<span>The small set of ideas that describe FabricOps as a governed Data Engineering practice.</span>
</summary>

<details id="fabricops-starter-kit">
<summary><strong>FabricOps Starter Kit</strong> — A plug-and-play Data Engineering and Governance practice for Microsoft Fabric.</summary>
<p>A plug-and-play Data Engineering and Governance practice for Microsoft Fabric, implemented through a planned operating workflow, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model.</p>
</details>

<details id="metadata">
<summary><strong>Metadata</strong> — Information about the data.</summary>
<p>Metadata is information about the data. In FabricOps this includes its structure, Profile, ownership, business meaning, sensitivity, Guardrails, lineage, Data Agreement, Data Contract, and other information used to understand and govern it.</p>
</details>

<details id="governance-as-code">
<summary><strong>Governance as Code</strong> — Defining governance rules in a structured, version-controlled form that can be applied consistently.</summary>
<p>Governance as Code means defining governance rules in a structured, version-controlled way so they can be reviewed, repeated, and applied consistently by FabricOps. This can include Guardrails, data quality rules, sensitivity and PII requirements, access rules, approvals, governance states, and other policies that can be expressed as configuration or executable checks.</p>
<p><strong>Also known as:</strong> policy as code</p>
</details>

<details id="configuration-driven-engineering">
<summary><strong>Configuration-driven Engineering</strong> — Controlling repeatable engineering behaviour through configuration instead of rewriting pipeline code.</summary>
<p>Configuration-driven Engineering means defining reusable pipeline behaviour through configuration so teams can change settings, targets, strategies, and governed parameters without duplicating or rewriting the underlying engineering logic.</p>
<p><strong>Also known as:</strong> config-driven engineering</p>
</details>

</details>

<details>
<summary>
<strong>Governance concepts</strong><br>
<span>Terms encountered as Governance establishes ownership, expectations, rules, controls, and Production approval.</span>
</summary>

<details id="data-steward">
<summary><strong>Data Steward</strong> — The person or role responsible for reviewing and maintaining the governance context for data.</summary>
<p>A Data Steward is the person or role responsible for reviewing and maintaining the governance context for data, including its meaning, ownership, sensitivity, intended use, and governance decisions.</p>
<p><strong>Also known as:</strong> data stewards</p>
</details>

<details id="data-agreement">
<summary><strong>Data Agreement</strong> — The governed record that establishes who is sharing what data, with whom, and why.</summary>
<p>A Data Agreement establishes the governed context for a dataset before engineering proceeds. It captures the parties involved, steward context, intended use, and expectations that guide the FabricOps workflow.</p>
<p><strong>Also known as:</strong> data agreements</p>
</details>

<details id="enrichment">
<summary><strong>Enrichment</strong> — Business and governance information added to the Data Catalogue after technical metadata has been captured.</summary>
<p>Enrichment is the business and governance information added to the Data Catalogue after the technical metadata has been captured. It includes descriptions, ownership, sensitivity, classification, and how the data is intended to be used.</p>
<p><strong>Also known as:</strong> metadata enrichment, enrich metadata</p>
</details>

<details id="data-sensitivity">
<summary><strong>Data Sensitivity</strong> — How carefully data should be handled based on its confidentiality or risk.</summary>
<p>Data Sensitivity describes how carefully data should be handled based on confidentiality, privacy, business risk, or regulatory requirements. It can influence access, masking, sharing, and other governance controls.</p>
<p><strong>Also known as:</strong> sensitivity</p>
</details>

<details id="pii">
<summary><strong>PII</strong> — Data that can identify or be linked to an individual.</summary>
<p>PII, or personally identifiable information, is data that can identify or be linked to an individual. In a governed workflow it may require additional controls such as restricted access, masking, or stricter handling.</p>
<p><strong>Also known as:</strong> personally identifiable information</p>
</details>

<details id="data-access">
<summary><strong>Data Access</strong> — The governed definition of who is allowed to access data and under what conditions.</summary>
<p>Data Access describes who is allowed to access governed data and the conditions or restrictions that apply. It provides the governance context that can be implemented through platform security controls such as RLS, OLS, permissions, or other access mechanisms.</p>
</details>

<details id="data-quality">
<summary><strong>Data Quality</strong> — Whether data meets the expectations required for its intended use.</summary>
<p>Data Quality describes whether data meets expected rules for things such as completeness, validity, consistency, uniqueness, accuracy, and other requirements needed for its intended use.</p>
<p><strong>Also known as:</strong> DQ</p>
</details>

<details id="guardrails">
<summary><strong>Guardrails</strong> — Governed rules FabricOps applies to data and pipelines.</summary>
<p>Guardrails are the governed rules FabricOps applies to data and pipelines. Today, they can check schema, freshness, profile behaviour, change over time, and data quality. In future they can also cover governance requirements such as stricter handling for sensitive data, masking or restricted access for PII, and additional controls for specific classifications.</p>
<p><strong>Also known as:</strong> guardrail</p>
</details>

<details id="enforcement">
<summary><strong>Enforcement</strong> — Applying active Guardrails during a pipeline run and acting on the result.</summary>
<p>Enforcement is when FabricOps applies the active Guardrails during a pipeline run and acts on the result. Depending on the Guardrail, the pipeline can continue, continue with a warning, or stop.</p>
<p><strong>Also known as:</strong> runtime enforcement, enforce</p>
</details>

<details id="guardrail-result">
<summary><strong>Guardrail Result</strong> — The recorded outcome after FabricOps evaluates a Guardrail during a pipeline run.</summary>
<p>A Guardrail Result is the recorded outcome after FabricOps evaluates a Guardrail during a pipeline run. It records whether the check passed, warned, or failed, what was checked, and whether the pipeline is allowed to continue.</p>
<p><strong>Also known as:</strong> guardrail results</p>
</details>

<details id="data-contract">
<summary><strong>Data Contract</strong> — The approved definition of what is expected from governed Production data.</summary>
<p>A Data Contract is the approved definition of the structure, meaning, quality expectations, ownership, processing expectations, and governance requirements for governed Production data.</p>
<p><strong>Also known as:</strong> data contracts</p>
</details>

<details id="access-control">
<summary><strong>Access Control</strong> — The rules and mechanisms that determine who can access data or system resources.</summary>
<p>Access Control is the broader set of rules and mechanisms used to decide who can access datasets, tables, columns, workspaces, files, or other resources and what actions they are allowed to perform.</p>
</details>

<details id="row-level-security">
<summary><strong>Row-Level Security (RLS)</strong> — A security method that controls which rows of data a user can see.</summary>
<p>Row-Level Security limits the rows returned to a user based on identity, role, or access rules while allowing the same table or model to serve different audiences.</p>
<p><strong>Also known as:</strong> RLS</p>
</details>

<details id="object-level-security">
<summary><strong>Object-Level Security (OLS)</strong> — A security method that controls whether a user can see specific tables or columns.</summary>
<p>Object-Level Security restricts access to specific data objects, such as tables or columns, so unauthorized users cannot see those objects even when they can access the wider model or dataset.</p>
<p><strong>Also known as:</strong> OLS</p>
</details>

</details>

<details>
<summary>
<strong>Engineering concepts</strong><br>
<span>Terms encountered as Engineering sets up Fabric, builds pipelines, profiles data, and applies governed processing.</span>
</summary>

<details id="microsoft-fabric">
<summary><strong>Microsoft Fabric</strong> — Microsoft's analytics platform used as the runtime for FabricOps.</summary>
<p>Microsoft Fabric is the analytics platform FabricOps runs on, providing workspaces, Lakehouses, Warehouses, notebooks, Spark, SQL, and other data capabilities.</p>
</details>

<details id="workspace">
<summary><strong>Workspace</strong> — A Microsoft Fabric container for related data and analytics items.</summary>
<p>A Workspace is a Microsoft Fabric container used to organize and secure related items such as notebooks, Lakehouses, Warehouses, semantic models, and reports.</p>
<p><strong>Also known as:</strong> workspaces</p>
</details>

<details id="lakehouse">
<summary><strong>Lakehouse</strong> — A Fabric data store that combines data-lake storage with managed tables for analytics and Spark workloads.</summary>
<p>A Lakehouse in Microsoft Fabric stores files and managed Delta tables in OneLake and is commonly used with Spark, notebooks, and SQL analytics endpoints.</p>
<p><strong>Also known as:</strong> Lakehouses</p>
</details>

<details id="warehouse">
<summary><strong>Warehouse</strong> — A Fabric relational data store designed for SQL analytics and warehousing workloads.</summary>
<p>A Warehouse in Microsoft Fabric provides relational tables and SQL-based querying for structured analytics and data warehousing workloads.</p>
<p><strong>Also known as:</strong> Warehouses</p>
</details>

<details id="notebook">
<summary><strong>Notebook</strong> — An interactive Fabric document for running code, data processing, analysis, and engineering workflows.</summary>
<p>A Notebook is an interactive Microsoft Fabric document where users can run Python, PySpark, SQL, and other supported code for data engineering, analysis, experimentation, and operational workflows.</p>
<p><strong>Also known as:</strong> notebooks, Fabric notebook</p>
</details>

<details id="configuration">
<summary><strong>Configuration</strong> — Settings that define how FabricOps or a pipeline should behave without changing the underlying code.</summary>
<p>Configuration is the set of named settings used to control environment targets, processing choices, rules, parameters, and other behaviour without rewriting the implementation.</p>
<p><strong>Also known as:</strong> config</p>
</details>

<details id="pipeline">
<summary><strong>Pipeline</strong> — A sequence of steps that moves, transforms, checks, and writes data.</summary>
<p>A Pipeline is a repeatable sequence of data-processing steps that can read source data, transform it, apply checks, and write results to a target.</p>
<p><strong>Also known as:</strong> pipelines</p>
</details>

<details id="pyspark">
<summary><strong>PySpark</strong> — The Python API for Apache Spark.</summary>
<p>PySpark lets Python code use Apache Spark to process data across a distributed compute engine. It is commonly used in Fabric notebooks for large-scale transformations and data engineering.</p>
</details>

<details id="profile">
<summary><strong>Profile</strong> — A summary of the data at a point in time.</summary>
<p>A Profile is a summary of the data at a point in time. It shows things like row count, columns, data types, nulls, distinct values, minimum and maximum values, and value distributions. In FabricOps, this is stored in Data Profiled and Data Profiled Frequency metadata.</p>
<p><strong>Also known as:</strong> profiles, profiling</p>
</details>

<details id="schema">
<summary><strong>Schema</strong> — The defined structure of data, including its columns and data types.</summary>
<p>A Schema describes the structure of a dataset or table, including column names, data types, and other structural expectations.</p>
<p><strong>Also known as:</strong> schemas</p>
</details>

<details id="full-dataset">
<summary><strong>Full Dataset</strong> — A source processing strategy that reads the complete physical source dataset for every run.</summary>
<p>A source processing strategy that reads the complete physical source dataset for every run.</p>
</details>

<details id="incremental-watermark">
<summary><strong>Incremental Watermark</strong> — A source processing strategy that uses a checkpoint column to process rows newer than the last successfully committed watermark.</summary>
<p>A source processing strategy that uses a non-null, strictly increasing, globally unique checkpoint column to process rows newer than the last successfully committed watermark.</p>
<p><strong>Also known as:</strong> watermark-based incremental loading</p>
</details>

<details id="incremental-partition">
<summary><strong>Incremental Partition</strong> — A source processing strategy that processes whole logical data buckets, such as days, months, or snapshots, when those buckets are new or changed.</summary>
<p>A source processing strategy that processes whole logical data buckets, such as days, months, or snapshots, when those buckets are new or changed.</p>
<p><strong>Also known as:</strong> partition-based incremental loading</p>
</details>

<details id="incremental-subset">
<summary><strong>Incremental Subset</strong> — The runtime read mode used when FabricOps determines that only part of the source needs to be processed for the current run.</summary>
<p>The runtime read mode used when FabricOps determines that only part of the source needs to be processed for the current run.</p>
</details>

<details id="watermark">
<summary><strong>Watermark</strong> — A checkpoint value that records how far a successful incremental source load has processed.</summary>
<p>A strictly increasing, globally unique checkpoint value that records how far a successful incremental source load has processed.</p>
</details>

<details id="parallel-processing">
<summary><strong>Parallel Processing</strong> — Processing multiple parts of a workload at the same time.</summary>
<p>Parallel Processing divides work so multiple tasks or data partitions can be processed at the same time, which can reduce elapsed processing time when the workload and compute resources support it.</p>
</details>

<details id="data-modelling">
<summary><strong>Data Modelling</strong> — Organizing data structures and relationships so data can be stored, understood, and used effectively.</summary>
<p>Data Modelling is the practice of designing tables, fields, keys, relationships, and structures so data supports its intended analytical, operational, or reporting use.</p>
<p><strong>Also known as:</strong> data modeling</p>
</details>

<details id="partition">
<summary><strong>Partition</strong> — A logical data bucket such as a day, month, or snapshot that can be processed or reprocessed as a whole.</summary>
<p>A logical data bucket such as a day, month, or snapshot that can be processed or reprocessed as a whole.</p>
</details>

<details id="physical-partitioning">
<summary><strong>Physical Partitioning</strong> — How a Lakehouse table is physically organized for storage and pruning. This is separate from FabricOps incremental partition source processing.</summary>
<p>How a Lakehouse table is physically organized for storage and pruning. This is separate from FabricOps incremental partition source processing.</p>
<p><strong>Also known as:</strong> partition_by</p>
</details>

<details id="append">
<summary><strong>Append</strong> — A write strategy that adds new rows without replacing existing rows.</summary>
<p>Append adds new rows to an existing target while leaving existing rows unchanged. It is appropriate only when incoming data is additive and existing records do not need to be changed or removed.</p>
</details>

<details id="overwrite">
<summary><strong>Overwrite</strong> — A write strategy that replaces existing target data.</summary>
<p>Overwrite replaces existing target data with the newly prepared data. Depending on the implementation, it can replace a whole table or only a governed partition scope.</p>
</details>

<details id="slowly-changing-dimensions">
<summary><strong>Slowly Changing Dimensions (SCD)</strong> — Patterns for handling changes to descriptive records over time.</summary>
<p>Slowly Changing Dimensions are data-modelling patterns for handling changes to descriptive records. Common approaches include SCD Type 1, which replaces the previous value, and SCD Type 2, which keeps history by creating versioned records.</p>
<p><strong>Also known as:</strong> SCD, slowly changing dimension</p>
</details>

</details>
