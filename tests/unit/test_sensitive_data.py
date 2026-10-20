"""Sensitive Data Guardrail preparation tests."""

from importlib import import_module
import json

import pytest
from tests.helpers import execution_plan_stub

module = import_module("fabricops_kit.pipeline.check_sensitive_data")
shared = import_module("fabricops_kit.pipeline.shared")


def _rule(*, treatment="tokenize", action="Block", column_name="email", version=2,
          column_id="email-id", parameters=None):
    return {
        "guardrail_rule_id": f"sensitive-{version}", "guardrail_version": 1,
        "contract_id": "contract", "contract_version": version,
        "table_id": "table-id", "column_id": column_id, "column_name": column_name,
        "guardrail_type": "sensitive_data", "rule_parameters_json": json.dumps({
            "scope": "column", "treatment": treatment, **(parameters or {}),
        }),
        "action": action, "is_active": True,
    }


def _runtime(monkeypatch, rules, writes):
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "resolve_pipeline_data_contract", lambda *_a, **_k: {"contract_id": "contract"})
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *_a, **_k: {
        "table_id": "table-id", "table_name": "customers", "store_type": "lakehouse",
        "store": "unified", "schema": "dbo",
    })
    monkeypatch.setattr(module, "load_table_guardrail_rules", lambda *_a, **_k: rules)
    monkeypatch.setattr(shared, "write_guardrail_result_row", lambda **kwargs: writes.append(kwargs["result"]))


def test_development_without_selected_contract_skips_without_catalogue(monkeypatch, spark_session):
    """Authoring mode preserves the input without requiring governed metadata."""
    frame = spark_session.createDataFrame([(1, "raw")], ["id", "email"])
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "resolve_pipeline_data_contract", lambda *_a, **_k: None)
    monkeypatch.setattr(
        module,
        "resolve_catalogue_table_identity",
        lambda *_a, **_k: pytest.fail("authoring mode must not require Catalogue registration"),
    )

    result = module.check_sensitive_data(frame, table_id="table-id")

    assert result["status"] == "skipped"
    assert result["dataframe"] is frame
    assert result["can_continue"] is True

