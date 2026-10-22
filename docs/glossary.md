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
<summary><strong>FabricOps Starter Kit</strong> — A lightweight governed engineering framework for Microsoft Fabric.</summary>
<p>FabricOps packages reusable notebooks, governed read/write orchestration, Data Contracts, Data Agreements, and shared metadata so teams can run governed Fabric pipelines without rebuilding the same engineering and governance plumbing.</p>
</details>

<details id="data-agreement">
<summary><strong>Data Agreement</strong> — A versioned agreement between provider and recipient Data Stewards that defines why data may be shared and used.</summary>
<p>A Data Agreement records accountable producer/consumer stewards, purpose, approved uses and validity. An Activated Pipeline links one exact Agreement version to a complete successfully tested whole pipeline.</p>
<p><strong>Also known as:</strong> data agreements</p>
</details>

<details id="data-contract">
<summary><strong>Data Contract</strong> — A versioned set of governed expectations for one table.</summary>
<p>A globally versioned table-centric Data Contract freezes Schema, processing, Enrichment and Guardrails. Draft becomes Frozen and stays immutable and reusable across environments. An Activated Pipeline references exact versions and payload hashes. Environment activation can differ while sharing one central contract history; contracts have no individual activation step.</p>
<p><strong>Also known as:</strong> data contracts</p>
</details>

<details id="activated-pipeline">
<summary><strong>activated pipeline</strong> — An immutable approved version of a completely and successfully tested whole pipeline.</summary>
<p>METADATA_ACTIVATION_STATE contains immutable approved pipeline manifests and the active configuration for each environment and pipeline_id. Each manifest binds successful whole-run Testing, an exact effective Agreement, global frozen contracts, transformation settings and physical destinations. Governance approves affected pipelines together; new Live runs resolve the coordinated revision automatically. Activation neither deploys notebooks nor writes business data.</p>
<p><strong>Also known as:</strong> activated pipelines</p>
</details>

<details id="pipeline-execution-plan">
<summary><strong>pipeline execution plan</strong> — The validated execution decisions shared by every Read and Write in one pipeline run.</summary>
<p>Internal run authority fixes exact table contracts, stable pipeline identity and environment destinations. Test discovers participants from operations; Live pins an approved manifest and revision. Public Read and Write calls use the execution session automatically.</p>
</details>

<details id="testing">
<summary><strong>Testing</strong> — Pipeline execution against all frozen contracts, or explicit contract-free exploration.</summary>
<p>Test evaluates real reads, transformations and selected frozen Data Contract Guardrails without business or operational metadata commits. Diagnostic results remain in the execution session. Existing activation requires persisted complete Testing evidence, which evaluation-only Test cannot create.</p>
</details>

<details id="live">
<summary><strong>Live</strong> — The deliberate pipeline-wide mode that permits governed publication and operational metadata commits.</summary>
<p>Live automatically resolves an approved environment configuration from METADATA_ACTIVATION_STATE and pins its revision. Exact contracts, writer ownership, transformation settings and physical destinations are enforced. Affected running executions drain before coordinated activation.</p>
</details>

<details id="enrichment">
<summary><strong>Enrichment</strong> — Descriptive business and governance metadata added to a governed table or column.</summary>
<p>FabricOps Enrichment stores descriptions, Grain description, and information classifications inside METADATA_DATA_CONTRACT.contract_payload_json for an exact Data Contract version. It adds context but does not enforce pipeline behaviour; runtime requirements belong in Guardrails.</p>
<p><strong>Also known as:</strong> metadata enrichment, enrich metadata</p>
</details>

<details id="guardrails">
<summary><strong>Guardrails</strong> — Versioned rules that FabricOps checks during governed pipeline execution.</summary>
<p>FabricOps Guardrails are executable definitions inside METADATA_DATA_CONTRACT.contract_payload_json for an exact version. Source contracts support five Guardrails: Schema, Grain, Freshness, Source Drift, and Data Quality. Target contracts support four: Schema, Grain, Data Quality, and Sensitive Data treatment. orchestrate_read runs four checks: Freshness, Schema, Grain, and Data Quality. orchestrate_write runs five checks: Schema, Sensitive Data, Source Drift on participating sources, Grain, and Data Quality before publication. Schema checks block missing Required columns and contracted datatype mismatches; additional columns warn and permit continuation. Active Sensitive Data treatment failures also block publication. Grain, Freshness, Source Drift, and Data Quality rules can be configured to warn or block when their expectation is not met.</p>
<p><strong>Also known as:</strong> guardrail</p>
</details>

