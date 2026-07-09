<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.1.0

- Package version: `0.1.0`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: Not specified
- [GitHub Release](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.1.0)

## Why this release exists

FabricOps 0.1.0 establishes the first supported foundation for governed Microsoft Fabric notebook projects. It focuses on reliable Fabric input and output, dataframe profiling, agreement-driven metadata, and lightweight exploration workflows.

## Live in this release

<div class="fabricops-release-card-grid">
<a class="fabricops-release-card" href="functions/"><strong>9</strong><span>Live functions</span></a>
<a class="fabricops-release-card" href="metadata/"><strong>4</strong><span>Live metadata tables</span></a>
<a class="fabricops-release-card" href="templates/"><strong>3</strong><span>Live notebook templates</span></a>
</div>

## Downloads

- [Download wheel](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/download/v0.1.0/fabricops_kit-0.1.0-py3-none-any.whl)
- [Download source distribution](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/download/v0.1.0/fabricops_kit-0.1.0.tar.gz)
- [Download notebook pack](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/download/v0.1.0/fabricops-kit-0.1.0-notebooks.zip)
- [View GitHub Release](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.1.0)
- Verify downloads with [SHA256SUMS](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/download/v0.1.0/SHA256SUMS.txt)

## Get started

1. Download and install the wheel.
2. Download the released notebook pack.
3. Run `00_env_config`.
4. Run `01_agreement`.
5. Use `99_explore` for supported exploration.

## Known limitations

The pipeline execution workflow, governance review workflow, DQ rule authoring and enforcement, and notebook registry remain Preview and are not part of the supported frozen release surface for 0.1.0.

## Release notes

### Added

- Established the first supported FabricOps Starter Kit release surface for governed Microsoft Fabric notebook projects.
- Shipped Live Fabric input/output helpers, dataframe profiling support, agreement-driven metadata tables, and the supported `00_env_config`, `01_agreement`, and `99_explore` notebook templates.
- Published the release lifecycle manifest used to separate Live release assets from Preview capabilities.

### Known limitations

- Pipeline execution, governance review, DQ rule authoring and enforcement, and notebook registry capabilities remain Preview in this release.

### Upgrade instructions

- This is the first supported release; no prior supported release upgrade is required.
