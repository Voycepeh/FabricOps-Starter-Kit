# record_table_governance

Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:1062`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L1062-L1164">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use after reviewers approve governance rows in 03_governance and those approvals should become metadata-backed evidence.

**Do not use when:**

- Do not use to draft governance recommendations, bypass review approval, or write unapproved rows.

**Additional context:**

Persists approved column context, DQ rules, and classification records for a selected table in one governance commit action.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def record_table_governance(
    config: Any,
    env: str,
    profile_rows: list[dict[str, Any]],
    spark_session: Any,
    context_reviews: list[dict[str, Any]] | None=None,
    dq_rule_reviews: list[dict[str, Any]] | None=None,
    classification_reviews: list[dict[str, Any]] | None=None,
    approved_by: str | None=None,
    governance_selection: dict[str, Any] | None=None,
    write_governance_review: bool=False,
    mode: str='append',
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
written = record_table_governance(CONFIG, env, profile_rows, spark_session=spark, context_reviews=context_rows, dq_rule_reviews=dq_rows, classification_reviews=classification_rows, approved_by="reviewer")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `Any` | Yes | Shared ``00_env_config`` configuration that routes metadata writes to the configured metadata lakehouse target. |
| `env` | `str` | Yes | Environment key in ``config``. |
| `profile_rows` | `list[dict[str, Any]]` | Yes | Column-profile rows loaded for the selected catalogue table. |
| `spark_session` | `Any` | Yes | Spark session used to create DataFrames for metadata writes. |
| `context_reviews` | `list[dict[str, Any]] \| None` | No | Human-approved rows from the governance review workflow. Only rows with ``review_status="approved"`` and ``commit=True`` are written. |
| `dq_rule_reviews` | `list[dict[str, Any]] \| None` | No | Not documented yet |
| `classification_reviews` | `list[dict[str, Any]] \| None` | No | Not documented yet |
| `approved_by` | `str \| None` | No | Reviewer identity to stamp on records. When omitted, runtime defaults are used. |
| `governance_selection` | `dict[str, Any] \| None` | No | Catalogue selection used to re-read persisted evidence and write a final governance outcome row. |
| `write_governance_review` | `bool` | No | Whether to append a ``METADATA_GOVERNANCE_REVIEWS`` outcome row after checking agreement, pipeline, schema/profile, and DQ evidence. |
| `mode` | `str` | No | Write mode for metadata table commits. |

## Returns

Dictionary of records written for column_context, dq_rules, and column_classification.

### Return interpretation

The returned dictionary groups written records by metadata area. Confirm counts match approved review rows before treating governance as complete.

## Raises / Errors

Raises configuration, validation, Spark, or metadata-write errors when approved records cannot be built or persisted.

### Common failure causes

- Review rows are not approved.
- Required profile context is missing.
- Metadata routing is unavailable.
- Spark cannot write one of the governance metadata tables.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.governance_review._build_classification_records`
- `fabricops_kit.governance_review._build_column_context_records`
- `fabricops_kit.governance_review._build_dq_rule_records`
- `fabricops_kit.governance_review._review_governance_evidence`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `03_governance`

**Side effects:**

Writes approved governance metadata records to configured metadata tables.

**Notes:**

