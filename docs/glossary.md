<!-- GENERATED FILE: edit docs/reference/_data/glossary.json or scripts/generate_glossary_page.py -->

# FabricOps glossary

Use this page as the repository source of truth for FabricOps, Microsoft Fabric, Governance, and Data Engineering terminology.

Definitions are grounded first in the current FabricOps implementation. Microsoft Fabric terms follow Microsoft terminology and link to Microsoft Learn. Established Governance and Engineering terms keep their standard meaning unless FabricOps explicitly documents a narrower implementation.

<details>
<summary>
<strong>FabricOps concepts</strong><br>
<span>These terms describe how FabricOps implements its Data Engineering and Governance practice. Where a broader industry concept exists, the definitions here describe how FabricOps uses it.</span>
</summary>

<details id="fabricops-starter-kit">
<summary><strong>FabricOps Starter Kit</strong> — A plug-and-play Data Engineering and Governance practice for Microsoft Fabric.</summary>
<p>FabricOps Starter Kit is a plug-and-play Data Engineering and Governance practice for Microsoft Fabric, implemented through a planned operating workflow, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model.</p>
</details>

<details id="governance-as-code">
<summary><strong>Governance as Code</strong> — Defining governance requirements in structured, version-controlled forms that FabricOps can review, apply, and enforce consistently.</summary>
<p>In FabricOps, Governance as Code means expressing governance requirements in structured, version-controlled forms so they can be reviewed, repeated, and applied consistently. This includes FabricOps metadata such as Data Agreements, Enrichment, Guardrails, Data Contracts, approved usages, and other governed configuration or executable checks.</p>
</details>

<details id="configuration-driven-engineering">
<summary><strong>Configuration-driven Engineering</strong> — Controlling repeatable engineering behaviour through configuration instead of rewriting pipeline code.</summary>
<p>In FabricOps, Configuration-driven Engineering means defining reusable pipeline behaviour through configuration so teams can change environment targets, source processing strategies, target write strategies, and governed parameters without duplicating or rewriting the underlying engineering logic.</p>
<p><strong>Also known as:</strong> config-driven engineering</p>
</details>

<details id="data-agreement">
<summary><strong>Data Agreement</strong> — A governed agreement between a provider Data Steward and a recipient Data Steward that defines why data is shared and its approved uses.</summary>
<p>In FabricOps, a Data Agreement is a versioned governed agreement between two distinct active Data Stewards: one provider and one recipient. It records the business purpose, approved usages, validity period, supporting documents, domain, and other governance context under which governed data is shared.</p>
<p><strong>Also known as:</strong> data agreements</p>
</details>

<details id="enrichment">
<summary><strong>Enrichment</strong> — Business and governance information added to the Data Catalogue after technical metadata has been captured.</summary>
<p>In FabricOps, Enrichment is business and governance metadata added to a governed table or column after technical Catalogue metadata has been captured. It can record descriptions, ownership, sensitivity, classification, and other context used to understand and govern the data.</p>
<p><strong>Also known as:</strong> metadata enrichment, enrich metadata</p>
</details>

<details id="guardrails">
<summary><strong>Guardrails</strong> — Governed rules that FabricOps applies to data and pipeline execution.</summary>
<p>In FabricOps, Guardrails are versioned governed rules associated with a table or column. Active Guardrails can evaluate schema, freshness, profile behaviour, change over time, data quality, and other supported requirements during pipeline execution.</p>
<p><strong>Also known as:</strong> guardrail</p>
</details>

<details id="enforcement">
<summary><strong>Enforcement</strong> — Applying active Guardrails during a pipeline run and acting on their results.</summary>
<p>In FabricOps, Enforcement applies the relevant active Guardrails during pipeline execution and acts on their outcomes. Depending on the configured rule and severity, execution can continue, continue with a warning, or stop.</p>
<p><strong>Also known as:</strong> runtime enforcement, enforce</p>
</details>

<details id="guardrail-result">
<summary><strong>Guardrail Result</strong> — The recorded outcome after FabricOps evaluates a Guardrail during a pipeline run.</summary>
<p>In FabricOps, a Guardrail Result records the outcome of evaluating a Guardrail during a pipeline run, including what was checked, the evaluation status, and the execution decision associated with the result.</p>
<p><strong>Also known as:</strong> guardrail results</p>
</details>

<details id="data-contract">
<summary><strong>Data Contract</strong> — A versioned definition of the guarantees and expectations for one governed table.</summary>
<p>In FabricOps, a Data Contract is an immutable, versioned definition for one governed table under one exact Data Agreement version. It is tied to a table_id and freezes the table identity and schema together with relevant processing expectations, Enrichment, active Guardrails, approved usages, Agreement context, and Data Steward context so consumers know what they can depend on. FabricOps can provide Data Contracts for governed tables it writes and consume Data Contracts for governed tables it reads.</p>
<p><strong>Also known as:</strong> data contracts</p>
</details>

