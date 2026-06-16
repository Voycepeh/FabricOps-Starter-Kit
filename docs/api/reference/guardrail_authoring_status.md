# guardrail_authoring_status

Return lifecycle fields for guardrail rules under the effective table policy.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:1784`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L1784-L1809">View on GitHub</a>
</div>


## Signature

<div class="reference-api-definition" markdown="1">

```python
def guardrail_authoring_status(
    policy: Mapping[str, Any],
    bypass_reason: str='',
    actor: str | None=None,
    config: Any=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `policy` | `Mapping[str, Any]` | Yes | Effective table governance policy. |
| `bypass_reason` | `str` | No | User-entered justification when bypassing required approval. |
| `actor` | `str \| None` | No | Current user identifier. |
| `config` | `Any` | No | Runtime configuration used for timestamp formatting. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

## Raises / Errors

Not documented yet

## Relationships

### Used by

- `fabricops_kit.governance_review._base_guardrail_rule_record`

### Calls

- `fabricops_kit.metadata._now_utc_iso`
- `fabricops_kit.metadata._resolve_action_by`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    guardrail_authoring_status(...)
    ├── _now_utc_iso(...)
    │   └── _current_audit_timestamp(...)
    │       └── _get_audit_timezone(...)
    │           └── _validate_audit_timezone(...)
    └── _resolve_action_by(...)
        ├── _context_get(...)
        └── _runtime_context(...)
            └── _context_get(...)
    ```

??? info "Internal helpers used: 7"

    This callable uses 7 internal helpers for audit timestamp and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/config.py#L70-L76"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/config.py#L62-L67"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/config.py#L27-L59"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.guardrail_authoring_status`
- Short name: `guardrail_authoring_status`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1784`
- Inbound references count: 1
- Outbound references count: 2
- Used in templates: 02_pipeline
- Glossary terms: —

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail authoring`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- `fabricops_kit.governance_review._base_guardrail_rule_record`

### Outbound references

- `fabricops_kit.metadata._now_utc_iso`
- `fabricops_kit.metadata._resolve_action_by`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L1784-L1809">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7bbc85a74147bcfc02f1948a8bca8a640c1e15b8/src/fabricops_kit/governance_review.py#L1784-L1809</a>
- Start line: `1784`
- End line: `1809`
- Signature:

```python
def guardrail_authoring_status(
    policy: Mapping[str, Any],
    bypass_reason: str='',
    actor: str | None=None,
    config: Any=None,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation summary

- Internal helper count: 7
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## See also

No related guides documented.
