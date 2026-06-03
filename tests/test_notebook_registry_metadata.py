from types import SimpleNamespace

import pytest

import fabricops_kit.metadata as metadata
from fabricops_kit.fabric_input_output import FabricStore


EXPECTED_NOTEBOOK_REGISTRY_COLUMNS = [
    "agreement_id",
    "environment_name",
    "dataset_name",
    "table_name",
    "topic",
    "pipeline_name",
    "notebook_type",
    "workspace_id",
    "workspace_name",
    "notebook_id",
    "notebook_name",
    "notebook_url",
    "user_name",
    "user_id",
    "registered_at",
]


def _config():
    store = FabricStore(env="dev", workspace_id="workspace", item_id="metadata-item", name="lh_metadata_dev", kind="lakehouse")
    return SimpleNamespace(path_config=SimpleNamespace(paths={"dev": {"metadata": store}}))


class _Frame:
    def __init__(self, rows):
        self.rows = rows
        self.columns = list(rows[0]) if rows else []

    def limit(self, count):
        assert count == 0
        return self


class _Spark:
    def __init__(self):
        self.source_rows = []

    def createDataFrame(self, rows):
        self.source_rows.append(rows)
        return _Frame(rows)


def test_notebook_registry_schema_helper_returns_register_current_notebook_columns():
    assert metadata.NOTEBOOK_REGISTRY_TABLE == "METADATA_NOTEBOOK_REGISTRY"
    assert metadata.get_notebook_registry_schema() == EXPECTED_NOTEBOOK_REGISTRY_COLUMNS
    assert "notebook_registry_key" not in metadata.get_notebook_registry_schema()
    assert "workspace_name" in metadata.get_notebook_registry_schema()
    assert "workspace" not in metadata.get_notebook_registry_schema()


def test_setup_notebook_registry_table_creates_missing_table_and_validates_existing(monkeypatch):
    reads, writes = [], []
    attempts = {metadata.NOTEBOOK_REGISTRY_TABLE: 0}
    spark = _Spark()

    def read_table(config, env, target, table, **kwargs):
        reads.append((env, target, table, kwargs))
        attempts[table] += 1
        if attempts[table] == 1:
            raise RuntimeError("missing")
        return [dict.fromkeys(EXPECTED_NOTEBOOK_REGISTRY_COLUMNS, "")]

    monkeypatch.setattr(metadata, "read_lakehouse_table", read_table)
    monkeypatch.setattr(metadata, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))

    first = metadata.setup_notebook_registry_table(spark=spark, config=_config(), env="dev")
    second = metadata.setup_notebook_registry_table(spark=spark, config=_config(), env="dev")

    assert first["status"] == "ready"
    assert first["created"] is True
    assert first["created_tables"] == [metadata.NOTEBOOK_REGISTRY_TABLE]
    assert second["created"] is False
    assert second["created_tables"] == []
    assert len(writes) == 1
    written_df, env, target, table, kwargs = writes[0]
    assert written_df.columns == EXPECTED_NOTEBOOK_REGISTRY_COLUMNS
    assert (env, target, table, kwargs) == ("dev", "metadata", metadata.NOTEBOOK_REGISTRY_TABLE, {"mode": "ignore", "overwrite_schema": True})
    assert spark.source_rows == [[{field: "" for field in EXPECTED_NOTEBOOK_REGISTRY_COLUMNS}]]
    assert all(read[0:3] == ("dev", "metadata", metadata.NOTEBOOK_REGISTRY_TABLE) for read in reads)


def test_setup_notebook_registry_table_rejects_existing_table_with_missing_columns(monkeypatch):
    monkeypatch.setattr(metadata, "read_lakehouse_table", lambda *args, **kwargs: [{"agreement_id": "DA-1", "workspace": "Old Workspace"}])
    monkeypatch.setattr(metadata, "write_lakehouse_table", lambda *args, **kwargs: pytest.fail("existing table should not be overwritten"))

    with pytest.raises(ValueError, match="workspace_name"):
        metadata.setup_notebook_registry_table(spark=_Spark(), config=_config(), env="dev")


def test_register_current_notebook_row_columns_match_registry_schema(monkeypatch):
    writes = []
    monkeypatch.setattr(metadata, "_runtime_context", lambda: {
        "currentWorkspaceId": "workspace-id",
        "currentWorkspaceName": "Workspace Name",
        "currentNotebookId": "notebook-id",
        "currentNotebookName": "03_pc_orders_pipeline",
        "userName": "user@example.com",
        "userId": "user-id",
    })
    monkeypatch.setattr(metadata, "write_metadata_rows", lambda spark, rows, metadata_path, table_name, mode="append": writes.append((rows, metadata_path, table_name, mode)))

    row = metadata.register_current_notebook(
        spark=object(),
        metadata_path="metadata-path",
        agreement_id="DA-1",
        notebook_type="03_pc",
        environment_name="dev",
        dataset_name="orders",
        table_name="fact_orders",
        topic="pipeline",
        pipeline_name="orders_pipeline",
    )

    assert list(row) == metadata.get_notebook_registry_schema()
    assert set(row) == set(EXPECTED_NOTEBOOK_REGISTRY_COLUMNS)
    assert row["workspace_name"] == "Workspace Name"
    assert row["notebook_url"] == "https://app.fabric.microsoft.com/groups/workspace-id/notebooks/notebook-id"
    assert writes == [([row], "metadata-path", metadata.NOTEBOOK_REGISTRY_TABLE, "append")]