This is the v1 governance commit action for ``03_governance`` notebooks. It merges
the previous row-builder and per-table commit helpers into one explicit
human approval step while preserving configured metadata lakehouse routing.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    record_table_governance(...)
    ├── _build_classification_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   └── _json(...)
    ├── _build_column_context_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   └── _json(...)
    ├── _build_dq_rule_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   ├── _build_dq_rule_key(...)
    │   │   └── …
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _dq_rule_parameter_payload(...)
    │   ├── _json(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _configured_lakehouse_schema(...)
    │   ├── _get_store(...)
    │   │   └── …
    │   └── _normalize_schema_name(...)
    ├── _review_governance_evidence(...)
    │   ├── _build_metadata_table_key(...)
    │   │   └── …
    │   ├── _build_runtime_audit_fields(...)
    │   │   └── …
    │   ├── _configured_lakehouse_schema(...)
    │   │   └── …
    │   ├── _latest_row(...)
    │   │   └── …
    │   ├── _now_utc_iso(...)
    │   │   └── …
    │   ├── _read_metadata_rows(...)
    │   │   └── …
    │   ├── _resolve_action_by(...)
    │   │   └── …
    │   ├── _status_is_failed(...)
    │   ├── _status_is_warning(...)
    │   ├── _value(...)
    │   ├── load_catalogue_profile_rows(...)
    │   │   └── …
    │   └── write_lakehouse_table(...)
    │       └── …
    └── write_lakehouse_table(...)
        ├── _get_store(...)
        │   └── …
        ├── _normalize_table_name(...)
        └── _resolve_lakehouse_table_path(...)
            └── …
    ```

??? info "Internal helpers used: 33"

    This callable uses 33 internal helpers for audit timestamp, metadata loading, rule parsing, rule evaluation, result summary, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L147-L219"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L69-L75"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L61-L66"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L895-L899"><code>_latest_row</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L27-L58"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L81-L82"><code>_build_metadata_column_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L77-L78"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/fabric_input_output.py#L152-L165"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L472-L494"><code>_dq_rule_parameter_payload</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L910-L911"><code>_read_metadata_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L72-L74"><code>_stable_metadata_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L1230-L1303"><code>_validate_dq_rules</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L78-L79"><code>_canonical_dq_rule_type</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L573-L578"><code>_json</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L627-L667"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/fabric_input_output.py#L105-L116"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L85-L86"><code>_build_dq_rule_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L497-L548"><code>_build_dq_rule_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Result summary</h4>
        <p>Build final statuses, counts, and messages for the caller.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L902-L903"><code>_status_is_failed</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L906-L907"><code>_status_is_warning</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/config.py#L670-L708"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L88-L100"><code>_approved_column_identity</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L82-L85"><code>_approved_review_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L550-L571"><code>_build_classification_records</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L456-L469"><code>_build_column_context_records</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L101-L113"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L61-L62"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L65-L69"><code>_resolve_action_by</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L914-L1060"><code>_review_governance_evidence</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L120-L144"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/metadata.py#L116-L117"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.record_table_governance`
- Short name: `record_table_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1062`
- Inbound references count: 0
- Outbound references count: 6
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, metadata lakehouse, guardrail

### AI implementation contract

- **required_context:** Requires 03_governance profile rows and 00_env_config metadata routing; governance metadata must be written to the configured metadata target.
- **inputs:** config, env, profile_rows, spark_session, optional approved context/DQ/classification review rows, approved_by, and mode.
- **output:** Dictionary of records written for column_context, dq_rules, and column_classification.
- **side_effects:** Writes approved governance metadata records to configured metadata tables.
- **failure_modes:** Raises configuration, validation, Spark, or metadata-write errors when approved records cannot be built or persisted.
- **verification:** Verify review_status is approved and commit is true for intended rows before calling; confirm returned record groups match expected approvals.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.governance_review._build_classification_records`
- `fabricops_kit.governance_review._build_column_context_records`
- `fabricops_kit.governance_review._build_dq_rule_records`
- `fabricops_kit.governance_review._review_governance_evidence`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L1062-L1164">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad2fcc19aa4b83b0f36592c2535bd0207c4c6158/src/fabricops_kit/governance_review.py#L1062-L1164</a>
- Start line: `1062`
- End line: `1164`
- Signature:

```python
def record_table_governance(
    config: Any,
    env: str,
    profile_rows: list[dict[str, Any]],
    spark_session: Any,
    context_reviews: list[dict[str, Any]] | None=None,
    dq_rule_reviews: list[dict[str, Any]] | None=None,
    classification_reviews: list[dict[str, Any]] | None=None,
    approved_by: str | None=None,
    governance_selection: dict[str, Any] | None=None,
    write_governance_review: bool=False,
    mode: str='append',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation summary

- Internal helper count: 33
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
