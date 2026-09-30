<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `widget_render_data_agreement`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.widgets.widget_render_data_agreement.widget_render_data_agreement`

Source path: `src/fabricops_kit/widgets/widget_render_data_agreement.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/widgets/widget_render_data_agreement.py)

Signature: `widget_render_data_agreement(*, spark: 'Any', context: 'dict[str, Any] | None' = None) -> 'dict[str, Any]'`

## Description

Render a wide, single-flow data-agreement editor.

## Parameters

spark : pyspark.sql.SparkSession
    Fabric Spark session used for initial metadata reads, explicit steward
    refreshes, and the final append-only write.
context : dict[str, Any], optional
    Advanced override for the active Fabric context. When omitted, the
    helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

## Return value

dict[str, Any]
    Stable root, section, field, document, steward, and save controls.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)
