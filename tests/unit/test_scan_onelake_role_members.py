"""Tests for the caller-scoped OneLake membership workaround."""

import importlib
import io
import json
from urllib.error import HTTPError

import pytest

m = importlib.import_module("fabricops_kit.access_scanner.scan_onelake_role_members")
WORKSPACE = "00000000-0000-0000-0000-000000000001"
ITEM = "00000000-0000-0000-0000-000000000002"
ORIGIN = "https://wabi-example-redirect.analysis.windows.net"
RULES = [
    {
        "effect": "Permit",
        "permission": [{"attributeName": "Path", "attributeValueIncludedIn": ["*"]}],
        "constraints": {"row": "restricted"},
    }
]


def _sources(monkeypatch, *, details=None, assignments=None, members=None):
    roles = [
        {
            "name": "Readers",
            "decisionRules": RULES,
            "members": members
            or {
                "microsoftEntraMembers": [{"objectId": "group-1"}],
                "fabricItemMembers": [{"itemAccess": ["ReadAll"], "sourcePath": "workspace/item"}],
            },
        }
    ]

    def collection(url, token):
        assert token == "test-token"
        return roles if url.endswith("dataAccessRoles") else assignments or []

    monkeypatch.setattr(m, "_collection", collection)
    monkeypatch.setattr(
        m,
        "_portal_access",
        lambda url, token: {
            "detail": details
            if details is not None
            else [
                {"objectId": "group-1", "givenName": "Data Readers", "permissions": 1},
            ]
        },
    )
    return roles


def _scan(**kwargs):
    return m.scan_onelake_role_members(WORKSPACE, ITEM, portal_base_url=ORIGIN, access_token="test-token", **kwargs)


def test_named_members_and_supplied_users_preserve_origin_and_restrictions(monkeypatch):
    """Resolve names while keeping supplied membership distinct from API facts."""
    _sources(monkeypatch)
    result = _scan(group_memberships={"Data Readers": ["alice@example.com", "ALICE@example.com", "bob@example.com"]})
    explicit = result["role_members"][0]
    assert explicit["display_name"] == "Data Readers"
    assert explicit["principal_type"] == "UNKNOWN"
    assert json.loads(explicit["decision_rules_json"]) == RULES
    users = [row for row in result["users"] if row["permission_source"] == "ONELAKE_ROLE"]
    assert [row["user_principal"] for row in users] == ["alice@example.com", "bob@example.com"]
    assert all(row["principal_object_id"] == "group-1" for row in users)
    assert all(row["identity_source"] == "CALLER_SUPPLIED_GROUP_MEMBERSHIP" for row in users)
    assert result["item_access"][0]["permissions_raw"] == 1
    assert any(row["status"] == "AUTOMATIC_MEMBERSHIP_UNRESOLVED" for row in result["coverage"])


def test_object_id_precedes_name_and_workspace_type_is_authoritative(monkeypatch):
    """Use stable group IDs and explicit API types instead of portal UI labels."""
    _sources(
        monkeypatch,
        assignments=[
            {"principal": {"id": "group-1", "displayName": "Data Readers", "type": "Group"}, "role": "Member"}
        ],
    )
    result = _scan(group_memberships={"GROUP-1": ["alice@example.com"], "Data Readers": ["wrong@example.com"]})
    assert {row["user_principal"] for row in result["users"]} == {"alice@example.com"}
    assert result["role_members"][0]["principal_type"] == "GROUP"
    assert {row["permission_source"] for row in result["users"]} == {"ONELAKE_ROLE", "ITEM_ACCESS", "WORKSPACE_ROLE"}


def test_ambiguous_group_name_is_not_expanded(monkeypatch):
    """Never map one display name onto two distinct principal IDs."""
    _sources(
        monkeypatch,
        details=[{"objectId": "group-1", "givenName": "Readers"}, {"objectId": "group-2", "givenName": "Readers"}],
    )
    result = _scan(group_memberships={"Readers": ["alice@example.com"]})
    assert result["users"] == []
    assert any(row["status"] == "AMBIGUOUS_GROUP_NAME" for row in result["coverage"])


def test_known_users_do_not_become_groups_from_a_name_mapping(monkeypatch):
    """Caller mappings must not override an API User classification."""
    _sources(
        monkeypatch,
        assignments=[
            {
                "principal": {
                    "id": "group-1",
                    "displayName": "Data Readers",
                    "type": "User",
                    "userDetails": {"userPrincipalName": "actual@example.com"},
                },
                "role": "Viewer",
            }
        ],
    )
    result = _scan(group_memberships={"Data Readers": ["wrong@example.com"]})
    assert {row["user_principal"] for row in result["users"]} == {"actual@example.com"}
    assert all(row["identity_source"] == "API" for row in result["users"])


def test_unknown_principal_is_not_presented_as_an_individual(monkeypatch):
    """A resolved display name alone does not identify an individual user."""
    _sources(monkeypatch)
    result = _scan()
    assert result["users"] == []
    assert result["role_members"][0]["display_name"] == "Data Readers"
    assert any(row["status"] == "PRINCIPAL_TYPE_UNRESOLVED" for row in result["coverage"])


