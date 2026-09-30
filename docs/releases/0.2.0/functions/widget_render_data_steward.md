<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `widget_render_data_steward`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.widgets.widget_render_data_steward.widget_render_data_steward`

Source path: `src/fabricops_kit/widgets/widget_render_data_steward.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/widgets/widget_render_data_steward.py)

Signature: `widget_render_data_steward(*, spark: 'Any', context: 'dict[str, Any] | None' = None) -> 'dict[str, Any]'`

## Description

Render append-only data steward create/update maintenance.

## Parameters

spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads and append-only writes.
context : dict[str, Any], optional
    Advanced override for the active Fabric context. When omitted, the
    helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

## Return value

dict[str, Any]
    Rendered widget controls keyed for notebook customization.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)