<details id="enforcement">
<summary><strong>Enforcement</strong> — Evaluating active Guardrails during a pipeline run and applying their configured action.</summary>
<p>FabricOps orchestrate_read() and orchestrate_write() resolve the selected Data Contract and run its Guardrails at the relevant boundary. Schema violations and Sensitive Data treatment failures block; Grain, Freshness, Source Drift, and Data Quality follow their saved Warn or Block action. Live stops when an applicable configured Guardrail blocks or cannot execute; disabled optional checks do not impose additional requirements.</p>
<p><strong>Also known as:</strong> runtime enforcement, enforce</p>
</details>

<details id="guardrail-result">
<summary><strong>Guardrail Result</strong> — The outcome of a Guardrail evaluation during a pipeline run.</summary>
<p>FabricOps persists summary outcomes in METADATA_GUARDRAIL_RESULTS and returns stage results through orchestrate_read() and orchestrate_write(), so Engineering can inspect what passed, warned, or blocked.</p>
<p><strong>Also known as:</strong> guardrail results</p>
</details>

<details id="governance-as-code">
<summary><strong>Governance as Code</strong> — Representing governance decisions as structured metadata that engineering can directly use.</summary>
<p>FabricOps stores Data Agreements, Data Contracts, Enrichment, and Guardrails as structured metadata. Governed pipelines resolve that same metadata during validation and execution instead of relying only on separate prose documentation.</p>
</details>

<details id="configuration-driven-engineering">
<summary><strong>Configuration-driven Engineering</strong> — Keeping reusable pipeline logic separate from environment-specific Fabric configuration.</summary>
<p>00_env_config maps logical stores to the Fabric items for the active environment. The same 02_pipeline can therefore move between environments without hard-coded workspace IDs, item IDs, paths, or endpoints throughout the notebook.</p>
<p><strong>Also known as:</strong> config-driven engineering</p>
</details>

<details id="read-transform-write">
<summary><strong>Read / Transform / Write</strong> — The three user-facing stages of the standard 02_pipeline: Read, Transform, and Write.</summary>
<p>Read uses FabricOps governed read orchestration, Transform contains project-owned PySpark logic, and Write uses governed write orchestration. Source and target describe dataset roles, not additional notebook stages.</p>
<p><strong>Also known as:</strong> Read → Transform → Write, RTW</p>
</details>

<details id="full-dataset">
<summary><strong>Full Dataset</strong> — A read that loads the complete selected source dataset for the run.</summary>
<p>FabricOps returns the complete selected source without a project-owned source filter or incremental scope.</p>
</details>

<details id="load-strategy">
<summary><strong>Load Strategy</strong> — The governed method used to write a target table.</summary>
<p>FabricOps supports four load strategies: overwrite, append, SCD1, and SCD2. The target Data Contract stores the selected strategy and any required parameters.</p>
<p><strong>Also known as:</strong> write strategy</p>
</details>

<details id="source-drift">
<summary><strong>Source Drift</strong> — A check for unexpected changes to source data already consumed by a target.</summary>
<p>FabricOps compares the current source observation with the last committed observation for the same source, target, and environment. A new observation is committed only after the target write succeeds.</p>
</details>

<details id="writer-ownership">
<summary><strong>Writer Ownership</strong> — The rule that one governed target table_id has one owning notebook writer.</summary>
<p>FabricOps records the logical writer notebook for a governed target. Pipeline execution rejects a conflicting writer so independent pipelines do not write the same governed table with different assumptions.</p>
<p><strong>Also known as:</strong> single writer</p>
</details>

<details id="data-catalogue">
<summary><strong>Data Catalogue</strong> — The canonical metadata record for a governed table and its columns.</summary>
<p>FabricOps Data Catalogue metadata identifies governed tables and columns and stores the technical and enriched attributes used by profiling, contracts, guardrails, and other governance workflows.</p>
<p><strong>Also known as:</strong> Data Catalogue</p>
</details>

<details id="freshness">
<summary><strong>Freshness</strong> — A Guardrail that checks whether source data is current enough for the governed expectation.</summary>
<p>FabricOps Freshness evaluates a configured date or datetime column against the expected source refresh timing. It is separate from the notebook's Fabric scheduled refresh.</p>
<p><strong>Also known as:</strong> Freshness Guardrail</p>
</details>

