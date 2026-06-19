# widget_review_table_governance

Render 03-only formal review controls for enrichment and guardrail records.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2594`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2594-L2795">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use only in 03_governance for formal governance review decisions.

### Do not use when

- Do not use in 02_pipeline or for enforcement results; runtime results belong in METADATA_GUARDRAIL_RESULTS.

### Additional context

Renders the formal review workflow that reads and appends review history in METADATA_ENRICHMENT_RULES and METADATA_GUARDRAIL_RULES.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_table_governance(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    source_notebook_type: str='03_governance',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Selected table state containing enrichment and guardrail rule history. |
| `spark_session` | `Any` | No | Spark session used to append formal review outcomes. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |
| `source_notebook_type` | `str` | No | Notebook context. Formal review actions require ``03_governance``. |

## Returns

Widget controls and action helpers for formal governance review.

### Return interpretation

The widget returns controls and action helpers that append formal review rows to the enrichment or guardrail rule history tables.

## Raises / Errors

Not documented yet

### Common failure causes

- The notebook context is not 03_governance.
- No reviewable records are available.
- The metadata target cannot be written.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.governance_review._assert_governance_review_context`
- `fabricops_kit.governance_review._dq_rule_parameters_summary`
- `fabricops_kit.governance_review.apply_governance_enrichment_action`
- `fabricops_kit.governance_review.apply_governance_rule_action`
- `fabricops_kit.governance_review.load_rule_review_history`

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

    ```text
    widget_review_table_governance(...)
    ├── _assert_governance_review_context(...)
    ├── _dq_rule_parameters_summary(...)
    ├── apply_governance_enrichment_action(...)
    │   ├── _assert_governance_review_context(...)
    │   ├── _now_utc_iso(...)
    │   │   └── _current_audit_timestamp(...)
    │   │       └── _get_audit_timezone(...)
    │   │           └── _validate_audit_timezone(...)
    │   ├── _record_identity(...)
    │   └── _resolve_action_by(...)
    │       ├── _context_get(...)
    │       └── _runtime_context(...)
    │           └── _context_get(...)
    ├── apply_governance_rule_action(...)
    │   ├── _assert_governance_review_context(...)
    │   ├── _now_utc_iso(...)
    │   │   └── _current_audit_timestamp(...)
    │   │       └── _get_audit_timezone(...)
    │   │           └── _validate_audit_timezone(...)
    │   ├── _record_identity(...)
    │   └── _resolve_action_by(...)
    │       ├── _context_get(...)
    │       └── _runtime_context(...)
    │           └── _context_get(...)
    ├── load_rule_review_history(...)
    └── resolve_fabric_context(...)
        └── get_default_fabric_context(...)
    ```

??? info "Internal helpers used: 10"

    This callable uses 10 internal helpers for audit timestamp, metadata loading, rule evaluation, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1723-L1725"><code>_record_identity</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L780-L795"><code>_dq_rule_parameters_summary</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1650-L1653"><code>_assert_governance_review_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_table_governance`
- Short name: `widget_review_table_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2594`
- Inbound references count: 0
- Outbound references count: 6
- Used in templates: 03_governance
- Glossary terms: guardrails, metadata lakehouse, notebook template

### Implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Review table governance`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Widget controls and action helpers for formal governance review.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.governance_review._assert_governance_review_context`
- `fabricops_kit.governance_review._dq_rule_parameters_summary`
- `fabricops_kit.governance_review.apply_governance_enrichment_action`
- `fabricops_kit.governance_review.apply_governance_rule_action`
- `fabricops_kit.governance_review.load_rule_review_history`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2594-L2795">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2594-L2795</a>
- Start line: `2594`
- End line: `2795`
- Signature:

```python
def widget_review_table_governance(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    source_notebook_type: str='03_governance',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="widget_select_guardrail_target/"><code>fabricops_kit.governance_review.widget_select_guardrail_target</code></a>
- <a href="widget_enrich_table_metadata/"><code>fabricops_kit.governance_review.widget_enrich_table_metadata</code></a>
- <a href="widget_author_guardrail_rules/"><code>fabricops_kit.governance_review.widget_author_guardrail_rules</code></a>

### Internal implementation summary

- Internal helper count: 10
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>
- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
