import pytest

from fabricops_kit import (
    SchemaContractValidationError,
    build_schema_contract_review_state,
    enforce_schema_result,
    load_schema_contract,
    suggest_schema_contract,
    validate_schema,
    write_schema_contract,
)
from fabricops_kit import schema_contracts as sc


class FakeField:
    def __init__(self, name, data_type, nullable=True):
        self.name = name
        self.dataType = data_type
        self.nullable = nullable


class FakeSchema:
    def __init__(self, fields):
        self.fields = fields


class FakeDf:
    def __init__(self, fields):
        self.schema = FakeSchema(fields)
        self.dtypes = [(f.name, str(f.dataType)) for f in fields]


class FakeSpark:
    def createDataFrame(self, rows):
        return [dict(r) for r in rows]


def test_suggest_schema_contract_from_profile_rows_retains_ordinal_type_and_nullability():
    rows = [
        {"COLUMN_NAME": "id", "DATA_TYPE": "integer", "NULL_COUNT": 0, "ORDINAL_POSITION": 1},
        {"COLUMN_NAME": "name", "DATA_TYPE": "string", "NULL_COUNT": 2, "ORDINAL_POSITION": 2},
    ]
    proposed = suggest_schema_contract(rows, agreement_id="AGR", contract_id="SRC", dataset_role="source")

    assert [r["column_name"] for r in proposed] == ["id", "name"]
    assert proposed[0]["data_type"] == "int"
    assert proposed[0]["nullable"] is False
    assert proposed[1]["nullable"] is True
    assert proposed[1]["ordinal_position"] == 2
    assert all(r["selected"] for r in proposed)


def test_suggest_schema_contract_from_dataframe_schema():
    df = FakeDf([FakeField("id", "Integer", False), FakeField("amount", "decimal(10,2)", True)])
    proposed = suggest_schema_contract(df, agreement_id="AGR", contract_id="TGT", dataset_role="target")

    assert proposed[0]["data_type"] == "int"
    assert proposed[0]["nullable"] is False
    assert proposed[1]["ordinal_position"] == 2


def expected(required=True):
    return [
        {"column_name": "id", "data_type": "int", "required": required, "nullable": False, "ordinal_position": 1},
        {"column_name": "name", "data_type": "string", "required": True, "nullable": True, "ordinal_position": 2},
    ]


def test_validate_schema_exact_match():
    result = validate_schema(FakeDf([FakeField("id", "integer", False), FakeField("name", "string", True)]), expected())
    assert result["is_valid"] is True


def test_validate_schema_missing_required_column():
    result = validate_schema(FakeDf([FakeField("name", "string", True)]), expected())
    assert result["missing_required_columns"] == ["id"]
    assert result["is_valid"] is False


def test_validate_schema_optional_column_missing_is_valid():
    result = validate_schema(FakeDf([FakeField("name", "string", True)]), expected(required=False))
    assert result["optional_missing_columns"] == ["id"]
    assert result["is_valid"] is True


def test_validate_schema_unexpected_column_allowed_and_rejected():
    df = FakeDf(
        [FakeField("id", "int", False), FakeField("name", "string", True), FakeField("new_col", "string", True)]
    )
    assert validate_schema(df, expected(), allow_extra_columns=True)["is_valid"] is True
    rejected = validate_schema(df, expected(), allow_extra_columns=False)
    assert rejected["unexpected_columns"] == ["new_col"]
    assert rejected["is_valid"] is False


def test_validate_schema_datatype_mismatch_and_equivalent_type_alias():
    alias_result = validate_schema(
        FakeDf([FakeField("id", "integer", False), FakeField("name", "string", True)]), expected()
    )
    assert alias_result["is_valid"] is True

    mismatch = validate_schema(
        FakeDf([FakeField("id", "bigint", False), FakeField("name", "string", True)]), expected()
    )
    assert mismatch["datatype_mismatches"] == [{"column_name": "id", "expected": "int", "actual": "bigint"}]


