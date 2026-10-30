# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from copy import deepcopy
from types import SimpleNamespace
from urllib.parse import parse_qs

import httpx
import pytest
from soar_sdk.asset_state import AssetState
from soar_sdk.auth import OAuthConfig, SOARAssetOAuthClient
from soar_sdk.auth.client import ConfigurationChangedError, TokenRefreshError
from soar_sdk.exceptions import ActionFailure
from soar_sdk.shims.phantom.encryption_helper import encryption_helper

from src import helper
from src.oauth_state import migrate_legacy_oauth_state


class Backend:
    def __init__(self, state=None):
        self.state = deepcopy(state or {})
        self.saves = 0

    def load_state(self):
        return deepcopy(self.state)

    def save_state(self, state):
        self.state = deepcopy(state)
        self.saves += 1


def make_asset(legacy=None, sdk=None):
    backend = Backend(legacy)
    state = AssetState(backend, "auth", "asset-1")
    if sdk is not None:
        state.put_all(sdk)
        backend.saves = 0
    asset = SimpleNamespace(
        auth_state=state,
        client_id="client-id",
        client_secret="synthetic-client-secret",  # pragma: allowlist secret
        authorization_key=None,
        verify_server_cert=True,
        scope="spark:rooms_read",
    )
    return asset, backend


@pytest.mark.parametrize("encrypted", [False, True])
@pytest.mark.parametrize("tokens", ["both", "access-only", "refresh-only"])
def test_migrates_tokens_and_is_idempotent(encrypted, tokens):
    token = {"expires_in": 999999, "scope": "spark:rooms_read"}
    if tokens != "refresh-only":
        token["access_token"] = "synthetic-old-access"
    if tokens != "access-only":
        token["refresh_token"] = "synthetic-old-refresh"
    plain = deepcopy(token)
    if encrypted:
        for key in ["access_token", "refresh_token"]:
            if key in token:
                token[key] = encryption_helper.encrypt(token[key], "asset-1")
    legacy = {"token": token, "is_encrypted": encrypted, "unrelated": "preserve"}
    asset, backend = make_asset(legacy)

    migrate_legacy_oauth_state(asset)
    migrate_legacy_oauth_state(asset)

    assert backend.saves == 1
    # Legacy state is preserved, and the SDK partition uses its encrypted storage.
    for key, value in legacy.items():
        assert backend.state[key] == value
    assert isinstance(backend.state["auth"], str)
    client = SOARAssetOAuthClient(
        OAuthConfig(
            client_id=asset.client_id, token_endpoint="https://example.com/token"
        ),
        asset.auth_state,
    )
    stored = client.get_stored_token()
    assert stored.access_token == plain.get("access_token", "")
    assert stored.refresh_token == plain.get("refresh_token")
    assert stored.scope == "spark:rooms_read"
    assert stored.expires_in is None
    if tokens != "access-only":
        assert stored.expires_at == 0
        assert stored.is_expired()


@pytest.mark.parametrize(
    "oauth",
    [
        {"token": {"access_token": "new-sdk-token"}, "client_id": "client-id"},
        {"token": None, "client_id": "client-id"},
        {"session": {"state": "pending"}},
        {},
    ],
    ids=["existing-token", "cleared-token", "pending-authorization", "empty-sdk-oauth"],
)
def test_existing_sdk_state_wins(oauth):
    sdk = {"oauth": oauth, "unrelated": {"preserve": True}}
    asset, backend = make_asset({"token": {"access_token": "legacy-token"}}, sdk)

    migrate_legacy_oauth_state(asset)

    assert asset.auth_state.get_all() == sdk
    assert backend.saves == 0


@pytest.mark.parametrize("legacy", [{}, {"token": {}}, {"token": None}])
def test_empty_legacy_state_does_not_write(legacy):
    asset, backend = make_asset(legacy)
    migrate_legacy_oauth_state(asset)
    assert backend.saves == 0
    assert asset.auth_state.get_all() == {}


def test_preserves_other_sdk_auth_keys():
    asset, _ = make_asset(
        {"token": {"access_token": "legacy-token"}}, {"unrelated": {"preserve": True}}
    )
    migrate_legacy_oauth_state(asset)
    assert asset.auth_state.get_all()["unrelated"] == {"preserve": True}


