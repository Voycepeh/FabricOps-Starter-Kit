# widget_review_table_guardrails

Render shared schema, freshness, profile-behavior, and DQ guardrail authoring guidance.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:836`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L836-L952">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 02_pipeline for engineering first-pass guardrails and in 03_governance for governance review before record_table_governance persists guardrail_reviews.

**Additional context:**

Renders shared guardrail authoring so engineering and governance can append schema, freshness, profile-behavior, and DQ rule metadata.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_table_guardrails(
    profile_rows: list[dict[str, Any]],
    existing_rules: list[dict[str, Any]] | None=None,
    author_role: str='governance',
    default_review_status: str | None=None,
    source_notebook_type: str='03_governance',
) -> list[dict[str, Any]]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `profile_rows` | `list[dict[str, Any]]` | Yes | Selected table profile rows used to identify environment, dataset, table, and available columns for new guardrail rules. |
| `existing_rules` | `list[dict[str, Any]] \| None` | No | Previously persisted guardrail rows for the selected table. The widget displays these rows as review context; updates are persisted as new append-only rows in ``METADATA_GUARDRAIL_RULES``. |
| `author_role` | `str` | No | Role stamped on queued guardrail rows. Use ``"engineering"`` from ``02_pipeline`` and ``"governance"`` from ``03_governance``. |
| `default_review_status` | `str \| None` | No | Initial workflow status for queued rows. Engineering defaults to ``"proposed"``; governance defaults to ``"governance_approved"``. |
| `source_notebook_type` | `str` | No | Notebook type stamped on queued rows. |

## Returns

list[dict[str, Any]]
    Mutable review list. Queue draft, proposed, engineer-approved,
    governance-approved, rejected, superseded, or inactive guardrail rows and
    pass the list to ``record_table_governance(guardrail_reviews=...)`` to
    append them to ``METADATA_GUARDRAIL_RULES``.

### Return interpretation

The widget captures committed guardrail review rows for METADATA_GUARDRAIL_RULES; runtime enforcement still happens only in 02_pipeline.

## Raises / Errors

Not documented yet

### Common failure causes

- Profile rows are missing.
- Changing data was selected without a watermark column.
- Unsupported guardrail status or severity was selected.
- Widget state was not committed through record_table_governance.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.governance_review._build_guardrail_rule_records`
- `fabricops_kit.governance_review._value`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`
- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

This shared widget supports ``schema``, ``freshness``,
``profile_behavior``, and ``dq`` guardrail categories. If ``data_change_choice``
is ``"changing data"``, queued rows must include ``watermark_column``.
Runtime enforcement remains owned by ``02_pipeline``; ``03_governance`` only
authors, reviews, approves, rejects, supersedes, or inactivates metadata.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    widget_review_table_guardrails(...)
    ├── _build_guardrail_rule_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   ├── _build_dq_rule_key(...)
    │   │   └── …
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _guardrail_parameter_payload(...)
    │   │   └── …
    │   ├── _json(...)
    │   ├── _normalize_guardrail_review_status(...)
    │   ├── _normalize_guardrail_severity(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    └── _value(...)
    ```

??? info "Internal helpers used: 26"

    This callable uses 26 internal helpers for audit timestamp, metadata loading, rule parsing, rule evaluation, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L149-L222"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/config.py#L70-L76"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/config.py#L62-L67"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/config.py#L27-L59"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L542-L612"><code>_build_guardrail_rule_records</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L83-L84"><code>_build_metadata_column_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L79-L80"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L485-L507"><code>_dq_rule_parameter_payload</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L531-L539"><code>_guardrail_parameter_payload</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L74-L76"><code>_stable_metadata_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L1493-L1566"><code>_validate_dq_rules</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L86-L87"><code>_canonical_dq_rule_type</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L699-L704"><code>_json</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L511-L518"><code>_normalize_guardrail_review_status</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L521-L528"><code>_normalize_guardrail_severity</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L87-L88"><code>_build_dq_rule_key</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L96-L108"><code>_approved_column_identity</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L90-L93"><code>_approved_review_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L103-L115"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L63-L64"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L67-L71"><code>_resolve_action_by</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L122-L146"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/metadata.py#L118-L119"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L78-L79"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_table_guardrails`
- Short name: `widget_review_table_guardrails`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `836`
- Inbound references count: 0
- Outbound references count: 2
- Used in templates: 02_pipeline, 03_governance
- Glossary terms: guardrail, metadata lakehouse, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected table profile rows used to identify environment, dataset, table,
    and available columns for new guardrail rules.
existing_rules : list of dict, optional
    Previously persisted guardrail rows for the selected table. The widget
    displays these rows as review context; updates are persisted as new
    append-only rows in ``METADATA_GUARDRAIL_RULES``.
author_role : {"engineering", "governance"}, default="governance"
    Role stamped on queued guardrail rows. Use ``"engineering"`` from
    ``02_pipeline`` and ``"governance"`` from ``03_governance``.
default_review_status : str, optional
    Initial workflow status for queued rows. Engineering defaults to
    ``"proposed"``; governance defaults to ``"governance_approved"``.
source_notebook_type : str, default="03_governance"
    Notebook type stamped on queued rows.
- **output:** list[dict[str, Any]]
    Mutable review list. Queue draft, proposed, engineer-approved,
    governance-approved, rejected, superseded, or inactive guardrail rows and
    pass the list to ``record_table_governance(guardrail_reviews=...)`` to
    append them to ``METADATA_GUARDRAIL_RULES``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._build_guardrail_rule_records`
- `fabricops_kit.governance_review._value`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L836-L952">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e6766f0a6882345999f458d924a400acd3720fbf/src/fabricops_kit/governance_review.py#L836-L952</a>
- Start line: `836`
- End line: `952`
- Signature:

```python
def widget_review_table_guardrails(
    profile_rows: list[dict[str, Any]],
    existing_rules: list[dict[str, Any]] | None=None,
    author_role: str='governance',
    default_review_status: str | None=None,
    source_notebook_type: str='03_governance',
) -> list[dict[str, Any]]:
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 26
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)
- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
