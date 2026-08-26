<!-- GENERATED FILE: edit docs/reference/_data/glossary.json or scripts/generate_glossary_page.py -->

# FabricOps glossary

This glossary is the canonical terminology source for FabricOps documentation. When a term is repeated elsewhere in the repository, its meaning should come from `docs/reference/_data/glossary.json` rather than being independently redefined.

Terms are grouped by where their meaning comes from: FabricOps, Microsoft Fabric, Data Governance, or Data Engineering.

<details>
<summary>
<strong>FabricOps concepts</strong><br>
<span>Terms that describe how FabricOps implements its governed engineering practice. These definitions are the FabricOps meaning used throughout this repository.</span>
</summary>

<details id="fabricops-starter-kit">
<summary><strong>FabricOps Starter Kit</strong> — A governed Data Engineering and Data Governance practice for Microsoft Fabric.</summary>
<p>FabricOps Starter Kit is a governed Data Engineering and Data Governance practice for Microsoft Fabric, implemented through an operating workflow, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model.</p>
</details>

<details id="data-agreement">
<summary><strong>Data Agreement</strong> — A governed agreement between a provider Data Steward and a recipient Data Steward that defines why data is shared, its approved uses, and the conditions that apply.</summary>
<p>In FabricOps, a Data Agreement is a versioned governance record between two distinct active Data Stewards: one provider and one recipient. It records the business purpose, approved usages, validity period, supporting documents, and other governance context that establishes the sharing relationship before governed tables are contracted.</p>
<p><strong>Also known as:</strong> data agreements</p>
</details>

<details id="data-contract">
<summary><strong>Data Contract</strong> — A versioned definition of the guarantees and expectations for one governed table that downstream consumers can depend on.</summary>
<p>In FabricOps, a Data Contract is tied to one governed table_id and one exact Data Agreement version. Each immutable contract version freezes the table identity and schema, processing definition, current enrichment, active Guardrails, approved usages, and the relevant Agreement and Data Steward context so consumers have a stable definition of what to expect from that table.</p>
<p><strong>Also known as:</strong> data contracts</p>
</details>

<details id="enrichment">
<summary><strong>Enrichment</strong> — Business and governance information added to the Data Catalogue after technical metadata has been captured.</summary>
<p>In FabricOps, Enrichment adds business and governance meaning to Data Catalogue metadata after technical metadata has been captured. It can add descriptions, ownership, sensitivity, classification, and other table- or column-level information used to understand and govern the data.</p>
<p><strong>Also known as:</strong> metadata enrichment, enrich metadata</p>
</details>

<details id="guardrails">
<summary><strong>Guardrails</strong> — Governed rules that FabricOps evaluates against data and pipeline behaviour.</summary>
<p>In FabricOps, Guardrails are versioned governed rules associated with a table or column. Active Guardrails can express expectations such as schema, freshness, profile behaviour, change behaviour, and data quality, and are evaluated during governed pipeline execution.</p>
<p><strong>Also known as:</strong> guardrail</p>
</details>

<details id="enforcement">
<summary><strong>Enforcement</strong> — Applying active Guardrails during a pipeline run and acting on the result.</summary>
<p>In FabricOps, Enforcement is the runtime application of active Guardrails. Depending on the configured rule and severity, the pipeline can continue, continue with a warning, or stop.</p>
<p><strong>Also known as:</strong> runtime enforcement, enforce</p>
</details>

<details id="guardrail-result">
<summary><strong>Guardrail Result</strong> — The recorded outcome after FabricOps evaluates a Guardrail during a pipeline run.</summary>
<p>A Guardrail Result records what FabricOps checked, whether the Guardrail passed, warned, or failed, and the resulting pipeline decision or status.</p>
<p><strong>Also known as:</strong> guardrail results</p>
</details>

<details id="governance-as-code">
<summary><strong>Governance as Code</strong> — Defining governance requirements in structured, version-controlled forms that FabricOps can review, apply, and enforce consistently.</summary>
<p>In FabricOps, Governance as Code means representing governance requirements as structured metadata, configuration, contracts, and executable checks so they can be reviewed, versioned, repeated, and applied consistently across the engineering workflow.</p>
</details>

<details id="configuration-driven-engineering">
<summary><strong>Configuration-driven Engineering</strong> — Controlling repeatable engineering behaviour through configuration instead of rewriting pipeline code.</summary>
<p>In FabricOps, Configuration-driven Engineering means keeping reusable pipeline logic stable while configuration selects environment targets, processing strategies, governed parameters, and other repeatable behaviour.</p>
<p><strong>Also known as:</strong> config-driven engineering</p>
</details>

