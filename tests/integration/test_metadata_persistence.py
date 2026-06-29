"""Test FabricOps metadata setup persistence behavior."""

from __future__ import annotations

import pytest

from fabricops_kit.config import setup_metadata_tables
from fabricops_kit.config.setup_metadata_tables import CANONICAL_METADATA_TABLES, _metadata_table_schema_registry
from tests.helpers import framework_config

pytestmark = pytest.mark.integration


class Table:
    """Minimal table fake exposing columns and active steward count."""

    def __init__(self, columns: list[str], count: int = 1) -> None:
        self.columns = list(columns)
        self._count = count

    def where(self, _expr: str) -> "Table":
        """Return self for active steward filtering."""
        return self

    def count(self) -> int:
        """Return configured fake row count."""
        return self._count


def test_central_metadata_setup_preserves_existing_valid_tables():
    """Verify central metadata setup preserves existing valid tables."""
    registry = _metadata_table_schema_registry()
    reads = []

    class Spark:
        def table(self, table: str) -> Table:
            reads.append(table)
            return Table(registry[table].fieldNames())

        def sql(self, statement: str) -> None:
            raise AssertionError(f"metadata setup must not call spark.sql: {statement}")

    result = setup_metadata_tables(spark=Spark(), config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert result["tables"] == CANONICAL_METADATA_TABLES
    assert result["created_tables"] == []
    assert result["warnings"] == []
    assert result["active_metadata_tables"] == CANONICAL_METADATA_TABLES
    assert result["created_or_checked_tables"] == CANONICAL_METADATA_TABLES
    assert reads == [*CANONICAL_METADATA_TABLES, "METADATA_DATA_STEWARD"]


def test_central_metadata_setup_rejects_existing_tables_missing_columns():
    """Verify central metadata setup rejects existing tables missing columns."""

    class Spark:
        def table(self, table: str) -> Table:
            if table == "METADATA_DATA_STEWARD":
                return Table(["steward_id"])
            return Table(_metadata_table_schema_registry()[table].fieldNames())

    with pytest.raises(ValueError, match=r"METADATA_DATA_STEWARD is missing required column\(s\): .*effective_from"):
        setup_metadata_tables(spark=Spark(), config=framework_config(), env="dev")
