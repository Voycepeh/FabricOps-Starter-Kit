# widget_pipeline_bootstrap

??? info "Downstream callables: 58"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[widgets/widget_pipeline_bootstrap.py]</span> <span class="reference-call-tree-type">[public callable]</span> <code>widget_pipeline_bootstrap(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><span class="reference-call-tree-source">[widgets/widget_pipeline_bootstrap.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_pipeline_bootstrap.py#L94-L195" class="reference-call-tree-callable"><code>_widget_pipeline_bootstrap_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L164-L172" class="reference-call-tree-callable"><code>get_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L156-L161" class="reference-call-tree-callable"><code>get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L116-L148" class="reference-call-tree-callable"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L261-L266" class="reference-call-tree-callable"><code>get_selected_agreement(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L256-L258" class="reference-call-tree-callable"><code>_get_selected_agreement_state(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L236-L239" class="reference-call-tree-callable"><code>set_active_pipeline_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><span class="reference-call-tree-source">[widgets/widget_pipeline_bootstrap.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_pipeline_bootstrap.py#L208-L442" class="reference-call-tree-callable"><code>_render_bootstrap_agreement_selector(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108" class="reference-call-tree-callable"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83" class="reference-call-tree-callable"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[widgets/notebook_registry.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/notebook_registry.py#L255-L311" class="reference-call-tree-callable"><code>current_notebook_active_registrations(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L21-L33" class="reference-call-tree-callable"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L40-L64" class="reference-call-tree-callable"><code>_runtime_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L36-L37" class="reference-call-tree-callable"><code>_safe_str(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[widgets/notebook_registry.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/notebook_registry.py#L196-L252" class="reference-call-tree-callable"><code>_load_notebook_registry(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L250-L260" class="reference-call-tree-callable"><code>read_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L116-L123" class="reference-call-tree-callable"><code>get_spark_session(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L216-L218" class="reference-call-tree-callable"><code>read_delta_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       └── </span><span class="reference-call-tree-source">[widgets/notebook_registry.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/notebook_registry.py#L47-L52" class="reference-call-tree-callable"><code>_coerce_row_dicts(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[widgets/notebook_registry.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/notebook_registry.py#L67-L193" class="reference-call-tree-callable"><code>register_current_notebook(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[config/audit.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/audit.py#L11-L13" class="reference-call-tree-callable"><code>_audit_timestamp_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L153-L165" class="reference-call-tree-callable"><code>coerce_metadata_row_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L125-L150" class="reference-call-tree-callable"><code>_coerce_metadata_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L107-L122" class="reference-call-tree-callable"><code>metadata_table_schema_registry(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │       ├── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L87-L99" class="reference-call-tree-callable"><code>_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │       │   └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L32-L84" class="reference-call-tree-callable"><code>spark_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │       └── </span><span class="reference-call-tree-source">[config/metadata_schemas.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py#L102-L104" class="reference-call-tree-callable"><code>audit_schema_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L239-L247" class="reference-call-tree-callable"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L595-L634" class="reference-call-tree-callable"><code>get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L547-L587" class="reference-call-tree-callable"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L49-L60" class="reference-call-tree-callable"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L263-L287" class="reference-call-tree-callable"><code>write_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L192-L197" class="reference-call-tree-callable"><code>normalize_write_mode(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L146-L150" class="reference-call-tree-callable"><code>resolve_configured_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L166-L170" class="reference-call-tree-callable"><code>resolve_lakehouse_table_location(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L37-L46" class="reference-call-tree-callable"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L85-L87" class="reference-call-tree-callable"><code>_resolve_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │   │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L90-L93" class="reference-call-tree-callable"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │   │       └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L27-L29" class="reference-call-tree-callable"><code>_join_lakehouse_area_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136" class="reference-call-tree-callable"><code>resolve_target_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │       ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66" class="reference-call-tree-callable"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   │       └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72" class="reference-call-tree-callable"><code>_validate_warehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L200-L203" class="reference-call-tree-callable"><code>validate_dataframe_writer(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L229-L236" class="reference-call-tree-callable"><code>write_delta_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[widgets/notebook_registry.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/notebook_registry.py#L55-L64" class="reference-call-tree-callable"><code>_notebook_registration_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L559-L575" class="reference-call-tree-callable"><code>latest_agreement_versions(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L382-L387" class="reference-call-tree-callable"><code>_coerce_row_dicts(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L546-L552" class="reference-call-tree-callable"><code>_parse_contract_version(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L588-L595" class="reference-call-tree-callable"><code>list_data_agreements(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L415-L417" class="reference-call-tree-callable"><code>_audit_date(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L577-L586" class="reference-call-tree-callable"><code>list_all_data_agreement_rows(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       └── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L316-L321" class="reference-call-tree-callable"><code>config_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L56-L131" class="reference-call-tree-callable"><code>render_searchable_selector(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L49-L53" class="reference-call-tree-callable"><code>_html_escape(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L37-L46" class="reference-call-tree-callable"><code>widget_common(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L25-L34" class="reference-call-tree-callable"><code>require_ipywidgets(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[widgets/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/shared.py#L250-L253" class="reference-call-tree-callable"><code>set_selected_agreement(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><span class="reference-call-tree-source">[widgets/widget_pipeline_bootstrap.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_pipeline_bootstrap.py#L199-L203" class="reference-call-tree-callable"><code>_html_escape(...)</code></a></div>
    </div>

Bootstrap a guided pipeline notebook run and store runtime defaults.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_pipeline_bootstrap.py:22`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_pipeline_bootstrap.py#L22-L86">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`

## Usage guidance

### Use when

- Use near the top of 02_pipeline or read-only exploration notebooks that need agreement-aware runtime defaults.

### Do not use when

- Do not use when an advanced custom notebook needs to pass every runtime parameter explicitly to lower-level helpers.

### Additional context

Resolves runtime and agreement context once so template notebooks can call guardrail and summary helpers with concise defaults.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_pipeline_bootstrap(
    notebook_type: str='02_pipeline',
    select_agreement: bool=False,
    register_notebook: bool=False,
    read_only: bool=False,
    run_context: Any=None,
    spark_session: Any=None,
    metadata_schema: str | None=None,
    pipeline_name: str | None=None,
    context: dict[str, Any] | None=None,
) -> Any:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
PIPELINE = widget_pipeline_bootstrap(notebook_type="02_pipeline", select_agreement=True, register_notebook=True)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `notebook_type` | `str` | No | FabricOps notebook type to associate with the active context. |
| `select_agreement` | `bool` | No | When True, render the agreement selector and capture the selected agreement for downstream defaults. |
| `register_notebook` | `bool` | No | When True, allow the agreement selector to register this notebook to the selected agreement. Use ``False`` for read-only exploration. |
| `read_only` | `bool` | No | Marks the active context as read-only for exploratory notebooks. The startup helper itself does not write metadata unless ``register_notebook=True`` is explicitly requested. |
| `run_context` | `Any` | No | ``RUN_CONTEXT`` from ``00_env_config``. Defaults to the active notebook variable named ``RUN_CONTEXT``. |
| `spark_session` | `Any` | No | Spark session. Defaults to the active notebook variable named ``spark``. |
| `metadata_schema` | `str \| None` | No | ``METADATA_SCHEMA`` from ``00_env_config`` when schema routing is used. |
| `pipeline_name` | `str \| None` | No | Friendly pipeline name. Defaults to Fabric runtime notebook metadata. |
| `context` | `dict[str, Any] \| None` | No | Advanced FabricOps context override. |

## Returns

Internal runtime context object with run_id, pipeline_name, notebook identity, agreement identity, and Spark context for downstream defaults. The concrete context class is internal and not a primary public API.

### Return interpretation

The returned context can be assigned to PIPELINE for target config and lineage fields while downstream helpers read the same active defaults automatically. The concrete context class is internal and not a primary public API.

## Raises / Errors

Not documented yet

### Common failure causes

- RUN_CONTEXT is unavailable.
- spark is unavailable.
- No agreement exists when select_agreement=True.
- The user has not selected an agreement.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Data agreement</span><span class="glossary-chip-definition">FabricOps agreement record that captures ownership, steward context, usage, and expectations.</span> <a href="../../../reference/glossary/#data-agreement">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)