<details id="full-dataset">
<summary><strong>Full Dataset</strong> — The FabricOps source-read strategy that reads the complete physical source dataset for a run.</summary>
<p>In FabricOps, Full Dataset is the explicit source_read_strategy that reads the complete physical source dataset for the run rather than resolving an incremental subset.</p>
</details>

<details id="incremental-watermark">
<summary><strong>Incremental Watermark</strong> — The FabricOps source-read strategy that processes rows after the last successfully committed watermark.</summary>
<p>In FabricOps, Incremental Watermark resolves a bounded row-level range from the last successfully committed checkpoint to the current source upper watermark. The current implementation requires the configured watermark column to be non-null and globally unique for every source row so the range can be processed deterministically without skipping tied late-arriving rows.</p>
</details>

<details id="incremental-partition">
<summary><strong>Incremental Partition</strong> — The FabricOps source-read strategy that processes whole logical data buckets when those buckets are new or changed.</summary>
<p>In FabricOps, Incremental Partition observes a configured logical partition column and resolves new, changed, or reappeared bucket values into an incremental subset. Safety rules can fall back to a full-dataset read or stop execution when the target write strategy cannot safely apply the detected changes.</p>
</details>

<details id="incremental-subset">
<summary><strong>Incremental Subset</strong> — The FabricOps runtime read mode used when only part of the source needs to be processed for the current run.</summary>
<p>Incremental Subset is a resolved FabricOps runtime read mode. It is produced after source-read preparation determines the exact watermark range or logical partition values required for the current run.</p>
</details>

</details>

<details>
<summary>
<strong>Microsoft Fabric concepts</strong><br>
<span>Microsoft Fabric terms. Definitions follow Microsoft terminology where possible and link to the relevant Microsoft Learn documentation.</span>
</summary>

<details id="microsoft-fabric">
<summary><strong>Microsoft Fabric</strong> — Microsoft's end-to-end analytics platform for data ingestion, transformation, real-time processing, analytics, and reporting.</summary>
<p>Microsoft Fabric is an end-to-end analytics platform that brings together data ingestion, transformation, real-time processing, analytics, and reporting through integrated Fabric workloads over a shared data and compute foundation.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview">Official documentation</a></p>
</details>

<details id="workspace">
<summary><strong>Workspace</strong> — A collaborative container that brings related Fabric items together and controls access to them.</summary>
<p>A Microsoft Fabric Workspace is a collection of items in a shared environment designed for collaboration. It acts as a container for items such as lakehouses, warehouses, notebooks, semantic models, and reports, and provides controls for who can access them.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/fundamentals/workspaces">Official documentation</a></p>
<p><strong>Also known as:</strong> workspaces</p>
</details>

<details id="lakehouse">
<summary><strong>Lakehouse</strong> — A Fabric data item that combines data-lake storage with warehouse-style querying for structured and unstructured data.</summary>
<p>A Lakehouse in Microsoft Fabric stores structured and unstructured data in one location using Delta Lake and supports analysis through both Apache Spark and SQL without requiring the data to be moved between separate systems.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview">Official documentation</a></p>
<p><strong>Also known as:</strong> Lakehouses</p>
</details>

<details id="warehouse">
<summary><strong>Warehouse</strong> — A Fabric relational warehouse item for structured data with full transactional T-SQL capabilities.</summary>
<p>A Warehouse in Microsoft Fabric is an enterprise-scale relational warehouse on a data-lake foundation. It is designed for structured analytics and SQL-first data warehousing workloads and supports full transactional T-SQL capabilities.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing">Official documentation</a></p>
<p><strong>Also known as:</strong> Warehouses</p>
</details>

<details id="notebook">
<summary><strong>Notebook</strong> — A Fabric code item and web-based interactive surface for developing and running data, Spark, and machine-learning workloads.</summary>
<p>A Microsoft Fabric Notebook is a primary code item and web-based interactive surface used to write and execute code, combine code with Markdown and visualizations, and develop data engineering, Apache Spark, and machine-learning workloads.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook">Official documentation</a></p>
<p><strong>Also known as:</strong> notebooks, Fabric notebook</p>
</details>

