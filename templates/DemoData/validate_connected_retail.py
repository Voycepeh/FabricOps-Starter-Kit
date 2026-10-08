"""Validate the connected retail CSV demo fixtures against the canonical product IDs."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a demo CSV fixture into dictionaries."""
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate() -> None:
    """Check shared product IDs, inventory events, and SCD snapshots."""
    products = read_csv(ROOT / "products.csv")
    ids = {row["product_id"] for row in products}
    assert len(ids) == len(products) == 8, "Canonical products must have eight unique IDs."
    for row in read_csv(ROOT / "orders.csv"):
        assert row["product_id"] in ids, "Order references an unknown product."

    movement_rows = []
    for day in (1, 2):
        rows = read_csv(ROOT / "incremental_inventory" / f"inventory_day{day}.csv")
        assert rows, "Inventory batch must not be empty."
        movement_rows.extend(rows)
    assert len(movement_rows) == 12
    assert len({row["movement_id"] for row in movement_rows}) == len(movement_rows)
    previous_timestamp = None
    for row in movement_rows:
        assert row["product_id"] in ids
        assert row["movement_type"] in {"RECEIPT", "REPLENISHMENT", "SALE"}
        quantity = int(row["quantity_change"])
        assert quantity > 0 if row["movement_type"] != "SALE" else quantity < 0
        timestamp = datetime.fromisoformat(row["modified_datetime"])
        assert previous_timestamp is None or timestamp > previous_timestamp
        previous_timestamp = timestamp
    balances = {product_id: 0 for product_id in ids}
    for row in movement_rows:
        balances[row["product_id"]] += int(row["quantity_change"])
        assert balances[row["product_id"]] >= 0
    assert balances["P001"] == 145 and balances["P002"] == 77

    snapshots = [read_csv(ROOT / "scd_product_master" / f"products_day{day}.csv") for day in (1, 2, 3)]
    for day, snapshot in enumerate(snapshots, 1):
        assert len(snapshot) == len(ids)
        assert {row["product_id"] for row in snapshot} == ids
        assert len({row["product_id"] for row in snapshot}) == len(snapshot)
        for row in snapshot:
            assert row["product_name"] == next(p["product_name"] for p in products if p["product_id"] == row["product_id"])
            assert float(row["list_price"]) > 0
            assert datetime.fromisoformat(row["modified_datetime"]).date().isoformat() == f"2026-10-{day + 5:02d}"
    by_id = [{row["product_id"]: row for row in snapshot} for snapshot in snapshots]
    def changes(before: dict, after: dict) -> set[str]:
        return {key for key in ids if any(before[key][field] != after[key][field] for field in ("product_category", "list_price"))}
    assert changes(by_id[0], by_id[1]) == {"P002"}
    assert changes(by_id[1], by_id[2]) == {"P001"}

    print("PASS: 8 shared products; 12 unique ordered inventory movements; 3 full snapshots.")
    print("Expected SCD1 row counts: 8, 8, 8; SCD2 version counts: 8, 9, 10.")
    print("Expected final stock: P001=145; P002=77.")


if __name__ == "__main__":
    validate()
