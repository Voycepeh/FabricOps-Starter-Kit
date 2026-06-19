# widget_author_guardrail_rules

Render combined guardrail authoring controls for the selected table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2557`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2557-L2591">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use after selecting a target in 03_governance when governance users need to create guardrail records.

### Do not use when

- Do not use for formal approve, reject, replace, or deactivate decisions; use widget_review_table_governance.

### Additional context

Renders the existing guardrail authoring widgets together so guardrail creation remains separate from formal governance review.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_author_guardrail_rules(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    source_notebook_type: str='03_governance',
    created_by_role: str='governance',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Handover state from :func:`widget_select_guardrail_target`. |
| `spark_session` | `Any` | No | Spark session used for saves. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |
| `source_notebook_type` | `str` | No | Notebook type stamped on authored records. |
| `created_by_role` | `str` | No | Role stamped on authored records. |

## Returns

Combined widget states for schema/freshness/profile and DQ authoring.

### Return interpretation

The helper returns child widget states whose saves append guardrail intent to METADATA_GUARDRAIL_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- No target state is selected.
- Rule parameters are invalid.
- The metadata target cannot be written.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- <a href="widget_author_dq_rules/"><code>fabricops_kit.governance_review.widget_author_dq_rules</code></a>
- <a href="widget_author_schema_freshness_profile_rules/"><code>fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules</code></a>

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Tree is truncated to keep the page readable.

    Unique internal helpers: 27. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><a href="widget_author_guardrail_rules/"><code>widget_author_guardrail_rules(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="widget_author_dq_rules/"><code>widget_author_dq_rules(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2280-L2316"><code>_dq_records_from_selection(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1941-L1954"><code>_latest_rule(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1957-L1963"><code>_rule_params(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1966-L1977"><code>_write_rule_records(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1941-L1954"><code>_latest_rule(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1957-L1963"><code>_rule_params(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2063-L2130"><code>_schema_freshness_profile_records_from_selection(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1966-L1977"><code>_write_rule_records(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span>…</div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row reference-call-tree-more" role="treeitem"><span class="reference-call-tree-prefix">        └── </span>…</div>
    </div>


<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_author_guardrail_rules`
- Short name: `widget_author_guardrail_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2557`
- Inbound references count: 0
- Outbound references count: 3
- Used in templates: 03_governance
- Glossary terms: guardrails, metadata lakehouse, notebook template

### Implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Author guardrail rules`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Combined widget states for schema/freshness/profile and DQ authoring.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- <a href="widget_author_dq_rules/"><code>fabricops_kit.governance_review.widget_author_dq_rules</code></a>
- <a href="widget_author_schema_freshness_profile_rules/"><code>fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2557-L2591">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2557-L2591</a>
- Start line: `2557`
- End line: `2591`
- Signature:

```python
def widget_author_guardrail_rules(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    source_notebook_type: str='03_governance',
    created_by_role: str='governance',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="widget_author_schema_freshness_profile_rules/"><code>fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules</code></a>
- <a href="widget_author_dq_rules/"><code>fabricops_kit.governance_review.widget_author_dq_rules</code></a>
- <a href="widget_review_table_governance/"><code>fabricops_kit.governance_review.widget_review_table_governance</code></a>

### Internal implementation summary

- Internal helper count: 27
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>
- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