<details id="full-dataset">
<summary><strong>Full Dataset</strong> — The FabricOps source processing strategy that reads the complete physical source dataset for a run.</summary>
<p>In FabricOps, Full Dataset is the source_read_strategy that processes the complete physical source dataset. It does not use a watermark column or logical source partition column.</p>
</details>

<details id="incremental-watermark">
<summary><strong>Incremental Watermark</strong> — The FabricOps source processing strategy that reads rows within a bounded range after the last successfully committed watermark.</summary>
<p>In FabricOps, Incremental Watermark is the source_read_strategy that uses one configured watermark column and a successfully committed checkpoint to resolve a bounded (lower, upper] source scope. The current implementation requires the watermark value to be non-null and globally unique for every source row so rows cannot be skipped when a checkpoint advances.</p>
<p><strong>Also known as:</strong> watermark-based incremental loading</p>
</details>

<details id="incremental-partition">
<summary><strong>Incremental Partition</strong> — The FabricOps source processing strategy that processes whole logical source buckets when they are new or changed.</summary>
<p>In FabricOps, Incremental Partition is the source_read_strategy that uses a configured logical partition column and change observations to select affected buckets, such as days, months, or snapshots. Depending on detected changes and the target write strategy, FabricOps can read an incremental subset, skip the run, require a full dataset read, or reject an unsafe change.</p>
<p><strong>Also known as:</strong> partition-based incremental loading</p>
</details>

<details id="incremental-subset">
<summary><strong>Incremental Subset</strong> — The FabricOps runtime read mode used when only part of the source should be processed for the current run.</summary>
<p>In FabricOps, Incremental Subset is a resolved runtime read mode, not an engineer-authored source strategy. It is produced when Incremental Watermark or Incremental Partition determines a safe bounded source scope for the current run.</p>
</details>

</details>

<details>
<summary>
<strong>Microsoft Fabric concepts</strong><br>
<span>Microsoft owns these product terms. FabricOps follows Microsoft Fabric terminology and links to Microsoft Learn as the source of truth.</span>
</summary>

<details id="microsoft-fabric">
<summary><strong>Microsoft Fabric</strong> — Microsoft's end-to-end analytics platform and the runtime platform for FabricOps.</summary>
<p>Microsoft Fabric is an end-to-end analytics platform that brings together data integration, data engineering, data warehousing, data science, real-time intelligence, and business intelligence over shared platform capabilities. FabricOps runs on Microsoft Fabric.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview">Official definition and documentation</a></p>
</details>

<details id="workspace">
<summary><strong>Workspace</strong> — A Microsoft Fabric collaborative container for organizing and managing access to related items.</summary>
<p>A Workspace in Microsoft Fabric is a collaborative container that groups related Fabric items and provides a place to manage access and work with those items. FabricOps uses separate workspaces to establish its Governance, Engineering Development, Engineering Production, and project-specific consumer operating boundaries.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/fundamentals/workspaces">Official definition and documentation</a></p>
<p><strong>Also known as:</strong> workspaces</p>
</details>

<details id="lakehouse">
<summary><strong>Lakehouse</strong> — A Microsoft Fabric storage item for files and Delta tables in OneLake with Spark and SQL access.</summary>
<p>A Lakehouse in Microsoft Fabric stores structured and unstructured data in OneLake using file and table areas, with Delta tables for managed structured data. It supports Spark-based engineering and SQL access through its SQL analytics endpoint.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview">Official definition and documentation</a></p>
<p><strong>Also known as:</strong> Lakehouses</p>
</details>

<details id="warehouse">
<summary><strong>Warehouse</strong> — A Microsoft Fabric relational warehouse item designed for structured, SQL-first analytics.</summary>
<p>A Warehouse in Microsoft Fabric is an enterprise-scale relational warehouse on a data lake foundation. It is primarily developed with T-SQL, stores data in Delta format, and is designed for structured analytical and data warehousing workloads.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing">Official definition and documentation</a></p>
<p><strong>Also known as:</strong> Warehouses</p>
</details>

<details id="notebook">
<summary><strong>Notebook</strong> — A Microsoft Fabric item for interactive code, data processing, analysis, and engineering.</summary>
<p>A Notebook in Microsoft Fabric is an interactive development item for working with Apache Spark and related data workloads. Fabric notebooks support PySpark, Scala, Spark SQL, and SparkR cells and are used extensively by FabricOps for setup, governance, engineering, and exploration workflows.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/fabric/data-engineering/author-execute-notebook">Official definition and documentation</a></p>
<p><strong>Also known as:</strong> notebooks, Fabric notebook</p>
</details>

