# `versioning` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Module pages document source modules and internal helpers for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable surface.

The public v1 callable surface is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 5</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns runtime package-version detection and documentation link helpers for Fabric notebooks.

## Module manifest

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Module name</td>
      <td><code>versioning</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns runtime package-version detection and documentation link helpers for Fabric notebooks.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td>—</td>
    </tr>
  </tbody>
</table>

## Public callables

No public exports in this module.

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>versioning</h5>
<h6>Public callables</h6>
<p>None.</p>
</section>

### Related internal helpers

<details>
<summary>Show internal helpers</summary>

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Helper</th>
      <th>Related public callables</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/internal/versioning/_get_docs_url/"><code>_get_docs_url</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/versioning/_get_docs_version/"><code>_get_docs_version</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/versioning/_get_package_version/"><code>_get_package_version</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/versioning/_get_release_notes_url/"><code>_get_release_notes_url</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/versioning/_print_runtime_banner/"><code>_print_runtime_banner</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_get_docs_url"><code>_get_docs_url</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_docs_version"><code>_get_docs_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_docs_version"><code>_get_docs_version</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_package_version"><code>_get_package_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_package_version"><code>_get_package_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_release_notes_url"><code>_get_release_notes_url</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_package_version"><code>_get_package_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_print_runtime_banner"><code>_print_runtime_banner</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_docs_url"><code>_get_docs_url</code></a>, <a class="reference-chip" href="#_get_package_version"><code>_get_package_version</code></a>, <a class="reference-chip" href="#_get_release_notes_url"><code>_get_release_notes_url</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

None.