def test_tokenize_is_opaque_null_preserving_and_caller_owned(monkeypatch, spark_session):
    """Tokenization replaces raw values and only returns its one-to-one mapping."""
    writes = []
    _runtime(monkeypatch, [_rule(), {**_rule(), "guardrail_type": "data_quality"}], writes)
    frame = spark_session.createDataFrame([(1, "a@example.test"), (2, "a@example.test"), (3, "b@example.test"), (4, None)], ["id", "email"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    values = [row.email for row in result["dataframe"].orderBy("id").collect()]
    assert values[0] == values[1]
    assert values[0] != values[2]
    assert values[3] is None
    assert not {"a@example.test", "b@example.test"}.intersection(value for value in values if value)
    mapping = result["support_mapping"].collect()
    assert {(row.table_id, row.column_id) for row in mapping} == {("table-id", "email-id")}
    assert {row.original_value for row in mapping} == {"a@example.test", "b@example.test"}
    assert len(writes) == 1
    assert all("original_value" not in str(value) for value in writes)


def test_multiple_sensitive_columns_apply_mixed_treatments(monkeypatch, spark_session):
    """All exact-version column rules apply independently in one preparation."""
    rules = [
        _rule(),
        {**_rule(treatment="remove", column_name="phone"),
         "guardrail_rule_id": "sensitive-phone", "column_id": "phone-id"},
    ]
    _runtime(monkeypatch, rules, [])
    frame = spark_session.createDataFrame(
        [(1, "a@example.test", "555-0100"), (2, "a@example.test", None)],
        ["id", "email", "phone"],
    )
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["dataframe"].columns == ["id", "email"]
    assert result["dataframe"].select("email").distinct().count() == 1
    assert {row.column_id for row in result["support_mapping"].collect()} == {"email-id"}
    assert len(result["checks"]) == 2


@pytest.mark.parametrize("parameters,expected", [
    ({"preserve_start": 1, "preserve_end": 0, "mask_character": "*"}, "S********"),
    ({"preserve_start": 0, "preserve_end": 3, "mask_character": "*"}, "******67A"),
    ({"preserve_start": 1, "preserve_end": 3, "mask_character": "*"}, "S*****67A"),
])
def test_mask_preserves_configured_portions(monkeypatch, spark_session, parameters, expected):
    """Mask obscures exactly the middle while preserving rows and nulls."""
    _runtime(monkeypatch, [_rule(treatment="mask", parameters=parameters)], [])
    frame = spark_session.createDataFrame([(1, "S1234567A"), (2, "S1"), (3, None)], ["id", "email"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    values = [row.email for row in result["dataframe"].orderBy("id").collect()]
    assert values == [expected, "**", None]
    assert result["support_mapping"] is None


def test_bucket_uses_open_ends_and_inclusive_lower_boundaries(monkeypatch, spark_session):
    """Bucket preserves rows and maps exact boundaries using lower-bound labels."""
    parameters = {
        "bins": [0, 3000, 5000, 8000, 12000],
        "labels": ["<3k", "3k-5k", "5k-8k", "8k-12k", "12k+"],
    }
    _runtime(monkeypatch, [_rule(treatment="bucket", column_name="salary", column_id="salary-id", parameters=parameters)], [])
    frame = spark_session.createDataFrame(
        [(1, -1.0), (2, 0.0), (3, 3000.0), (4, 8420.0), (5, 12000.0), (6, None)],
        ["id", "salary"],
    )
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert [row.salary for row in result["dataframe"].orderBy("id").collect()] == [
        "<3k", "<3k", "3k-5k", "8k-12k", "12k+", None,
    ]
    assert result["support_mapping"] is None


@pytest.mark.parametrize("treatment,parameters,column_type", [
    ("mask", {"preserve_start": -1, "preserve_end": 0, "mask_character": "*"}, "string"),
    ("bucket", {"bins": [0, 0], "labels": ["low", "high"]}, "double"),
    ("bucket", {"bins": [0, 10], "labels": ["low"]}, "double"),
    ("bucket", {"bins": [0, 10], "labels": ["low", "high"]}, "string"),
])
@pytest.mark.parametrize("action,can_continue", [("Warn", False), ("Block", False)])
def test_invalid_mask_or_bucket_policy_respects_action(
    monkeypatch, spark_session, treatment, parameters, column_type, action, can_continue
):
    """Malformed treatments block even when persisted intent still says Warn."""
    _runtime(monkeypatch, [_rule(treatment=treatment, action=action, parameters=parameters)], [])
    value = "not-numeric" if column_type == "string" else 1.0
    frame = spark_session.createDataFrame([(1, value)], f"id int, email {column_type}")
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["can_continue"] is can_continue
    assert result["status"] == ("warning" if can_continue else "failed")
    assert result["support_mapping"] is None


def test_all_four_treatments_execute_independently(monkeypatch, spark_session):
    """Tokenize, Mask, Bucket, and Remove apply in one exact contract version."""
    rules = [
        _rule(column_name="nric", column_id="nric-id"),
        _rule(treatment="mask", column_name="phone", column_id="phone-id", parameters={
            "preserve_start": 1, "preserve_end": 3, "mask_character": "*",
        }),
        _rule(treatment="bucket", column_name="salary", column_id="salary-id", parameters={
            "bins": [0, 3000, 5000, 8000, 12000],
            "labels": ["<3k", "3k-5k", "5k-8k", "8k-12k", "12k+"],
        }),
        _rule(treatment="remove", column_name="email", column_id="email-id"),
    ]
    _runtime(monkeypatch, rules, [])
    frame = spark_session.createDataFrame(
        [("S1234567A", "91234567", 8420, "a@example.test")],
        ["nric", "phone", "salary", "email"],
    )
    result = module.check_sensitive_data(frame, table_id="table-id")
    row = result["dataframe"].first()
    assert result["dataframe"].columns == ["nric", "phone", "salary"]
    assert row.nric != "S1234567A"
    assert row.phone == "9****567"
    assert row.salary == "8k-12k"
    assert {mapping.column_id for mapping in result["support_mapping"].collect()} == {"nric-id"}


def test_existing_mapping_preserves_established_token(monkeypatch, spark_session):
    """Caller-supplied persisted mappings retain established assignments."""
    _runtime(monkeypatch, [_rule()], [])
    frame = spark_session.createDataFrame(
        [(1, "a@example.test"), (2, "new@example.test")], ["id", "email"]
    )
    existing = spark_session.createDataFrame(
        [("table-id", "email-id", "a@example.test", "opaque-established")],
        ["table_id", "column_id", "original_value", "token_value"],
    )
    result = module.check_sensitive_data(
        frame, table_id="table-id", existing_mapping=existing
    )
    values = {row.id: row.email for row in result["dataframe"].collect()}
    assert values[1] == "opaque-established"
    assert values[2] != "new@example.test"


def test_remove_drops_only_sensitive_column(monkeypatch, spark_session):
    """Remove has no support mapping and preserves unrelated fields."""
    _runtime(monkeypatch, [_rule(treatment="remove")], [])
    frame = spark_session.createDataFrame([(1, "a@example.test", None), (2, "a@example.test", "x")], ["id", "email", "other"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["dataframe"].columns == ["id", "other"]
    assert [tuple(row) for row in result["dataframe"].orderBy("id").collect()] == [(1, None), (2, "x")]
    assert result["support_mapping"] is None


@pytest.mark.parametrize("action,can_continue,status", [("Warn", False, "failed"), ("Block", False, "failed")])
def test_missing_column_respects_normalized_action(monkeypatch, spark_session, action, can_continue, status):
    """Every failed treatment blocks and persists the effective Block action."""
    writes = []
    _runtime(monkeypatch, [_rule(action=action, column_name="missing")], writes)
    frame = spark_session.createDataFrame([(1, "a@example.test")], ["id", "email"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["can_continue"] is can_continue
    assert result["status"] == status
    assert result["dataframe"].collect() == frame.collect()
    assert writes[0]["status"] == status
    assert writes[0]["action"] == "Block"
    assert writes[0]["severity"] == "blocking"
    assert writes[0]["can_continue"] is False


def test_exact_contract_rules_are_supplied_by_canonical_resolver(monkeypatch, spark_session):
    """Runtime consumes only the exact rules returned by contract resolution."""
    _runtime(monkeypatch, [_rule(treatment="remove", version=3)], [])
    frame = spark_session.createDataFrame([(1, "a@example.test")], ["id", "email"])
    result = module.check_sensitive_data(frame, table_id="table-id")
    assert result["checks"][0]["contract_version"] == 3


def test_multiple_token_columns_have_one_releasable_cache(monkeypatch, spark_session):
    """Returned mappings release every per-column cache and retain UUID stability."""
    writes = []
    rules = [_rule(version=1), _rule(version=2, column_id="phone-id", column_name="phone")]
    _runtime(monkeypatch, rules, writes)
    frame = spark_session.createDataFrame([("a@example.test", "123"), ("b@example.test", "456")], ["email", "phone"])
    before = spark_session.sparkContext._jsc.getPersistentRDDs().size()
    result = module.check_sensitive_data(frame, table_id="table-id", verbose=False)
    mapping = result["support_mapping"]
    try:
        assert mapping.count() == 4
        assert len(result["dataframe"].collect()) == 2
        assert result["dataframe"].collect() == result["dataframe"].collect()
        assert "broadcast" not in result["dataframe"]._jdf.queryExecution().logical().toString().lower()
    finally:
        mapping.unpersist(blocking=True)
    assert spark_session.sparkContext._jsc.getPersistentRDDs().size() == before


def test_later_treatment_failure_releases_earlier_token_cache(monkeypatch, spark_session):
    """A blocked treatment result cannot strand a mapping that no caller receives."""
    _runtime(monkeypatch, [_rule(version=1), _rule(version=2, treatment="remove", column_id="missing-id", column_name="missing")], [])
    frame = spark_session.createDataFrame([("a@example.test",)], ["email"])
    before = spark_session.sparkContext._jsc.getPersistentRDDs().size()
    result = module.check_sensitive_data(frame, table_id="table-id", verbose=False)
    assert result["can_continue"] is False
    assert result["support_mapping"] is None
    assert spark_session.sparkContext._jsc.getPersistentRDDs().size() == before


@pytest.mark.parametrize('value,start,end,expected', [
    ('A', 0, 0, '*'), ('ABC', 1, 1, '***'), ('AB', 9, 9, '**'),
    ('', 0, 0, ''), ('ABCDE', 1, 1, 'A***E'),
])
def test_mask_never_exposes_short_values(spark_session, value, start, end, expected):
    """Partial preservation must never cause a short value to bypass masking."""
    frame = spark_session.createDataFrame([(value,)], ['sensitive'])
    prepared = shared._mask_column(frame, column_name='sensitive', parameters={
        'preserve_start': start, 'preserve_end': end, 'mask_character': '*',
    })
    assert prepared.first().sensitive == expected


def test_fixed_width_buckets_are_stable_across_batches(spark_session):
    """An anchored interval has the same meaning regardless of batch extrema."""
    from fabricops_kit.data_contract.shared import validate_sensitive_data_parameters

    params = validate_sensitive_data_parameters({'scope': 'column', 'treatment': 'bucket',
                                                 'bin_width': 10, 'bin_origin': 0})
    frame = spark_session.createDataFrame([(-1,), (0,), (9,), (10,), (None,)], 'value int')
    result = shared._bucket_column(frame, column_name='value', parameters=params)
    assert [r.value for r in result.collect()] == ['[-10, 0)', '[0, 10)', '[0, 10)', '[10, 20)', None]
    later = spark_session.createDataFrame([(9,), (1000,)], ['value'])
    assert shared._bucket_column(later, column_name='value', parameters=params).first().value == '[0, 10)'


@pytest.mark.parametrize('extra', [
    {'bin_width': 0}, {'bin_width': -1}, {'bin_width': True}, {'bin_width': float('nan')},
    {'bin_width': 10, 'bin_origin': float('inf')}, {'bin_width': 10, 'bins': [0], 'labels': ['all']},
])
def test_fixed_width_policy_rejects_invalid_or_ambiguous_settings(extra):
    """Reject invalid policy before constructing a Spark expression."""
    from fabricops_kit.data_contract.shared import validate_sensitive_data_parameters

    with pytest.raises(ValueError):
        validate_sensitive_data_parameters({'scope': 'column', 'treatment': 'bucket', **extra})


def test_returned_token_mapping_retains_absent_identities(spark_session):
    """A batch cannot erase assignments needed by a later batch."""
    existing = spark_session.createDataFrame([
        ('t', 'c', 'absent', 'retained'), ('t', 'c', 'present', 'stable'),
    ], ['table_id', 'column_id', 'original_value', 'token_value'])
    frame = spark_session.createDataFrame([('present',)], ['value'])
    mapping = shared._build_token_mapping(frame, column_name='value', column_id='c', table_id='t', existing_mapping=existing)
    try:
        assert {r.original_value: r.token_value for r in mapping.collect()} == {'absent': 'retained', 'present': 'stable'}
        assert shared._apply_token_mapping(frame, column_name='value', column_id='c', table_id='t', mapping=mapping).first().value == 'stable'
    finally:
        mapping.unpersist()


@pytest.mark.parametrize('mode', ['testing', 'live'])
@pytest.mark.parametrize('collision', [False, True])
def test_managed_token_mapping_uses_restricted_target_without_validation_writes(monkeypatch, spark_session, mode, collision):
    """Exercise real token generation and reuse around a mocked Delta vault merge."""
    import sys
    import types
    from fabricops_kit.config import GovernanceConfig

    fields = ['table_id', 'column_id', 'original_value', 'token_value', 'original_data_type']
    stored = spark_session.createDataFrame([('t', 'c', 'known', 'stable', 'string'),
        ('t', 'c', 'absent', 'stable' if collision else 'reserved', 'string')], fields)
    merges = []
    reads = []

    class Vault:
        def alias(self, _name):
            return self

        def merge(self, frame, condition):
            self.pending = frame
            assert 'original_value' in condition and 'column_id' in condition
            return self

        def whenNotMatchedInsert(self, **kwargs):
            assert set(kwargs['values']) == set(fields)
            return self

        def execute(self):
            nonlocal stored
            merges.append(self.pending.count())
            new = self.pending.join(stored.select('table_id', 'column_id', 'original_value'),
                                    ['table_id', 'column_id', 'original_value'], 'left_anti')
            stored = stored.unionByName(new).cache()
            stored.count()

    vault = Vault()
    delta = types.ModuleType('delta.tables')
    delta.DeltaTable = types.SimpleNamespace(isDeltaTable=lambda *_args: True, forPath=lambda *_args: vault)
    monkeypatch.setitem(sys.modules, 'delta', types.ModuleType('delta'))
    monkeypatch.setitem(sys.modules, 'delta.tables', delta)
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', lambda *args, **kwargs: (None, None, None, '/restricted'))

    def read(table_name, **kwargs):
        reads.append((table_name, kwargs))
        assert kwargs['store'] == 'Sensitive'
        assert kwargs['context']['_fabricops_suppress_io_log'] is True
        return stored

    monkeypatch.setattr(shared, 'read_lakehouse_table', read)
    config = types.SimpleNamespace(governance_config=GovernanceConfig(sensitive_data_token_mapping={
        'store': 'Sensitive', 'schema': 'vault', 'table_name': 'tokens',
    }))
    frame = spark_session.createDataFrame([('known',), ('new',)], ['value'])
    if collision:
        with pytest.raises(ValueError, match='reuses one token'):
            shared._build_token_mapping(frame, column_name='value', column_id='c', table_id='t',
                existing_mapping=None, config=config, env='dev', context={"execution_plan": execution_plan_stub(mode)})
        stored.unpersist()
        return
    mapping = shared._build_token_mapping(frame, column_name='value', column_id='c', table_id='t',
        existing_mapping=None, config=config, env='dev', context={"execution_plan": execution_plan_stub(mode)})
    try:
        values = {r.original_value: r.token_value for r in mapping.collect()}
        assert set(values) == {'known', 'new'}
        assert values['known'] == 'stable'
        assert values['new'] != 'new'
        assert merges == ([1] if mode == 'live' else [])
        assert {r.original_value for r in stored.collect()} == ({'known', 'new', 'absent'} if mode == 'live' else {'known', 'absent'})
        if mode == 'live':
            again = shared._build_token_mapping(frame, column_name='value', column_id='c', table_id='t',
                existing_mapping=None, config=config, env='dev', context={"execution_plan": execution_plan_stub("live")})
            try:
                assert {r.original_value: r.token_value for r in again.collect()} == values
                assert merges == [1]  # Reusing known assignments must not perform another Delta merge.
            finally:
                again.unpersist()
    finally:
        mapping.unpersist()
        stored.unpersist()


def test_managed_token_mapping_configuration_requires_separate_store():
    """Raw original-to-token relationships cannot default into general metadata."""
    from fabricops_kit.config import GovernanceConfig

    with pytest.raises(ValueError, match='separately restricted'):
        GovernanceConfig(sensitive_data_token_mapping={'store': 'Metadata', 'table_name': 'tokens'})
    with pytest.raises(ValueError, match='requires store'):
        GovernanceConfig(sensitive_data_token_mapping={'store': 'Sensitive'})


@pytest.mark.parametrize('origin', [0.0, 0.05])
def test_fixed_width_decimal_boundaries_are_exact(spark_session, origin):
    """A value exactly on a decimal boundary belongs to its own lower-inclusive band."""
    from decimal import Decimal

    values = [('1.20', '[1.2, 1.3)'), ('1.30', '[1.3, 1.4)'), ('2.40', '[2.4, 2.5)'), ('-0.10', '[-0.1, 0)')]
    if origin:
        values = [('1.25', '[1.25, 1.35)'), ('1.35', '[1.35, 1.45)'), ('-0.05', '[-0.05, 0.05)')]
    frame = spark_session.createDataFrame([(Decimal(value),) for value, _label in values], 'value decimal(10,2)')
    result = shared._bucket_column(frame, column_name='value', parameters={'bin_width': 0.1, 'bin_origin': origin})
    assert [row.value for row in result.collect()] == [label for _value, label in values]


def test_fixed_width_float_boundaries_and_nulls(spark_session):
    """Floating sources use decimal interval arithmetic and keep nulls."""
    frame = spark_session.createDataFrame([(1.2,), (1.3,), (None,)], 'value double')
    result = shared._bucket_column(frame, column_name='value', parameters={'bin_width': 0.1, 'bin_origin': 0.0})
    assert [row.value for row in result.collect()] == ['[1.2, 1.3)', '[1.3, 1.4)', None]


def test_fixed_width_high_precision_values_just_below_boundaries(spark_session):
    """Shifting high-precision decimals must not round them across an interval edge."""
    from decimal import Decimal

    frame = spark_session.createDataFrame([(Decimal('1.249999999999999999'),)], 'value decimal(38,18)')
    result = shared._bucket_column(frame, column_name='value', parameters={'bin_width': 0.1, 'bin_origin': 0.05})
    assert result.first().value == '[1.15, 1.25)'


def test_fixed_width_rejects_origin_that_reduces_decimal_precision(spark_session):
    """A large origin cannot silently round a small value into another interval."""
    frame = spark_session.createDataFrame([(1e-17,)], 'value double')
    with pytest.raises(ValueError, match='supported decimal precision'):
        shared._bucket_column(frame, column_name='value', parameters={'bin_width': 1e20, 'bin_origin': 1e20})