@pytest.mark.parametrize(
    "legacy",
    [
        {"token": "malformed"},
        {"token": {"access_token": ["malformed"]}},
        {"token": {"access_token": "synthetic-access", "scope": ["bad-scope"]}},
    ],
)
def test_malformed_tokens_fail_without_writing_or_exposing_values(legacy):
    asset, backend = make_asset(legacy)
    with pytest.raises(ActionFailure, match="Invalid legacy OAuth token") as exc:
        migrate_legacy_oauth_state(asset)
    assert "synthetic-access" not in str(exc.value)
    assert backend.saves == 0


def test_decryption_failure_is_sanitized_and_does_not_partially_migrate(monkeypatch):
    asset, backend = make_asset(
        {
            "token": {"access_token": "ciphertext", "refresh_token": "secret-refresh"},
            "is_encrypted": True,
        }
    )

    def decrypt(value, asset_id):
        if value == "ciphertext":
            return "decrypted-access"
        raise ValueError("contains secret-refresh")

    monkeypatch.setattr(encryption_helper, "decrypt", decrypt)
    with pytest.raises(ActionFailure, match="Unable to decrypt") as exc:
        migrate_legacy_oauth_state(asset)
    assert "secret-refresh" not in str(exc.value)
    assert "decrypted-access" not in str(exc.value)
    assert backend.saves == 0


def test_first_request_refreshes_migrated_token_and_persists_new_token(monkeypatch):
    asset, backend = make_asset(
        {
            "token": {
                "access_token": "old-access",
                "refresh_token": "old-refresh",
                "expires_in": 999999,
            }
        }
    )
    requests = []

    def handler(request):
        requests.append(request)
        if request.url.path == "/v1/access_token":
            assert parse_qs(request.content.decode()) == {
                "grant_type": ["refresh_token"],
                "client_id": ["client-id"],
                "client_secret": ["synthetic-client-secret"],
                "refresh_token": ["old-refresh"],
            }
            return httpx.Response(
                200,
                json={
                    "access_token": "new-access",
                    "refresh_token": "new-refresh",
                    "expires_in": 3600,
                },
            )
        assert request.headers["Authorization"] == "Bearer new-access"
        return httpx.Response(200, json={"items": []})

    client_cls = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: client_cls(**kw, transport=httpx.MockTransport(handler)),
    )

    assert helper.make_rest_call(asset, "/rooms") == {"items": []}
    assert helper.make_rest_call(asset, "/rooms") == {"items": []}

    assert [request.url.path for request in requests] == [
        "/v1/access_token",
        "/v1/rooms",
        "/v1/rooms",
    ]
    stored = asset.auth_state.get_all()["oauth"]["token"]
    assert stored["access_token"] == "new-access"
    assert stored["refresh_token"] == "new-refresh"
    assert backend.state["token"]["access_token"] == "old-access"


def test_personal_token_mode_does_not_attempt_migration(monkeypatch):
    asset = SimpleNamespace(authorization_key="synthetic-pat", verify_server_cert=True)
    migration = []
    monkeypatch.setattr(
        helper, "migrate_legacy_oauth_state", lambda asset: migration.append(asset)
    )

    def handler(request):
        assert request.headers["Authorization"] == "Bearer synthetic-pat"
        return httpx.Response(200, json={"items": []})

    client_cls = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: client_cls(**kw, transport=httpx.MockTransport(handler)),
    )
    assert helper.make_rest_call(asset, "/rooms") == {"items": []}
    assert migration == []


def test_failed_refresh_does_not_send_old_access_token(monkeypatch):
    asset, _ = make_asset(
        {"token": {"access_token": "old-access", "refresh_token": "old-refresh"}}
    )
    requests = []

    def handler(request):
        requests.append(request.url.path)
        assert request.url.path == "/v1/access_token"
        return httpx.Response(400, json={"error_description": "Refresh revoked"})

    client_cls = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: client_cls(**kw, transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(TokenRefreshError, match="Refresh revoked"):
        helper.make_rest_call(asset, "/rooms")
    assert requests == ["/v1/access_token"]
    assert asset.auth_state.get_all()["oauth"]["token"]["expires_at"] == 0


def test_sdk_credential_change_does_not_revive_legacy_tokens():
    asset, _ = make_asset({"token": {"access_token": "legacy-token"}})
    migrate_legacy_oauth_state(asset)
    client = SOARAssetOAuthClient(
        OAuthConfig(
            client_id="changed-client", token_endpoint="https://example.com/token"
        ),
        asset.auth_state,
    )
    with pytest.raises(ConfigurationChangedError):
        client.get_stored_token()
    migrate_legacy_oauth_state(asset)
    assert not asset.auth_state.get_all()["oauth"].get("token")
