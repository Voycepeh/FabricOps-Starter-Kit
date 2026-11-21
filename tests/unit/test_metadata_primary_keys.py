"""The diagram and runtime use one primary-key definition."""
import pytest

from fabricops_kit.config.metadata_schemas import METADATA_PRIMARY_KEYS, metadata_table_schema_registry
from fabricops_kit.io.shared import validate_metadata_primary_key
from scripts.reference_docs_metadata import METADATA_TABLE_MODELS


def test_diagram_keys_match_runtime_and_implemented_columns():
    """Every canonical table has exactly the key enforced by runtime writers."""
    registry = metadata_table_schema_registry()
    assert set(METADATA_PRIMARY_KEYS) == set(registry) == set(METADATA_TABLE_MODELS)
    for table, keys in METADATA_PRIMARY_KEYS.items():
        assert list(keys) == METADATA_TABLE_MODELS[table]["primary_key"]
        assert set(keys) <= set(registry[table].fieldNames())


@pytest.mark.parametrize("table", METADATA_PRIMARY_KEYS)
def test_key_validation_for_conditional_governance_mutations(table):
    """Whole-table transactions reject null, blank and duplicate keys before commit."""
    keys = METADATA_PRIMARY_KEYS[table]
    row = dict.fromkeys(keys, "one")
    validate_metadata_primary_key(table, [row])
    for rows in ([row, row], [{**row, keys[0]: None}], [{**row, keys[0]: " "}]):
        with pytest.raises(ValueError, match="primary key"):
            validate_metadata_primary_key(table, rows)