def test_validate_schema_nullability_mismatch():
    result = validate_schema(FakeDf([FakeField("id", "int", True), FakeField("name", "string", True)]), expected())
    assert result["nullability_mismatches"] == [{"column_name": "id", "expected": False, "actual": True}]


def test_validate_schema_column_order_enabled_and_ignored_by_default():
    df = FakeDf([FakeField("name", "string", True), FakeField("id", "int", False)])
    assert validate_schema(df, expected())["is_valid"] is True
    checked = validate_schema(df, expected(), check_column_order=True)
    assert len(checked["column_order_mismatches"]) == 2
    assert checked["is_valid"] is False


def test_enforce_schema_result_modes():
    drift = {"is_valid": False, "missing_required_columns": ["id"]}
    assert enforce_schema_result(drift, enforcement="observe")["can_continue"] is True
    with pytest.warns(UserWarning):
        assert enforce_schema_result(drift, enforcement="warn")["can_continue"] is True
    with pytest.raises(SchemaContractValidationError):
        enforce_schema_result(drift, enforcement="fail")


def test_review_state_filters_unselected_columns():
    state = build_schema_contract_review_state(
        [
            {"column_name": "id", "data_type": "integer", "selected": True},
            {"column_name": "debug", "data_type": "string", "selected": False},
        ]
    )
    assert [r["column_name"] for r in state["columns"]] == ["id"]
    assert state["columns"][0]["data_type"] == "int"


def test_contract_persistence_and_latest_dataset_specific_loading(monkeypatch):
    tables = {sc.SCHEMA_CONTRACT_TABLE: [], sc.SCHEMA_CONTRACT_COLUMN_TABLE: []}

    def fake_read(_config, _env, _target, table, **_kwargs):
        return tables[table]

    def fake_write(df, _config, _env, _target, table, **_kwargs):
        tables[table].extend(df)

    monkeypatch.setattr(sc, "read_lakehouse_table", fake_read)
    monkeypatch.setattr(sc, "write_lakehouse_table", fake_write)
    spark = FakeSpark()
    config = object()

    write_schema_contract(
        spark,
        config=config,
        env="dev",
        agreement_id="AGR",
        contract_id="SRC1",
        dataset_role="source",
        workspace_name="ws",
        item_name="lh",
        table_name="raw_a",
        columns=expected(),
        default_enforcement="warn",
    )
    write_schema_contract(
        spark,
        config=config,
        env="dev",
        agreement_id="AGR",
        contract_id="SRC2",
        dataset_role="source",
        workspace_name="ws",
        item_name="lh",
        table_name="raw_b",
        columns=expected(),
    )
    first_target = write_schema_contract(
        spark,
        config=config,
        env="dev",
        agreement_id="AGR",
        contract_id="TGT1",
        dataset_role="target",
        workspace_name="ws",
        item_name="lh",
        table_name="curated",
        columns=expected(),
    )
    second_target = write_schema_contract(
        spark,
        config=config,
        env="dev",
        agreement_id="AGR",
        contract_id="TGT1",
        dataset_role="target",
        workspace_name="ws",
        item_name="lh",
        table_name="curated",
        columns=expected(),
    )
    # Draft versions are preserved but ignored by load.
    tables[sc.SCHEMA_CONTRACT_TABLE].append({**second_target, "contract_version": 99, "contract_status": "draft"})

    source = load_schema_contract(
        config=config, env="dev", agreement_id="AGR", dataset_role="source", table_name="raw_a"
    )
    target = load_schema_contract(
        config=config, env="dev", agreement_id="AGR", dataset_role="target", table_name="curated"
    )

    assert source["contract_id"] == "SRC1"
    assert target["contract_version"] == 2
    assert target["contract_status"] == "approved"
    assert first_target["contract_version"] == 1


def test_load_schema_contract_rejects_agreement_only(monkeypatch):
    monkeypatch.setattr(sc, "read_lakehouse_table", lambda *args, **kwargs: [])
    with pytest.raises(ValueError):
        load_schema_contract(config=object(), env="dev", agreement_id="AGR", dataset_role="source")
