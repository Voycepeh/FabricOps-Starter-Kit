# FabricOps mascot and storyboard

Reusable transparent vector art for the FabricOps Remotion video and selected guided demo documentation. This asset set is deliberately independent of the existing Part 2 scene implementation.

## Design language

Charcoal and near-black shell, bright teal outlines and cyan facial glow. Keep the original FabricOps navy backgrounds and orange production emphasis. The same silhouette is used across poses. No third-party branding or generated raster text is embedded.

## Scene storyboard

| Sequence | Human and mascot action | Product claim |
| --- | --- | --- |
| 1. Define | Human states a business rule and identifies a sensitive field; robot listens. | Governance begins with human decisions. |
| 2. Author | Robot illustrates an optional AI-assisted suggestion: `modified_datetime >= order_datetime`; human reviews rule and masking treatment. | Executable rules remain human-reviewed. |
| 3. Enforce | Robot scans illustrative data rows; one passes and one fails. A separate downstream field is masked. | Guardrails evaluate data, they do not autonomously repair failing records. |
| 4. Engineer | Robot accompanies governed read and write, with project-owned PySpark in the middle. | FabricOps orchestrates repeatable engineering boundaries. |
| 5. Promote | DEV and PROD robots follow the same 02 Pipeline, resolving different Fabric Store locations through 00 Env Config. | Validated pipeline definition promotes unchanged. |
| 6. Consume | Approved Production data supports dashboards, data agents, applications and ML models. | Consumption is enabled, not auto-generated. |

## Asset manifest

* `robot-neutral.svg`: neutral
* `robot-pointing.svg`: pointing
* `robot-writing.svg`: writing
* `robot-scanning.svg`: scanning
* `robot-masking.svg`: masking
* `robot-carrying.svg`: carrying
* `robot-dev.svg`: dev
* `robot-prod.svg`: prod

All assets have a transparent canvas, common viewBox dimensions and accessible labels. Remotion can reference them through `staticFile('mascot/robot-neutral.svg')` when placed under `public/mascot`.

## Suggested documentation placement

Use a small, restrained mascot illustration at the Guided Demo overview, Step 2 pipeline, Step 3 contract authoring, Step 4 validation, and Steps 5–6 promotion/execution. Step 7 may reuse the pointing pose near consumption links. Avoid decorating API reference pages and avoid repeating a large illustration on every page. Introduce these placements in a separate focused documentation PR.

## Remotion implementation note

Treat SVGs as illustrative pose assets. Keep diagram connectors, title text, code, sample data, timing and animated labels as editable Remotion elements. Avoid reintroducing two-column feature-card layouts. Hold stable frames for readability. Do not conflate optional authoring AI with deterministic runtime enforcement.