<details id="grain">
<summary><strong>Grain</strong> — The column or column combination that uniquely identifies a row at the table's intended level of detail.</summary>
<p>FabricOps stores the Grain description as Enrichment, selected key columns as a singular table Grain definition, and enforcement as an independent choice. Grain is not enforced until explicitly enabled, defaulting to Block; Warn records violations and allows continuation. Enforced Grain rejects null key components and duplicate key combinations in returned Read rows or prepared Write input. It does not guarantee resulting-table uniqueness for Append or SCD. SCD2 history needs a version-aware physical row key.</p>
<p><strong>Also known as:</strong> row grain</p>
</details>

<details id="orchestrate-read">
<summary><strong>orchestrate_read()</strong> — The FabricOps orchestrator for reading a source and running the configured read-side governance checks.</summary>
<p>orchestrate_read() resolves the source, reads it through the appropriate FabricOps I/O path, and runs the applicable read-side checks before returning data and inspection outputs to the notebook.</p>
<p><strong>Also known as:</strong> governed read, read orchestrator</p>
</details>

<details id="orchestrate-write">
<summary><strong>orchestrate_write()</strong> — The FabricOps orchestrator for validating and writing one governed target.</summary>
<p>orchestrate_write() runs the applicable write-side checks, applies the governed load strategy, writes the target through FabricOps I/O, and records the resulting metadata only after the write succeeds.</p>
<p><strong>Also known as:</strong> governed write, write orchestrator</p>
</details>

<details id="contract-status">
<summary><strong>Contract Status</strong> — The lifecycle state of a Data Contract version: Draft, Frozen, or Activated.</summary>
<p>A Draft can be edited, a Frozen version is immutable and ready for validation, and an Activated frozen version is approved for Live use and linked to a Data Agreement version.</p>
<p><strong>Also known as:</strong> Draft, Frozen, Activated</p>
</details>

<details id="business-rule">
<summary><strong>Business Rule</strong> — A human-readable requirement that describes how governed data should behave.</summary>
<p>FabricOps can translate a Business Rule into the smallest deterministic Data Quality rules it can resolve, falling back to a custom PySpark boolean expression when needed.</p>
<p><strong>Also known as:</strong> business rules</p>
</details>

<details id="information-classification">
<summary><strong>Information Classification</strong> — A descriptive label that records the sensitivity or governance meaning of a table or column.</summary>
<p>FabricOps stores Information Classification as Enrichment. It provides governance context but does not apply masking, tokenization, bucketing, removal, or other runtime treatment by itself.</p>
<p><strong>Also known as:</strong> classification</p>
</details>

<details id="source-observation">
<summary><strong>Source Observation</strong> — A recorded view of source state used as the baseline for Source Drift checks.</summary>
<p>FabricOps compares the current source state with the latest committed observation for the same source, target, and environment. A new observation is committed only after the target write succeeds.</p>
<p><strong>Also known as:</strong> source observations</p>
</details>

<details id="table-profiling-policy">
<summary><strong>table profiling policy</strong> — Mutable Table ID-level operational schedules for Standard Profiling, Grain Discovery and Frequency Profiling.</summary>
<p>METADATA_TABLE_PROFILING stores independent frequency and Read/Write triggers plus per-environment/physical-context claims and last-success history. Policies are edited through Data Contract Authoring without changing immutable contract rules. Pipeline identity does not partition the shared schedule.</p>
</details>

<details id="lineage">
<summary><strong>Lineage</strong> — Metadata that records how governed data moves from source to target through a pipeline.</summary>
<p>FabricOps records source-to-target relationships from governed pipeline execution so a table's upstream and downstream paths can be traced.</p>
<p><strong>Also known as:</strong> data lineage</p>
</details>

<details id="table-id">
<summary><strong>table_id</strong> — The stable FabricOps identifier for one governed table.</summary>
<p>FabricOps uses table_id to resolve a governed table across metadata, Data Contracts, profiles, guardrails, lineage, and pipeline execution without relying on a physical Fabric item name alone.</p>
<p><strong>Also known as:</strong> table ID</p>
</details>

<details id="effective-data-access">
<summary><strong>Effective Data Access</strong> — The resolved access people have to Fabric data after combining supported access paths.</summary>
<p>FabricOps combines applicable item-level access with Workspace, SQL endpoint, or OneLake Security data permissions, then resolves principals to people while preserving verification state, restrictions, and inheritance paths.</p>
<p><strong>Also known as:</strong> effective access</p>
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