</details>

<details>
<summary>
<strong>Governance concepts</strong><br>
<span>Established data-governance and security concepts. FabricOps keeps their standard meaning and only adds implementation context where relevant.</span>
</summary>

<details id="data-steward">
<summary><strong>Data Steward</strong> — A person or role responsible for maintaining the meaning, quality expectations, governance rules, and appropriate use of data.</summary>
<p>A Data Steward is a governance role responsible for helping maintain trusted business and governance context for data, including meaning, quality expectations, classification, appropriate use, and governance decisions. FabricOps uses Data Stewards as the provider and recipient parties in a Data Agreement.</p>
<p><strong>Also known as:</strong> data stewards</p>
</details>

<details id="metadata">
<summary><strong>Metadata</strong> — Information that describes data and provides context for understanding, managing, or governing it.</summary>
<p>Metadata is information about data, such as its structure, meaning, ownership, lineage, quality context, classifications, and rules. FabricOps persists technical, operational, and governance metadata across its shared metadata model.</p>
</details>

<details id="data-sensitivity">
<summary><strong>Data Sensitivity</strong> — The level of care data requires based on confidentiality, privacy, business risk, or regulatory impact.</summary>
<p>Data Sensitivity describes the handling level appropriate for data based on confidentiality, privacy, business risk, or regulatory requirements. Sensitivity can influence access, masking, sharing, retention, and other governance controls.</p>
<p><strong>Also known as:</strong> sensitivity</p>
</details>

<details id="pii">
<summary><strong>PII</strong> — Information that can identify an individual directly or indirectly, alone or when combined with other information.</summary>
<p>PII, or personally identifiable information, is information that can identify an individual directly or indirectly, including when combined with other linked or linkable information. Governed handling can require controls such as restricted access or masking.</p>
<p><strong>Also known as:</strong> personally identifiable information</p>
</details>

<details id="data-access">
<summary><strong>Data Access</strong> — The governed definition of who is allowed to access data and under what conditions.</summary>
<p>Data Access describes the governed requirement for who may access data and the conditions or restrictions that apply. Technical controls such as permissions, RLS, OLS, masking, or other mechanisms can implement that requirement.</p>
</details>

<details id="data-quality">
<summary><strong>Data Quality</strong> — The degree to which data is fit for its intended use and meets defined expectations.</summary>
<p>Data Quality describes whether data is fit for its intended use and meets defined expectations such as completeness, validity, consistency, uniqueness, accuracy, timeliness, or other relevant requirements. FabricOps can represent and evaluate data quality requirements through Guardrails.</p>
<p><strong>Also known as:</strong> DQ</p>
</details>

<details id="access-control">
<summary><strong>Access Control</strong> — The rules and mechanisms that determine who can access data or system resources and what they can do.</summary>
<p>Access Control is the broader set of rules and mechanisms used to determine who can access datasets, tables, columns, workspaces, files, or other resources and which actions they are allowed to perform.</p>
</details>

<details id="row-level-security">
<summary><strong>Row-Level Security (RLS)</strong> — A security method that restricts which rows of data a user can access.</summary>
<p>Row-Level Security restricts the rows available to a user based on identity, role, or access rules while allowing the same table or semantic model to serve different audiences.</p>
<p><strong>Also known as:</strong> RLS</p>
</details>

<details id="object-level-security">
<summary><strong>Object-Level Security (OLS)</strong> — A security method that restricts access to specific data objects such as tables or columns.</summary>
<p>Object-Level Security restricts access to specific objects, such as tables or columns, so unauthorized users cannot access those objects even when they can access the wider model or data product.</p>
<p><strong>Also known as:</strong> OLS</p>
</details>

</details>

<details>
<summary>
<strong>Engineering concepts</strong><br>
<span>Established data-engineering concepts. FabricOps keeps their standard meaning and states any FabricOps-specific constraint explicitly.</span>
</summary>

<details id="configuration">
<summary><strong>Configuration</strong> — Named settings that control system or pipeline behaviour without changing the implementation code.</summary>
<p>Configuration is a set of named settings used to control environment targets, processing choices, rules, parameters, and other behaviour without rewriting the implementation. FabricOps uses configuration extensively to make notebook and pipeline behaviour repeatable across environments.</p>
<p><strong>Also known as:</strong> config</p>
</details>

