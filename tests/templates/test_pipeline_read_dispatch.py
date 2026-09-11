"""Contract tests for the cloneable 02_pipeline Read dispatcher."""

from pathlib import Path

import nbformat


ROOT = Path(__file__).parents[2]
NOTEBOOK = ROOT / "templates" / "notebooks" / "02_pipeline.ipynb"


def _cell(cell_id: str) -> str:
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    return next(cell.source for cell in notebook.cells if cell.get("id") == cell_id)


def test_read_blocks_expose_one_cloneable_store_dispatch_pattern():
    """Every Read block visibly supports Lakehouse, Warehouse table, and Warehouse query reads."""
    required = (
        "READ_STORE_TYPE =",
        "READ_TARGET =",
        "READ_SCHEMA =",
        "READ_TABLE =",
        "READ_QUERY =",
        "read_pipeline_prep(",
        'if READ_STORE_TYPE == "lakehouse":',
        'elif READ_STORE_TYPE == "warehouse":',
        "read_lakehouse_table(table_id=READ_TABLE_ID)",
        "read_warehouse_table(",
        "read_warehouse_query(READ_QUERY, target=READ_TARGET)",
        "observe_table(",
        "check_freshness(",
        "check_source_stability(",
        'if READ_STORE_TYPE == "warehouse" and READ_QUERY:',
        "profile_dataframe(read_df)",
        "check_schema(",
        "check_dq(",
        "profile_and_register_table(read_df)",
        "READ_PREPS[READ] = read_prep",
        "READ_DFS[READ] = read_df",
    )
    for index in (1, 2, 3):
        block = _cell(f"read-{index}")
        for fragment in required:
            assert fragment in block
        assert "READ_MODE" not in block
        assert "SOURCE_READER" not in block


def test_read_examples_cover_lakehouse_and_warehouse_query():
    """The canonical examples demonstrate both physical-store types and optional SQL pushdown."""
    first = _cell("read-1")
    second = _cell("read-2")
    third = _cell("read-3")

    assert 'READ_STORE_TYPE = "lakehouse"' in first
    assert 'READ_STORE_TYPE = "lakehouse"' in second
    assert "READ_QUERY = None" in first
    assert "READ_QUERY = None" in second
    assert 'READ_STORE_TYPE = "warehouse"' in third
    assert 'READ_QUERY = f"""' in third


def test_custom_warehouse_query_is_derived_not_physical_contract_surface():
    """Custom SQL keeps physical-source observation but profiles the derived result diagnostically."""
    block = _cell("read-3")
    query_branch = block.index('if READ_STORE_TYPE == "warehouse" and READ_QUERY:')
    diagnostic = block.index("profile_dataframe(read_df)", query_branch)
    canonical_else = block.index("else:", query_branch)
    schema_check = block.index("check_schema(", canonical_else)

    assert diagnostic < canonical_else < schema_check
    assert block.index("observe_table(") < query_branch
    assert "Custom SQL returns derived engineering data" in block


def test_invalid_store_type_and_lakehouse_query_fail_visibly():
    """The notebook keeps dispatch validation visible instead of hiding it in a generic reader."""
    block = _cell("read-1")
    assert "READ_QUERY is only supported when READ_STORE_TYPE='warehouse'." in block
    assert "READ_STORE_TYPE must be 'lakehouse' or 'warehouse'." in block