<details id="scheduled-refresh">
<summary><strong>scheduled refresh</strong> — The Microsoft Fabric schedule configured to run a notebook.</summary>
<p>FabricOps reads notebook schedule metadata from Fabric. It is operational metadata, not a Data Contract setting, and is separate from the Freshness expectation for source data.</p>
<p><strong>Microsoft Learn:</strong> <a href="https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/list-item-schedules">Official documentation</a></p>
<p><strong>Also known as:</strong> notebook schedule</p>
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
<summary><strong>Metadata</strong> — Information that describes data and its technical, business, governance, or operational context.</summary>
<p>FabricOps metadata includes table and column structure, profiles, lineage, stewardship, agreements, contracts, enrichment, guardrails, and pipeline observations.</p>
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

<details id="sensitive-data">
<summary><strong>sensitive data</strong> — A Guardrail that applies an explicit treatment to a governed column before write.</summary>
<p>FabricOps Sensitive Data rules apply one configured treatment to a column before a governed write: tokenize, mask, bucket, or remove. Information Classification remains descriptive and does not trigger treatment by itself.</p>
<p><strong>Also known as:</strong> Sensitive Data Guardrail</p>
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
<summary><strong>Data Quality</strong> — Whether data meets the expectations required for its intended use.</summary>
<p>In FabricOps, Data Quality Guardrails define deterministic checks such as completeness, allowed values, blocked values, ranges, uniqueness, and business-rule expressions.</p>
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
<p>FabricOps uses configuration to resolve environment-specific Fabric items and repeatable pipeline settings without embedding them throughout project logic.</p>
<p><strong>Also known as:</strong> config</p>
</details>

<details id="pipeline">
<summary><strong>Pipeline</strong> — A repeatable sequence of steps that moves, transforms, validates, or writes data.</summary>
<p>In FabricOps, 02_pipeline provides the standard Read → Transform → Write flow, with governed orchestration around project-owned transformation logic.</p>
<p><strong>Also known as:</strong> pipelines</p>
</details>

<details id="pipeline-run">
<summary><strong>pipeline run</strong> — One logical pipeline execution across every declared Read and Write.</summary>
<p>METADATA_PIPELINE_RUN records one logical attempt across all declared Reads and Writes, stable pipeline_id, candidate identity, operations and status. Notebook cell events detect failure but do not establish whole-run success. Unobserved completion remains incomplete. Ungoverned Testing is excluded from approval evidence. Live references its exact activated_pipeline_id.</p>
</details>

<details id="pyspark">
<summary><strong>PySpark</strong> — The Python API for Apache Spark.</summary>
<p>PySpark lets Python code use Apache Spark for distributed data processing. FabricOps uses PySpark in Fabric notebooks for repeatable data engineering and transformation workloads.</p>
</details>

<details id="profile">
<summary><strong>Profile</strong> — A measured summary of a dataset at a point in time.</summary>
<p>FabricOps profiling records characteristics such as row count, data types, nulls, distinct values, ranges, frequencies, and key candidates in metadata.</p>
<p><strong>Also known as:</strong> profiles, profiling</p>
</details>

<details id="schema">
<summary><strong>Schema</strong> — The defined structure of data, including its fields or columns and their data types.</summary>
<p>FabricOps uses schema expectations to compare the structure of governed data, including column names and data types, at the relevant read or write boundary.</p>
<p><strong>Also known as:</strong> schemas</p>
</details>

<details id="watermark">
<summary><strong>Watermark</strong> — A saved progress value used to identify data after the last successful incremental boundary.</summary>
<p>A watermark marks target-specific incremental progress. After successful target publication, later FabricOps incremental reads return rows strictly after the committed value.</p>
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
<p>Physical Partitioning controls how data files are organized by partition values in storage. It is a target storage and performance concern, distinct from project-owned source filtering.</p>
<p><strong>Also known as:</strong> partition_by</p>
</details>

<details id="append">
<summary><strong>Append</strong> — A load strategy that adds incoming rows to the target.</summary>
<p>FabricOps adds the prepared incoming rows without changing existing target rows.</p>
</details>

<details id="overwrite">
<summary><strong>Overwrite</strong> — A load strategy that replaces the target data in the write scope.</summary>
<p>FabricOps replaces existing target data with the prepared output for the configured write scope.</p>
</details>

<details id="slowly-changing-dimensions">
<summary><strong>Slowly Changing Dimensions (SCD)</strong> — Patterns for updating records while either replacing or preserving historical values.</summary>
<p>SCD1 updates the matched record in place. SCD2 preserves history by closing the previous version and writing a new version.</p>
<p><strong>Also known as:</strong> SCD, slowly changing dimension</p>
</details>

</details>
