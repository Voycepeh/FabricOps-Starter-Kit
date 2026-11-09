# `observe_source_drift`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Observe every previously read physical source against accepted pipeline history.


## Usage notes

After all Reads and before transformation, when historical source changes should be observed.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
result = observe_source_drift(observe_immediately=True, source_observation_days=1, block=True)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def observe_source_drift(
    observe_immediately: bool=True,
    source_observation_days: int | None=1,
    block: bool=True,
) -> dict:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `observe_immediately` | `bool` | No | `True` | Observe immediately: True forces a check now; False uses the interval. An interval skip is reported as skipped, never passed. |
| `source_observation_days` | `int \| None` | No | `1` | Observe every day(s): positive integer interval since the last accepted snapshot. None requests observation on each call. Booleans are invalid. |
| `block` | `bool` | No | `True` | Block write: stop execution after reporting all failures. False returns warnings and permits continuation, including when evaluation is unavailable. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
result = observe_source_drift(block=True, observe_immediately=True)
scheduled = observe_source_drift(observe_immediately=False, source_observation_days=1)
```

</div>

## Returns

dict
    Pipeline and execution IDs, status, can_continue, blocking policy,
    per-source counts/reasons and scoped investigation queries. Counts include
    added, modified, removed and ambiguous historical rows. Without validated
    unique keys, added/missing content is exact but modifications are unknown;
    ambiguous counts describe missing content and overlap removed counts.

## Raises / Errors

ValueError
    If controls are invalid.
RuntimeError
    If no pipeline is active, or blocking observation detects historical
    changes or cannot evaluate a source. All sources are attempted and
    diagnostics are persisted and printed before a blocking exception.

## Notes

<div class="reference-docstring-notes" markdown="1">

Requires Spark and configured metadata access. A full-source scan and retained
identity/hash multiplicities cost compute and metadata storage proportional to
distinct source content. No raw business values are persisted. Observation
captures candidates; successful Finalize and verified required publications
accept them. A successful nonblocking run with completed evaluation accepts its new snapshot, retaining
warning diagnostics. Failed, blocked, partial or stale concurrent runs do not
advance history. Dry Run never persists or accepts snapshots. Existing aggregate
fingerprints cannot prove historical row identity: a clean successful run must
establish the first exact snapshot. Observation does not repair source data.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Call after all orchestrate_read calls and before transformation and Write.
Full and Incremental Read both observe the complete physical source, once
per canonical Table ID per call. Sources read later are not covered. This
optional function works without Data Contracts and with every Write Mode.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/observe_source_drift.py:17`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/observe_source_drift.py#L17-L196">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |


</details>
