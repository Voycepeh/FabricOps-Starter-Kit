# `io` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-internal">Internal-only module</span>
  <div class="api-chip-subtitle">Not intended as a primary user-facing API surface.</div>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 0</span><span class="reference-chip">Uses 1 external module</span><span class="reference-chip">Used by 0 external modules</span></div>

## Module purpose

Owns shared internal IO helpers used by one-function IO owner modules.

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
      <td><code>io</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns shared internal IO helpers used by one-function IO owner modules.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
      <td><code>io_core</code></td>
    </tr>
  </tbody>
</table>

## Public callables

No public exports in this module.

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>io</h5>
<h6>Public callables</h6>
<p>None.</p>
</section>

### Related internal helpers

No module-level internal helpers detected.

### External callers

None.
### External callees

**io_core**
<a class="reference-chip" href="io_core/#read_lakehouse_csv_core"><code>read_lakehouse_csv_core</code></a>, <a class="reference-chip" href="io_core/#read_lakehouse_excel_core"><code>read_lakehouse_excel_core</code></a>, <a class="reference-chip" href="io_core/#read_lakehouse_parquet_core"><code>read_lakehouse_parquet_core</code></a>, <a class="reference-chip" href="io_core/#read_lakehouse_table_core"><code>read_lakehouse_table_core</code></a>, <a class="reference-chip" href="io_core/#read_warehouse_query_core"><code>read_warehouse_query_core</code></a>, <a class="reference-chip" href="io_core/#read_warehouse_table_core"><code>read_warehouse_table_core</code></a>, <a class="reference-chip" href="io_core/#write_lakehouse_table_core"><code>write_lakehouse_table_core</code></a>, <a class="reference-chip" href="io_core/#write_warehouse_table_core"><code>write_warehouse_table_core</code></a>