def test_optional_source_failures_preserve_primary_roles(monkeypatch):
    """Failures must remain visible rather than become an apparently complete scan."""
    _sources(monkeypatch)
    original = m._collection

    def collection(url, token):
        if url.endswith("roleAssignments"):
            raise RuntimeError("forbidden")
        return original(url, token)

    monkeypatch.setattr(m, "_collection", collection)

    def portal(url, token):
        raise RuntimeError("forbidden")

    monkeypatch.setattr(m, "_portal_access", portal)
    result = _scan(group_memberships={"group-1": ["alice@example.com"]})
    assert result["role_members"][0]["principal_object_id"] == "group-1"
    assert result["users"][0]["user_principal"] == "alice@example.com"
    assert len([row for row in result["coverage"] if row["status"] == "UNAVAILABLE"]) == 2


@pytest.mark.parametrize(
    "origin",
    [
        "http://wabi-example.analysis.windows.net",
        "https://evil.example",
        "https://wabi-example.analysis.windows.net.evil.example",
        ORIGIN + "/path",
        "https://user:pass@wabi-example.analysis.windows.net",
    ],
)
def test_invalid_portal_origins_rejected_before_auth(monkeypatch, origin):
    """Validate the token destination before acquiring or sending credentials."""
    monkeypatch.setattr(m, "fabric_access_token", lambda token: pytest.fail("must not authenticate"))
    with pytest.raises(ValueError, match="portal_base_url"):
        m.scan_onelake_role_members(WORKSPACE, ITEM, portal_base_url=origin)


@pytest.mark.parametrize(
    "mapping",
    [{"Readers": "alice@example.com"}, {"Readers": [None]}, {"Readers": [""]}, {"Readers": [], "readers": []}, []],
)
def test_invalid_membership_mappings_rejected(mapping):
    """Reject ambiguous or malformed supplied memberships before scanning."""
    with pytest.raises(ValueError):
        _scan(group_memberships=mapping)


def test_collection_follows_tokens_not_external_continuation_uris(monkeypatch):
    """Keep all authenticated pagination on the original resource."""
    calls = []

    def read(url, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            return {"value": [{"name": "a"}], "continuationToken": "a+b", "continuationUri": "https://evil.example"}
        return {"value": [{"name": "b"}]}

    monkeypatch.setattr(m, "request_fabric_json", read)
    assert len(m._collection("https://api.fabric.microsoft.com/v1/resource", "test-token")) == 2
    assert calls[1] == "https://api.fabric.microsoft.com/v1/resource?continuationToken=a%2Bb"


def test_repeated_pagination_is_reported(monkeypatch):
    """Do not loop or return partial roles on a broken continuation chain."""
    monkeypatch.setattr(m, "request_fabric_json", lambda *a, **kw: {"value": [], "continuationToken": "same"})
    with pytest.raises(RuntimeError, match="repeated"):
        m._collection("https://api.fabric.microsoft.com/v1/resource", "test-token")


def test_portal_redirect_refused_and_http_details_not_exposed(monkeypatch):
    """Do not forward credentials or echo server bodies into returned coverage."""
    assert m.PortalNoRedirect().redirect_request(None, None, 302, None, None, "https://evil.example") is None

    class Opener:
        def open(self, request, timeout):
            assert request.get_method() == "GET"
            raise HTTPError(request.full_url, 302, "redirect", {}, io.BytesIO(b"sensitive server detail"))

    monkeypatch.setattr(m, "build_opener", lambda *args: Opener())
    with pytest.raises(RuntimeError, match="HTTP 302") as error:
        m._portal_access(ORIGIN + "/metadata/access/artifacts/" + ITEM, "test-token")
    assert "sensitive" not in str(error.value)


def test_public_export_and_preview_lifecycle():
    """Expose the workaround without promoting it into the supported Live API."""
    from fabricops_kit import scan_onelake_role_members
    from fabricops_kit.public_api import PREVIEW_PUBLIC_API, SUPPORTED_PUBLIC_API

    assert scan_onelake_role_members is m.scan_onelake_role_members
    name = f"{m.__name__}.scan_onelake_role_members"
    assert name in PREVIEW_PUBLIC_API
    assert name not in SUPPORTED_PUBLIC_API


def test_explicit_member_type_is_used_when_portal_type_is_unknown(monkeypatch):
    """Use an explicit User type without inferring it from a readable name."""
    _sources(monkeypatch, members={"microsoftEntraMembers": [{"objectId": "group-1", "objectType": "User"}]})
    result = _scan()
    role_users = [row for row in result["users"] if row["permission_source"] == "ONELAKE_ROLE"]
    assert len(role_users) == 1
    assert role_users[0]["identity_source"] == "API"


def test_empty_membership_is_unverified_and_does_not_invent_users(monkeypatch):
    """An empty supplied list must not become directory proof or a user row."""
    _sources(monkeypatch)
    result = _scan(group_memberships={"Data Readers": []})
    assert result["users"] == []
    assert any(row["status"] == "CALLER_SUPPLIED_MEMBERSHIP_UNVERIFIED" for row in result["coverage"])


def test_changed_role_members_shape_fails_explicitly(monkeypatch):
    """Stop if the primary API's member collection is no longer recognizable."""
    _sources(monkeypatch, members={"microsoftEntraMembers": "changed"})
    with pytest.raises(RuntimeError, match="response changed"):
        _scan()


def test_changed_portal_response_is_rejected(monkeypatch):
    """Do not interpret a different portal shape as an empty access list."""

    class Opener:
        def open(self, request, timeout):
            return io.BytesIO(b'{"unexpected": []}')

    monkeypatch.setattr(m, "build_opener", lambda *args: Opener())
    with pytest.raises(RuntimeError, match="response changed"):
        m._portal_access(ORIGIN, "test-token")
