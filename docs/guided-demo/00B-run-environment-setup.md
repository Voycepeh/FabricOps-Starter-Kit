# Step 0B: Set up the operating environment

**Configure `00_env_config`, then prove configuration-driven engineering from a plain PySpark notebook by reading the raw demo files and landing the managed tables used by the later pipeline demo.**

Complete [Step 0A: Prepare Fabric artifacts](00A-setup-fabric-artifacts.md) first.

!!! info "Key concepts for this step"

    [**Configuration**](../glossary.md#configuration) — named settings that control environment targets, processing choices, and runtime behaviour.  
    [**Configuration-driven Engineering**](../glossary.md#configuration-driven-engineering) — reusable engineering behaviour controlled through configuration rather than rewritten code.  
    [**Notebook**](../glossary.md#notebook) — the Fabric document used to run the FabricOps setup and workflow code.

    These are the only glossary concepts you need before starting this step.

## High-level flow

```text
Configure 00_env_config
        ↓
Open a plain PySpark notebook
        ↓
%run 00_env_config
        ↓
Read raw demo files with FabricOps
        ↓
Write managed Lakehouse + Warehouse tables
        ↓
Optionally read them back and display
        ↓
Ready for 02_pipeline
```

???+ success "Live — Open `00_env_config`"

    Open the copied `00_env_config` notebook in the target workspace. Run it in Governance, Engineering Development, and Engineering Production.

    FabricOps keeps environment configuration in a notebook so downstream notebooks can load the configured context naturally through `%run 00_env_config` rather than introducing a separate YAML or file-parsing step.

???+ success "Live — Attach the Fabric Environment"

    1. Open the notebook.
    2. Select the Fabric Environment containing the FabricOps wheel.
    3. Restart the notebook session after changing the Environment or its libraries.

    You can skip this when the workspace default Environment already contains the correct FabricOps package.

    ![Fabric notebook Environment selection example](../assets/00B/fabric-example-set-notebook-environment.png)

???+ success "Live — Configure Fabric item paths"

    Update `ENV_PATHS` for the active environment so FabricOps can resolve the required workspaces and Fabric items.

    A Fabric item URL contains the workspace ID and item ID, which can be used to populate the configuration.

    ![Path config](../assets/00B/00_config_paths.png)

    !!! note "Why this configuration exists"

        A Fabric notebook works naturally with its attached/default item, but a real pipeline may need several Lakehouses, Warehouses, or workspaces. Without central configuration, those cross-item reads and writes can push physical OneLake paths, workspace IDs, and item IDs into individual `02_pipeline` notebooks.

        FabricOps centralises those environment-specific identities in `00_env_config`. Engineering notebooks keep logical target names such as `source`, `unified`, and `product`, while FabricOps resolves the correct Development or Production item at runtime. That means promotion does not require rewriting paths in every pipeline, and replacing or adding a Fabric item can be handled in the environment configuration instead of across many notebooks.

        Read the deeper rationale in the [FabricOps Engineering Guide — Config-driven engineering and why FabricOps has I/O functions](../reference/engineering-cheat-sheet.md#config-driven-engineering).

???+ success "Live — Review widget settings"

    Change widget settings only when you need different dropdown options or additional custom fields.

    Custom fields are stored as JSON and do not create additional physical table columns.

    ![Widget config](../assets/00B/00_config_widgets_config_setup.png)

???+ success "Live — Set up metadata tables"

    Complete this block in the Governance workspace.

    1. Confirm that the `metadata` target points to the correct metadata Lakehouse.
    2. Run the metadata setup cell.
    3. Allow the setup to create or validate the required metadata tables.
    4. Leave the setup cell unchanged during normal Guided Demo runs.

    ![Setup Metadata Tables](../assets/00B/00_config_metadata_tables_setup_code.png)

    The cell should complete without errors and confirm that the metadata tables are ready.

    ![Metadata Tables Done](../assets/00B/Metadata-Tables-Created.png)

???+ success "Live — Prove configuration-driven engineering from a plain notebook"

    In **Engineering Development**, create a new plain PySpark notebook. This is intentionally not a FabricOps pipeline template.

    Attach the same Fabric Environment, then make the configured Fabric context available with one line:

    ```python
    %run 00_env_config
    ```

    Import only the public I/O functions needed for this setup:

    ```python
    from fabricops_kit import (
        read_lakehouse_csv,
        read_lakehouse_excel,
        read_lakehouse_json,
        read_lakehouse_parquet,
        read_lakehouse_table,
        read_warehouse_table,
        write_lakehouse_table,
        write_warehouse_table,
    )
    ```

    The notebook can now use logical targets from `00_env_config` instead of embedding physical OneLake paths, workspace IDs, or Fabric item IDs.

???+ success "Live — Read the raw Orders demo"

    Use CSV as the default walkthrough:

    ```python
    orders_df = read_lakehouse_csv(
        "DemoData/orders.csv",
        target="source",
        spark_session=spark,
        header=True,
        inferSchema=True,
    )
    ```

    The other Orders files are format-equivalent, so you can swap only the reader and file path while keeping the same downstream setup:

    ```python
    # Equivalent alternatives — choose one instead of the CSV call above.
    # orders_df = read_lakehouse_json(
    #     "DemoData/orders.json", target="source", spark_session=spark,
    # )
    # orders_df = read_lakehouse_parquet(
    #     "DemoData/orders.parquet", target="source", spark_session=spark,
    # )
    # orders_df = read_lakehouse_excel(
    #     "DemoData/orders.xlsx", target="source", spark_session=spark,
    #     sheet_name="orders",
    # )
    ```

    This is the raw-file boundary. Files do not need a FabricOps `table_id` merely to be read from the Lakehouse `Files` area.

???+ success "Live — Read the supporting raw files"

    Read the Product reference data and historical Orders data from the same configured Source Lakehouse:

    ```python
    products_df = read_lakehouse_csv(
        "DemoData/products.csv",
        target="source",
        spark_session=spark,
        header=True,
        inferSchema=True,
    )

    order_history_df = read_lakehouse_csv(
        "DemoData/order_history.csv",
        target="source",
        spark_session=spark,
        header=True,
        inferSchema=True,
    )
    ```

???+ success "Live — Land the managed source tables"

    Write the current Orders and Product reference data into the schema-enabled Source Lakehouse. These are the managed Lakehouse sources used later by `02_pipeline`.

    ```python
    write_lakehouse_table(
        orders_df,
        "orders",
        target="source",
        schema="demo",
        mode="overwrite",
    )

    write_lakehouse_table(
        products_df,
        "products",
        target="source",
        schema="demo",
        mode="overwrite",
    )
    ```

    Write the historical data into the configured Product Warehouse so the later pipeline can demonstrate a Warehouse query source rather than another Lakehouse table read:

    ```python
    write_warehouse_table(
        order_history_df,
        "demo",
        "order_history",
        target="product",
        mode="overwrite",
    )
    ```

    !!! note "Why this happens before `02_pipeline`"

        Step 0B is basic physical ingestion and setup. The later `02_pipeline` starts from managed Fabric tables so every governed source can have a stable table identity and the demo can focus on source preparation, observation, incremental scope, transformation, target preparation, and governed publication.

??? info "Optional — Read the landed tables back"

    Confirm that the managed sources are physically available before continuing:

    ```python
    orders_table_df = read_lakehouse_table(
        "orders",
        target="source",
        schema="demo",
        spark_session=spark,
    )
    display(orders_table_df)

    products_table_df = read_lakehouse_table(
        "products",
        target="source",
        schema="demo",
        spark_session=spark,
    )
    display(products_table_df)

    order_history_table_df = read_warehouse_table(
        "demo",
        "order_history",
        target="product",
        spark_session=spark,
    )
    display(order_history_table_df)
    ```

    This optional verification demonstrates the full-table Lakehouse and Warehouse readers without turning the setup notebook into the governed ETL itself.

???+ success "Live — Confirm reusable context"

    `00_env_config` prepares reusable context for downstream FabricOps functions and notebooks.

    ![For Downstream Usage](../assets/00B/00_config_resuable_context.png)

## Expected result

`00_env_config` is ready when the Fabric Environment is attached, package imports work, paths and runtime settings are configured, metadata tables exist, and `FABRIC_CONTEXT["env"]` plus `FABRIC_CONTEXT["config"]` are available.

The canonical raw files have also been landed into the managed sources used by the later ETL:

```text
Source Lakehouse
  demo.orders
  demo.products

Product Warehouse
  demo.order_history
```

You have now demonstrated that `00_env_config` plus a plain PySpark notebook is enough to perform configuration-driven FabricOps reads and writes. Step 2 can therefore focus on the governed operating pattern rather than basic physical setup.

**Previous:** [Step 0A: Prepare Fabric artifacts](00A-setup-fabric-artifacts.md)  
**Next:** [Step 1: Create Data Stewards and Data Agreements](01-create-agreement.md)
