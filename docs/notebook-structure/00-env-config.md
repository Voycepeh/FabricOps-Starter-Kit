# `00_env_config`

Use this page to understand the purpose and segment flow of this notebook template. Each segment shows the typical callables commonly used there.

Shared environment bootstrap and validation before exploration or pipeline notebooks run.

> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb">Open template notebook</a>

> `00_env_config` is shared setup.

## Segment 1: Explain the shared environment role

Describe what this shared config notebook sets up and what downstream exploration or pipeline notebooks depend on.

## Segment 2: Define environment targets and notebook policy

<table class="reference-function-table notebook-structure-function-table">
  <thead>
    <tr>
      <th>Callable</th>
      <th>Module</th>
      <th>Why it is commonly used here</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/FabricStore/"><code>FabricStore</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a></td>
      <td data-label="Why it is commonly used here">Fabric lakehouse or warehouse connection details.</td>
    </tr>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/load_config/"><code>load_config</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a></td>
      <td data-label="Why it is commonly used here">Validate and return a user-supplied framework configuration.</td>
    </tr>
  </tbody>
</table>

## Segment 3: Set AI, quality, governance, and lineage defaults

## Segment 4: Assemble and validate framework config

<table class="reference-function-table notebook-structure-function-table">
  <thead>
    <tr>
      <th>Callable</th>
      <th>Module</th>
      <th>Why it is commonly used here</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/load_config/"><code>load_config</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a></td>
      <td data-label="Why it is commonly used here">Validate and return a user-supplied framework configuration.</td>
    </tr>
  </tbody>
</table>

## Segment 5: Run startup checks and show resolved paths

<table class="reference-function-table notebook-structure-function-table">
  <thead>
    <tr>
      <th>Callable</th>
      <th>Module</th>
      <th>Why it is commonly used here</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Callable"><a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a></td>
      <td data-label="Module"><a class="reference-module-link" href="../../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a></td>
      <td data-label="Why it is commonly used here">Run consolidated FabricOps startup for exploration and pipeline notebooks.</td>
    </tr>
  </tbody>
</table>

