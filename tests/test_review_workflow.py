from fabricops_kit.business_context import _extract_column_business_context_suggestions, _prepare_business_context_profile_input
import fabricops_kit.business_context as business_context
from fabricops_kit.config import ReviewWorkflowConfig
from fabricops_kit.data_governance import extract_personal_identifier_suggestions, prepare_governance_profile_input
from fabricops_kit.data_quality import _approved_dq_rules_from_review_rows, _prepare_dq_profile_rows_with_context


def test_business_context_profile_shaping_and_extraction():
    rows = _prepare_business_context_profile_input([{"COLUMN_NAME": "id", "DATA_TYPE": "string"}], table_name="orders", table_context="sales")
    assert rows[0]["column_name"] == "id"
    out = _extract_column_business_context_suggestions([{"ai_business_context_response": "{'column_name':'id','business_context':'identifier'}"}])
    assert out[0]["column_name"] == "id"


def test_dq_profile_prep_and_approved_extraction():
    profile_rows = [{"column_name": "id", "data_type": "string"}, {"column_name": "status", "data_type": "string"}]
    contexts = [{"column_name": "id", "approved_business_context": "Identifier"}]
    prepared = _prepare_dq_profile_rows_with_context(profile_rows, table_name="orders", column_contexts=contexts)
    assert len(prepared) == 1
    approved = _approved_dq_rules_from_review_rows([{"approval_status": "approved", "proposed_rule_payload": "{'rule_id': 'id_not_null'}"}])
    assert approved[0]["rule_id"] == "id_not_null"


def test_governance_profile_prep_and_extraction():
    prepared = prepare_governance_profile_input([{"column_name": "email"}], table_name="orders", column_contexts=[{"column_name": "email", "approved_business_context": "Contact email"}])
    assert prepared[0]["approved_business_context"] == "Contact email"
    out = extract_personal_identifier_suggestions([{"ai_governance_response": '{"column_name":"email","ai_suggested_personal_identifier_classification":"direct_identifier"}'}])
    assert out[0]["column_name"] == "email"


def test_review_workflow_config_defaults():
    cfg = ReviewWorkflowConfig()
    assert cfg.default_approval_status == "pending"


def test_review_business_context_requires_widgets(monkeypatch):
    def _raise(*args, **kwargs):
        raise ImportError("ipywidgets missing")

    monkeypatch.setattr(business_context.importlib, "import_module", _raise)
    try:
        business_context.review_business_context([{"column_name": "id", "business_context": "Identifier"}], "dev", "sales", "orders")
        assert False, "expected ImportError"
    except ImportError:
        assert True
