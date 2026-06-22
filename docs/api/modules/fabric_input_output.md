# `fabric_input_output` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 8</span><span class="reference-chip">Internal helpers: 0</span><span class="reference-chip">Uses 1 external module</span><span class="reference-chip">Used by 0 external modules</span></div>

## Module purpose

Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.

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
      <td><code>fabric_input_output</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns Fabric read/write helpers for Lakehouse, Warehouse, and file/table IO.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>8</td>
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
      <td><a href="../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read a CSV file from a configured Fabric lakehouse Files path.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read an Excel file from a configured Fabric lakehouse Files path.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read a Parquet path from a configured Fabric lakehouse Files path.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read a Delta table from a configured Fabric lakehouse target.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/read_warehouse_query/"><code>read_warehouse_query</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/read_warehouse_table/"><code>read_warehouse_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Read a table from a configured Fabric warehouse target.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write a Spark DataFrame to a configured Fabric lakehouse Delta table.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/write_warehouse_table/"><code>write_warehouse_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write a DataFrame to a configured Fabric warehouse target.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>fabric_input_output</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../reference/read_warehouse_query/"><code>read_warehouse_query</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../reference/read_warehouse_table/"><code>read_warehouse_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../reference/write_warehouse_table/"><code>write_warehouse_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
</ul>
</section>

### Related internal helpers

No module-level internal helpers detected.

### External callers

None.
### External callees

**io_core**
<a class="reference-chip" href="io_core/#read_lakehouse_csv_core"><code>read_lakehouse_csv_core</code></a>, <a class="reference-chip" href="io_core/#read_lakehouse_excel_core"><code>read_lakehouse_excel_core</code></a>, <a class="reference-chip" href="io_core/#read_lakehouse_parquet_core"><code>read_lakehouse_parquet_core</code></a>, <a class="reference-chip" href="io_core/#read_lakehouse_table_core"><code>read_lakehouse_table_core</code></a>, <a class="reference-chip" href="io_core/#read_warehouse_query_core"><code>read_warehouse_query_core</code></a>, <a class="reference-chip" href="io_core/#read_warehouse_table_core"><code>read_warehouse_table_core</code></a>, <a class="reference-chip" href="io_core/#write_lakehouse_table_core"><code>write_lakehouse_table_core</code></a>, <a class="reference-chip" href="io_core/#write_warehouse_table_core"><code>write_warehouse_table_core</code></a>