<details id="pipeline">
<summary><strong>Pipeline</strong> — A repeatable sequence of steps that moves, transforms, checks, and writes data.</summary>
<p>A data pipeline is a repeatable sequence of processing steps that can read source data, transform it, validate it, and write results to a target. In FabricOps, the notebook-facing engineering workflow uses this concept without implying that every pipeline is a Microsoft Fabric Data Factory Pipeline item.</p>
<p><strong>Also known as:</strong> pipelines</p>
</details>

<details id="pyspark">
<summary><strong>PySpark</strong> — The Python API for Apache Spark.</summary>
<p>PySpark lets Python code use Apache Spark to process data with a distributed compute engine. FabricOps uses PySpark in Fabric notebooks for repeatable data engineering, profiling, validation, and related processing.</p>
</details>

<details id="profile">
<summary><strong>Profile</strong> — A statistical and structural summary of a dataset at a point in time.</summary>
<p>A data Profile summarizes a dataset at a point in time using characteristics such as row count, columns, data types, nulls, distinct values, minimum and maximum values, and value distributions. FabricOps stores profiling outputs in Data Profiled and Data Profiled Frequency metadata.</p>
<p><strong>Also known as:</strong> profiles, profiling</p>
</details>

<details id="schema">
<summary><strong>Schema</strong> — The defined structure of data, including columns, data types, and other structural expectations.</summary>
<p>A Schema describes the structure of a dataset or table, including column names, data types, and other structural expectations. FabricOps captures table and column structure in Catalogue metadata and can validate it through Guardrails and Data Contracts.</p>
<p><strong>Also known as:</strong> schemas</p>
</details>

<details id="watermark">
<summary><strong>Watermark</strong> — A checkpoint that represents how far an incremental process has successfully processed a source.</summary>
<p>A Watermark is a checkpoint used by an incremental process to represent processing progress and determine what should be considered after the last successful point. The generic concept does not require watermark values to be globally unique; FabricOps Incremental Watermark deliberately imposes stricter requirements.</p>
</details>

<details id="parallel-processing">
<summary><strong>Parallel Processing</strong> — Processing multiple parts of a workload at the same time.</summary>
<p>Parallel Processing divides work so multiple tasks, data partitions, or workers can operate concurrently, which can reduce elapsed processing time when the workload and compute resources support it.</p>
</details>

<details id="data-modelling">
<summary><strong>Data Modelling</strong> — Designing data structures and relationships so data can be stored, understood, and used effectively.</summary>
<p>Data Modelling is the practice of designing tables, fields, keys, relationships, and structures so data supports its intended analytical, operational, or reporting use.</p>
<p><strong>Also known as:</strong> data modeling</p>
</details>

<details id="partition">
<summary><strong>Partition</strong> — A distinct subset of data grouped so it can be stored, queried, processed, or managed separately.</summary>
<p>A Partition is a subset of data grouped by a defined rule or boundary so it can be handled separately. In FabricOps Incremental Partition, the word refers specifically to logical source buckets such as days, months, or snapshots rather than necessarily to the target table's physical storage layout.</p>
</details>

<details id="physical-partitioning">
<summary><strong>Physical Partitioning</strong> — Organizing stored table data by partition columns so storage engines can manage and prune data more efficiently.</summary>
<p>Physical Partitioning organizes a table's stored data into physical partitions based on one or more partition columns. In FabricOps, this is a target storage concern and is separate from the logical source buckets used by Incremental Partition.</p>
<p><strong>Also known as:</strong> partition_by</p>
</details>

<details id="append">
<summary><strong>Append</strong> — A write strategy that adds new rows without replacing existing rows.</summary>
<p>Append adds incoming rows to an existing target while leaving existing rows unchanged. It is appropriate when incoming data is additive and existing target records do not need to be changed or removed.</p>
</details>

<details id="overwrite">
<summary><strong>Overwrite</strong> — A write strategy that replaces existing target data within the write scope.</summary>
<p>Overwrite replaces existing target data with newly prepared data within the implemented write scope. Depending on the processing definition, the scope can be a whole table or a governed physical partition scope.</p>
</details>

<details id="slowly-changing-dimensions">
<summary><strong>Slowly Changing Dimensions (SCD)</strong> — Data-modelling patterns for handling changes to descriptive dimension records over time.</summary>
<p>Slowly Changing Dimensions are data-modelling patterns for managing changes to descriptive records. Common approaches include SCD Type 1, which replaces prior attribute values, and SCD Type 2, which preserves history through versioned records. FabricOps implements governed SCD1 and SCD2 target processing where the configured target writer supports it; governed Warehouse SCD execution is not currently supported.</p>
<p><strong>Also known as:</strong> SCD, slowly changing dimension</p>
</details>

</details>
