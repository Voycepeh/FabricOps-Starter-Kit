# Function Usage Guide

Use this page to understand how notebook templates map to the main public callables.

## Start from the templates

<table class="reference-template-table">
  <thead>
    <tr>
      <th>Notebook</th>
      <th>Guided usage</th>
      <th>Full template</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Notebook"><code>00_env_config</code></td>
      <td data-label="Guided usage">Shared environment bootstrap and validation before exploration or pipeline notebooks run.<br><a href="../notebook-structure/00-env-config/">View guided structure</a></td>
      <td data-label="Full template"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb">Open notebook</a></td>
    </tr>
    <tr>
      <td data-label="Notebook"><code>01_da_&lt;agreement&gt;</code></td>
      <td data-label="Guided usage">Captures approved usage, business context, stewardship notes, DQ approvals, governance approvals, and agreement-level controls reused by exploration and pipeline notebooks.<br><a href="../notebook-structure/01-data-sharing-agreement/">View guided structure</a></td>
      <td data-label="Full template"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_da_agreement_template.ipynb">Open notebook</a></td>
    </tr>
    <tr>
      <td data-label="Notebook"><code>02_ex_&lt;agreement&gt;_&lt;topic&gt;</code></td>
      <td data-label="Guided usage">Exploration notebook flow used to profile source data and draft advisory AI outputs for human review.<br><a href="../notebook-structure/02-exploration/">View guided structure</a></td>
      <td data-label="Full template"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_ex_agreement_topic.ipynb">Open notebook</a></td>
    </tr>
    <tr>
      <td data-label="Notebook"><code>03_pc_&lt;agreement&gt;_&lt;pipeline&gt;</code></td>
      <td data-label="Guided usage">Pipeline notebook flow for deterministic enforcement and controlled publishing.<br><a href="../notebook-structure/03-pipeline-contract/">View guided structure</a></td>
      <td data-label="Full template"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_pc_agreement_pipeline_template.ipynb">Open notebook</a></td>
    </tr>
  </tbody>
</table>

## What runs where

- `00_env_config` is shared setup.
- `01_data_sharing_agreement` is the governance source of truth.
- `02_ex` proposes evidence and AI-assisted suggestions.
- `03_pc` loads approved metadata and enforces controls.

AI functions are advisory. Approved contracts and pipeline notebooks are the enforcement point.