<details id="medallion-architecture">
<summary><strong>Medallion Architecture</strong> — A layered data architecture that progressively improves data from Bronze raw data through Silver validated and enriched data to Gold curated data.</summary>
<p>In Microsoft Fabric, Medallion Architecture organizes data into Bronze, Silver, and Gold layers so data becomes progressively more reliable and useful as it moves from raw ingestion through validation and enrichment to curated consumption. Fabric implementations can use Lakehouses, Warehouses, or a combination of Fabric data stores for these layers.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture">Official documentation</a></p>
<p><strong>Also known as:</strong> medallion architecture design</p>
</details>

</details>

<details>
<summary>
<strong>Data Governance concepts</strong><br>
<span>Established governance terms used by FabricOps. The definitions keep their broader governance meaning and describe FabricOps usage only where relevant.</span>
</summary>

<details id="metadata">
<summary><strong>Metadata</strong> — Information that describes data, its meaning, structure, context, management, or use.</summary>
<p>Metadata is information used to describe, understand, manage, or govern data. In FabricOps this includes technical structure, Profiles, ownership, business meaning, sensitivity, Guardrails, lineage, Data Agreements, Data Contracts, and other governance and engineering context.</p>
</details>

<details id="data-steward">
<summary><strong>Data Steward</strong> — A person or role responsible for maintaining the meaning, quality expectations, governance rules, classification, and appropriate use of data.</summary>
<p>A Data Steward helps maintain trusted governance context for data, including its business meaning, ownership or accountability, sensitivity, quality expectations, intended use, and governance decisions. FabricOps uses active Data Stewards as the provider and recipient parties in Data Agreements.</p>
<p><strong>Also known as:</strong> data stewards</p>
</details>

<details id="data-sensitivity">
<summary><strong>Data Sensitivity</strong> — How carefully data should be handled based on its confidentiality, privacy, business risk, or regulatory impact.</summary>
<p>Data Sensitivity describes the level of care and protection data requires based on confidentiality, privacy, business risk, or regulatory requirements. It can influence access, masking, sharing, retention, and other governance controls.</p>
<p><strong>Also known as:</strong> sensitivity</p>
</details>

<details id="pii">
<summary><strong>PII</strong> — Information that can identify an individual directly or indirectly, on its own or when combined with other information.</summary>
<p>PII, or personally identifiable information, is information that can identify or be linked to an individual. Depending on the context and applicable policy, it may require controls such as restricted access, masking, minimization, or stricter handling.</p>
<p><strong>Also known as:</strong> personally identifiable information</p>
</details>

<details id="data-access">
<summary><strong>Data Access</strong> — The governed definition of who is allowed to access data and under what conditions.</summary>
<p>Data Access describes who is permitted to use governed data, what level of access is appropriate, and what conditions or restrictions apply. Those requirements can be implemented through platform security controls such as permissions, RLS, OLS, or other mechanisms.</p>
</details>

<details id="data-quality">
<summary><strong>Data Quality</strong> — Whether data is fit for its intended use and meets the quality expectations that apply to it.</summary>
<p>Data Quality describes whether data satisfies the expectations required for its intended use, including dimensions such as completeness, validity, consistency, uniqueness, accuracy, timeliness, and other context-specific requirements.</p>
<p><strong>Also known as:</strong> DQ</p>
</details>

<details id="access-control">
<summary><strong>Access Control</strong> — The rules and mechanisms that determine who can access data or system resources and what actions they can perform.</summary>
<p>Access Control is the broader set of rules and technical mechanisms used to determine who can access datasets, tables, columns, workspaces, files, or other resources and what actions they are allowed to perform.</p>
</details>

<details id="row-level-security">
<summary><strong>Row-Level Security (RLS)</strong> — A security method that controls which rows of data a user can see.</summary>
<p>Row-Level Security limits the rows available to a user based on identity, role, or access rules while allowing the same table or semantic model to serve different audiences.</p>
<p><strong>Also known as:</strong> RLS</p>
</details>

<details id="object-level-security">
<summary><strong>Object-Level Security (OLS)</strong> — A security method that controls whether a user can access specific data objects such as tables or columns.</summary>
<p>Object-Level Security restricts access to specific data objects, such as tables or columns, so unauthorized users cannot access those objects even when they can access the wider semantic model or resource.</p>
<p><strong>Also known as:</strong> OLS</p>
</details>

</details>

<details>
<summary>
<strong>Data Engineering concepts</strong><br>
<span>Established engineering terms used by FabricOps. The definitions keep their broader engineering meaning and call out FabricOps behaviour only where it materially matters.</span>
</summary>

