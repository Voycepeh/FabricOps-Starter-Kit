# `versioning` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 5</span><span class="reference-chip">Internal helpers: 0</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

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
      <td>5</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>0</td>
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

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Callable</th>
      <th>Tier</th>
      <th>Type</th>
      <th>Summary</th>
      <th>Related helpers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/print_runtime_banner/"><code>print_runtime_banner</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Print the installed package version and matching documentation links in a notebook-friendly banner.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_docs_url/"><code>get_docs_url</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Return the published documentation URL for a package version.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_docs_version/"><code>get_docs_version</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Map a full package version to the matching major.minor documentation version.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_package_version/"><code>get_package_version</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Return the installed FabricOps Starter Kit package version for the active notebook runtime.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_release_notes_url/"><code>get_release_notes_url</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Return the patch-specific release notes URL for a package version.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>versioning</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/get_docs_url/"><code>get_docs_url</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/get_docs_version/"><code>get_docs_version</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/get_docs_version/"><code>get_docs_version</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/get_package_version/"><code>get_package_version</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/get_package_version/"><code>get_package_version</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/get_release_notes_url/"><code>get_release_notes_url</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/get_package_version/"><code>get_package_version</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/print_runtime_banner/"><code>print_runtime_banner</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/get_docs_url/"><code>get_docs_url</code></a>, <a class="reference-chip" href="../../reference/get_package_version/"><code>get_package_version</code></a>, <a class="reference-chip" href="../../reference/get_release_notes_url/"><code>get_release_notes_url</code></a>
</li>
</ul>
</section>

### Related internal helpers

No module-level internal helpers detected.

### External callers

None.
### External callees

None.
