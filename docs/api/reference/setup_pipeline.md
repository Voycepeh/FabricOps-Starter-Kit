# `setup_pipeline`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.3.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Start Dry Run or explicit-ID Ungoverned execution; Governed fails closed pending deployment verification.


## Usage notes

Call after setup_notebook() and before Read, Transform and Write. Persistent execution requires an explicit saved Pipeline ID.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
context = setup_notebook()
pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Ungoverned")
preview = setup_pipeline(pipeline_mode="Dry Run")
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_pipeline(
    *,
    pipeline_id: str | None=None,
    pipeline_mode: str='Ungoverned',
    observe_source: bool=False,
    source_observation_days: int | None=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `pipeline_id` | `str \| None` | No | `None` | Canonical lowercase UUIDv4 kept in version-controlled pipeline source, stable across environments and notebook deployments. Required for Ungoverned and Governed. Dry Run may allocate a session-only ID. |
| `pipeline_mode` | `str` | No | `'Ungoverned'` | Preview, publish without governance, or enforce activated governance. |
| `observe_source` | `bool` | No | `False` | Manually request a full physical Source Observation for this execution. |
| `source_observation_days` | `int \| None` | No | `None` | Automatically observe after this many days since the last accepted full observation. None disables automatic observation. Manual requests override the interval. Incremental SQL scope does not restrict observation. Baselines are accepted only with verified target publication; failed or no-op writes do not consume the interval. Changed fingerprints are diagnostic unless a separately configured Source Drift policy blocks publication. |

</div>

## Returns

PipelineSession
    Context-local Read/Write execution and in-memory report. Call
    finalize_pipeline after every Read, transformation and Write completes.

### Return interpretation

Returns a context-local Dry Run/Ungoverned session exposing the explicit Pipeline ID, optional Dry Run Contract preview and execution reporting. finalize_pipeline records completion; interrupted runs remain incomplete. Governed is blocked pending trusted deployment verification.

## Raises / Errors

ValueError
    If the mode or Pipeline ID is invalid, or a persistent ID is omitted.
RuntimeError
    If notebook setup or Spark is unavailable, or Governed deployment
    verification has not been established. Governed fails before admission
    and publication; a caller-supplied Git SHA cannot authorize it.

### Common failure causes

- Missing, failed or outdated setup_notebook() initialization.
- Invalid frozen contract selections.
- Missing explicit persistent Pipeline ID or pending Governed deployment verification.

## Notes

<div class="reference-docstring-notes" markdown="1">

Call setup_notebook first. Spark and Fabric identity come from that setup.
There is no permanent registration, approval, notebook rebinding or automatic
UUID recovery. A notebook may use different explicit Pipeline IDs. Repeated
setup closes the previous execution. Dry Run never writes Registry, Run,
profiling results or Processing State. Persistent runs record final outcomes;
a successful Write does not imply successful whole-notebook completion.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Dry Run previews transformations, optional Contract checks and profiling without
durable mutations. Ungoverned publishes without activated Contracts, but cannot
write protected Table IDs or physical destination aliases. Governed requires
activated deployment and independently activated table Contracts. It currently
fails closed until trusted deployment verification is proven and integrated.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/setup_pipeline.py:130`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/setup_pipeline.py#L130-L205">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.3.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 15 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.3.0 |
| Live | 0.3.1 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.activated_pipeline.shared.build_governed_pipeline_plan</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.resolve_runtime_context</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.pipeline.shared._row_to_dict</code></li>
<li><code>fabricops_kit.pipeline.shared.close_current_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.start_pipeline_session</code></li>
<li><code>fabricops_kit.pipeline.shared.validate_pipeline_id</code></li>
<li><code>fabricops_kit.widgets.shared._html_escape</code></li>
<li><code>fabricops_kit.widgets.shared.form_page</code></li>
<li><code>fabricops_kit.widgets.shared.require_ipywidgets</code></li>
</ul>


</details>
