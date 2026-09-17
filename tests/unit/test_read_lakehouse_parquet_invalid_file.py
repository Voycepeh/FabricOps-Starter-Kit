"""Regression tests for invalid Parquet file handling."""

from __future__ import annotations

import pytest

from fabricops_kit.config import FabricStore, PathConfig
from fabricops_kit.io.read_lakehouse_parquet import read_lakehouse_parquet


def _context():
    config = PathConfig(
        paths={
            "dev": {
                "Bronze": FabricStore(
                    env="dev",
                    workspace_id="dev-bronze-workspace",
                    item_id="dev-bronze-item",
                    kind="lakehouse",
                )
            }
        }
    )
    return {"config": config, "env": "dev"}


def test_invalid_parquet_footer_skips_tsus_fallback():
    """Corrupt Parquet files should fail immediately instead of trying ``_tsus``."""

    class Reader:
        def __init__(self):
            self.parquet_calls = []

        def option(self, _key, _value):
            return self

        def parquet(self, path):
            self.parquet_calls.append(path)
            raise RuntimeError(
                "[CANNOT_READ_FILE_FOOTER] Could not read footer. "
                "orders.parquet is not a Parquet file. Expected magic number at tail"
            )

    class Spark:
        def __init__(self):
            self.read = Reader()

    spark = Spark()

    with pytest.raises(RuntimeError, match="CANNOT_READ_FILE_FOOTER"):
        read_lakehouse_parquet(
            "Demo/orders.parquet",
            store="Bronze",
            spark_session=spark,
            verbose=False,
            context=_context(),
        )

    assert spark.read.parquet_calls == [
        "abfss://dev-bronze-workspace@onelake.dfs.fabric.microsoft.com/"
        "dev-bronze-item/Files/Demo/orders.parquet"
    ]