<details id="configuration">
<summary><strong>Configuration</strong> — Named settings that control system or pipeline behaviour without changing the underlying implementation.</summary>
<p>Configuration is the set of named settings used to control environment targets, processing choices, parameters, rules, and other behaviour without rewriting the implementation.</p>
<p><strong>Also known as:</strong> config</p>
</details>

<details id="pipeline">
<summary><strong>Pipeline</strong> — A repeatable sequence of steps that moves, transforms, validates, or writes data.</summary>
<p>A data pipeline is a repeatable processing flow that can read source data, transform it, apply checks or validations, and write results to a target.</p>
<p><strong>Also known as:</strong> pipelines</p>
</details>

<details id="pyspark">
<summary><strong>PySpark</strong> — The Python API for Apache Spark.</summary>
<p>PySpark lets Python code use Apache Spark for distributed data processing. FabricOps uses PySpark in Fabric notebooks for repeatable data engineering and transformation workloads.</p>
</details>

<details id="profile">
<summary><strong>Profile</strong> — A summary of the characteristics of a dataset at a point in time.</summary>
<p>A data Profile summarizes characteristics such as row count, columns, data types, nulls, distinct values, minimum and maximum values, and value distributions. FabricOps stores these observations in Data Profiled and Data Profiled Frequency metadata.</p>
<p><strong>Also known as:</strong> profiles, profiling</p>
</details>

<details id="schema">
<summary><strong>Schema</strong> — The defined structure of data, including its fields or columns and their data types.</summary>
<p>A Schema describes the structure expected for a dataset or table, including field or column names, data types, and other structural constraints or expectations.</p>
<p><strong>Also known as:</strong> schemas</p>
</details>

<details id="watermark">
<summary><strong>Watermark</strong> — A checkpoint that represents how far an incremental process has successfully processed a source.</summary>
<p>A Watermark is a saved progress marker used by an incremental process to determine what data should be considered after a previously successful point. The exact uniqueness, ordering, and tie-handling requirements depend on the incremental design.</p>
</details>

<details id="parallel-processing">
<summary><strong>Parallel Processing</strong> — Processing multiple independent parts of a workload at the same time.</summary>
<p>Parallel Processing divides a workload so multiple tasks, partitions, or units of work can execute concurrently, which can reduce elapsed time when the workload and available compute support it.</p>
</details>

<details id="data-modelling">
<summary><strong>Data Modelling</strong> — Designing data structures and relationships so data can be stored, understood, and used effectively.</summary>
<p>Data Modelling is the practice of designing tables, fields, keys, relationships, and structures so data supports its intended analytical, operational, or reporting use.</p>
<p><strong>Also known as:</strong> data modeling</p>
</details>

<details id="partition">
<summary><strong>Partition</strong> — A subdivision of data or workload used to organize storage or processing.</summary>
<p>A Partition groups part of a dataset or workload so it can be stored, scanned, processed, or managed independently. The term can refer to logical processing groups or physical storage organization depending on context.</p>
</details>

<details id="physical-partitioning">
<summary><strong>Physical Partitioning</strong> — Organizing stored data physically by one or more partition columns to improve management or data skipping.</summary>
<p>Physical Partitioning controls how data files are organized by partition values in storage. In FabricOps this is distinct from the Incremental Partition source-read strategy, which operates on logical source buckets.</p>
<p><strong>Also known as:</strong> partition_by</p>
</details>

<details id="append">
<summary><strong>Append</strong> — A write strategy that adds new rows without replacing existing rows.</summary>
<p>Append adds incoming rows to an existing target while leaving existing rows unchanged. It is appropriate when incoming data is additive and existing records do not need to be changed or removed.</p>
</details>

<details id="overwrite">
<summary><strong>Overwrite</strong> — A write strategy that replaces existing target data within a defined write scope.</summary>
<p>Overwrite replaces existing target data with newly prepared data. Depending on the implementation and scope, this can replace a whole table or a selected partition range.</p>
</details>

<details id="slowly-changing-dimensions">
<summary><strong>Slowly Changing Dimensions (SCD)</strong> — Patterns for handling changes to descriptive dimension records over time.</summary>
<p>Slowly Changing Dimensions are data-modelling patterns for handling changes to descriptive records. Common approaches include SCD Type 1, which replaces the previous value, and SCD Type 2, which preserves history by creating versioned records.</p>
<p><strong>Also known as:</strong> SCD, slowly changing dimension</p>
</details>

</details>
