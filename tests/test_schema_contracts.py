import pytest

from fabricops_kit import (
    SchemaContractValidationError,
    apply_schema_guardrail,
    review_schema_contract,
    validate_schema,
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


def expected(required=True):
    return [
        {"column_name": "id", "data_type": "int", "required": required, "nullable": False, "ordinal_position": 1},
        {"column_name": "name", "data_type": "string", "required": True, "nullable": True, "ordinal_position": 2},
    ]


def profile_rows():
    return [
        {"COLUMN_NAME": "id", "DATA_TYPE": "integer", "NULL_COUNT": 0, "ORDINAL_POSITION": 1},
        {"COLUMN_NAME": "name", "DATA_TYPE": "string", "NULL_COUNT": 2, "ORDINAL_POSITION": 2},
    ]


def test_review_schema_contract_approves_versions_and_persists(monkeypatch):
    tables = {sc.SCHEMA_CONTRACT_TABLE: [], sc.SCHEMA_CONTRACT_COLUMN_TABLE: []}

    def fake_read(_config, _env, _target, table, **_kwargs):
        return tables[table]

    def fake_write(df, _config, _env, _target, table, **_kwargs):
        tables[table].extend(df)

    monkeypatch.setattr(sc, "read_lakehouse_table", fake_read)
    monkeypatch.setattr(sc, "write_lakehouse_table", fake_write)

    result = review_schema_contract(
        profile_rows(),
        config=object(),
        env="dev",
        agreement_id="AGR",
        contract_id="SRC",
        dataset_role="source",
        workspace_name="ws",
        item_name="lh",
        table_name="raw_orders",
        spark_session=FakeSpark(),
        approved=True,
        default_enforcement="warn",
    )
    second = review_schema_contract(
        profile_rows(),
        config=object(),
        env="dev",
        agreement_id="AGR",
        contract_id="SRC",
        dataset_role="source",
        workspace_name="ws",
        item_name="lh",
        table_name="raw_orders",
        spark_session=FakeSpark(),
        approved=True,
    )

    assert result["status"] == "approved"
    assert result["contract_version"] == 1
    assert result["settings"]["default_enforcement"] == "warn"
    assert [r["column_name"] for r in result["columns"]] == ["id", "name"]
    assert result["columns"][0]["data_type"] == "int"
    assert result["columns"][0]["nullable"] is False
    assert second["contract_version"] == 2
    assert len(tables[sc.SCHEMA_CONTRACT_TABLE]) == 2
    assert len(tables[sc.SCHEMA_CONTRACT_COLUMN_TABLE]) == 4


def test_review_schema_contract_does_not_persist_without_explicit_approval(monkeypatch):
    writes = []
    monkeypatch.setattr(sc, "write_lakehouse_table", lambda *args, **kwargs: writes.append(args))
    result = review_schema_contract(
        profile_rows(),
        config=object(),
        env="dev",
        agreement_id="AGR",
        contract_id="SRC",
        dataset_role="source",
        workspace_name="ws",
        item_name="lh",
        table_name="raw_orders",
        spark_session=FakeSpark(),
        approved=False,
    )

    assert result["status"] == "pending_approval"
    assert result["contract_version"] is None
    assert writes == []


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


def test_apply_schema_guardrail_loads_validates_enforces_and_writes_evidence(monkeypatch):
    dataset = {
        "contract_id": "SRC",
        "agreement_id": "AGR",
        "dataset_role": "source",
        "workspace_name": "ws",
        "item_name": "lh",
        "table_name": "raw_orders",
        "allow_extra_columns": False,
        "check_column_order": False,
        "default_enforcement": "observe",
        "contract_status": "approved",
        "contract_version": 1,
    }
    columns = [{**row, "contract_id": "SRC", "contract_version": 1} for row in expected()]
    writes = []

    def fake_read(_config, _env, _target, table, **_kwargs):
        return {sc.SCHEMA_CONTRACT_TABLE: [dataset], sc.SCHEMA_CONTRACT_COLUMN_TABLE: columns}[table]

    def fake_write(df, _config, _env, _target, table, **_kwargs):
        writes.append((table, df))

    monkeypatch.setattr(sc, "read_lakehouse_table", fake_read)
    monkeypatch.setattr(sc, "write_lakehouse_table", fake_write)

    result = apply_schema_guardrail(
        FakeDf([FakeField("id", "int", False), FakeField("name", "string", True)]),
        config=object(),
        env="dev",
        agreement_id="AGR",
        dataset_role="source",
        workspace_name="ws",
        item_name="lh",
        table_name="raw_orders",
        run_id="run-1",
        spark_session=FakeSpark(),
    )

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["validation"]["is_valid"] is True
    assert result["evidence_status"] == "written"
    assert writes[0][0] == sc.SCHEMA_VALIDATION_EVIDENCE_TABLE


def test_apply_schema_guardrail_returns_not_configured_when_contract_missing(monkeypatch):
    monkeypatch.setattr(sc, "read_lakehouse_table", lambda *args, **kwargs: [])
    result = apply_schema_guardrail(
        FakeDf([FakeField("id", "int", False)]),
        config=object(),
        env="dev",
        agreement_id="AGR",
        dataset_role="source",
        table_name="raw_orders",
        run_id="run-1",
        spark_session=FakeSpark(),
    )

    assert result["status"] == "not_configured"
    assert result["can_continue"] is True
    assert result["evidence_status"] == "not_written"


def test_apply_schema_guardrail_raises_on_fail_drift_after_writing_evidence(monkeypatch):
    dataset = {
        "contract_id": "SRC",
        "agreement_id": "AGR",
        "dataset_role": "source",
        "table_name": "raw_orders",
        "allow_extra_columns": False,
        "check_column_order": False,
        "default_enforcement": "fail",
        "contract_status": "approved",
        "contract_version": 1,
    }
    columns = [{**row, "contract_id": "SRC", "contract_version": 1} for row in expected()]
    writes = []

    def fake_read(_config, _env, _target, table, **_kwargs):
        return {sc.SCHEMA_CONTRACT_TABLE: [dataset], sc.SCHEMA_CONTRACT_COLUMN_TABLE: columns}[table]

    def fake_write(df, _config, _env, _target, table, **_kwargs):
        writes.append((table, df))

    monkeypatch.setattr(sc, "read_lakehouse_table", fake_read)
    monkeypatch.setattr(sc, "write_lakehouse_table", fake_write)

    with pytest.raises(SchemaContractValidationError):
        apply_schema_guardrail(
            FakeDf([FakeField("name", "string", True)]),
            config=object(),
            env="dev",
            agreement_id="AGR",
            dataset_role="source",
            table_name="raw_orders",
            run_id="run-1",
            spark_session=FakeSpark(),
        )

    assert writes and writes[0][0] == sc.SCHEMA_VALIDATION_EVIDENCE_TABLE
    assert writes[0][1][0]["validation_status"] == "failed"


def test_internal_helpers_are_not_exported_from_package():
    import fabricops_kit

    for name in [
        "suggest_schema_contract",
        "write_schema_contract",
        "load_schema_contract",
        "enforce_schema_result",
        "build_schema_validation_evidence",
        "write_schema_validation_evidence",
        "normalize_spark_data_type",
    ]:
        assert name not in fabricops_kit.__all__
        assert not hasattr(fabricops_kit, name)

    assert "review_schema_contract" in fabricops_kit.__all__
    assert "apply_schema_guardrail" in fabricops_kit.__all__
    assert "validate_schema" in fabricops_kit.__all__


def test_03_pc_uses_apply_schema_guardrail_not_manual_schema_chain():
    import json
    from pathlib import Path

    nb = json.loads(Path("templates/notebooks/03_pc_agreement_pipeline_template.ipynb").read_text())
    code = "\n".join("".join(cell.get("source", [])) for cell in nb["cells"] if cell.get("cell_type") == "code")

    assert "apply_schema_guardrail(" in code
    assert code.count("apply_schema_guardrail(") == 2
    assert "dataset_role=\"source\"" in code
    assert "dataset_role=\"target\"" in code
    for internal_name in [
        "load_schema_contract(",
        "enforce_schema_result(",
        "build_schema_validation_evidence(",
        "write_schema_validation_evidence(",
    ]:
        assert internal_name not in code
