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
from inspect import unwrap
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit
from unittest.mock import Mock

import httpx
import pytest
from soar_sdk.auth.client import OAuthClientError, TokenRefreshError
from soar_sdk.exceptions import ActionFailure

from src import helper
from src.app import oauth_callback
from tests.test_oauth_state_migration import make_asset


@pytest.fixture
def http_clients(monkeypatch):
    clients = []
    client_cls = httpx.Client

    def install(handler):
        def create(**kwargs):
            client = client_cls(**kwargs, transport=httpx.MockTransport(handler))
            clients.append((kwargs, client))
            return client

        monkeypatch.setattr(httpx, "Client", create)
        return clients

    return install


@pytest.mark.parametrize("verify", [True, False, None])
@pytest.mark.parametrize("fail", [False, True], ids=["success", "token-error"])
def test_authorization_exchange_uses_asset_tls_and_closes_transport(
    http_clients, verify, fail
):
    asset, _ = make_asset()
    asset.verify_server_cert = verify
    requests = []

    def handler(request):
        requests.append(request)
        body = parse_qs(request.content.decode())
        assert body["grant_type"] == ["authorization_code"]
        assert body["redirect_uri"] == ["https://soar.example.com/oauth_callback"]
        assert "code_verifier" not in body
        if fail:
            return httpx.Response(400, json={"error_description": "Code rejected"})
        return httpx.Response(
            200,
            json={
                "access_token": "new-access",
                "refresh_token": "new-refresh",
                "expires_in": 3600,
            },
        )

    clients = http_clients(handler)

    def exchange():
        with helper.oauth_client(
            asset, "https://soar.example.com/oauth_callback"
        ) as client:
            url, _ = client.create_authorization_url("asset-1", use_pkce=False)
            assert "code_challenge" not in parse_qs(urlsplit(url).query)
            return client.fetch_token_with_authorization_code("synthetic-code")

    if fail:
        with pytest.raises(OAuthClientError, match="Code rejected"):
            exchange()
    else:
        assert exchange().access_token == "new-access"

    assert len(requests) == 1
    assert len(clients) == 1
    assert clients[0][0]["verify"] is (verify if verify is not None else True)
    assert clients[0][0]["timeout"] == 30
    assert clients[0][1].is_closed


@pytest.mark.parametrize("verify", [True, False, None])
@pytest.mark.parametrize("fail", [False, True], ids=["success", "refresh-error"])
def test_refresh_and_resource_requests_use_same_tls_and_close(
    http_clients, verify, fail
):
    asset, _ = make_asset(
        {"token": {"access_token": "old-access", "refresh_token": "old-refresh"}}
    )
    asset.verify_server_cert = verify
    requests = []

    def handler(request):
        requests.append(request.url.path)
        if request.url.path == "/v1/access_token":
            assert parse_qs(request.content.decode())["grant_type"] == ["refresh_token"]
            if fail:
                return httpx.Response(
                    400, json={"error_description": "Refresh revoked"}
                )
            return httpx.Response(
                200, json={"access_token": "new-access", "expires_in": 3600}
            )
        assert request.headers["Authorization"] == "Bearer new-access"
        return httpx.Response(200, json={"items": []})

    clients = http_clients(handler)

    if fail:
        with pytest.raises(TokenRefreshError, match="Refresh revoked"):
            helper.make_rest_call(asset, "/rooms")
    else:
        assert helper.make_rest_call(asset, "/rooms") == {"items": []}
    assert requests == (
        ["/v1/access_token"] if fail else ["/v1/access_token", "/v1/rooms"]
    )
    assert len(clients) == 2
    assert all(
        kwargs["verify"] is (verify if verify is not None else True)
        for kwargs, _ in clients
    )
    assert all(kwargs["timeout"] == 30 for kwargs, _ in clients)
    assert all(client.is_closed for _, client in clients)


def test_poll_uses_sdk_session_reload_and_exchange(monkeypatch):
    client = Mock()
    client.get_authorization_code.side_effect = [None, "callback-code"]
    progress = Mock()
    sleep = Mock()
    monkeypatch.setattr(helper.time, "sleep", sleep)
    helper.wait_for_oauth_authorization(client, progress)
    assert client.get_authorization_code.call_count == 2
    client.get_authorization_code.assert_called_with(force_reload=True)
    client.fetch_token_with_authorization_code.assert_called_once_with("callback-code")
    assert progress.call_count == 2
    sleep.assert_called_with(3)


def test_poll_timeout_does_not_exchange_code(monkeypatch):
    client = Mock()
    monkeypatch.setattr(helper.time, "monotonic", Mock(side_effect=[0, 106]))
    with pytest.raises(
        ActionFailure, match="Authorization timed out after 105 seconds"
    ):
        helper.wait_for_oauth_authorization(client, Mock())
    client.fetch_token_with_authorization_code.assert_not_called()


def test_callback_state_validation_uses_scoped_client(http_clients):
    asset, _ = make_asset()
    asset.verify_server_cert = False
    clients = http_clients(
        lambda request: pytest.fail("callback must only store the code")
    )
    with helper.oauth_client(
        asset, "https://soar.example.com/oauth_callback"
    ) as client:
        url, _ = client.create_authorization_url("asset-1", use_pkce=False)
    callback_state = parse_qs(urlsplit(url).query)["state"]
    for state, status in [(["wrong-state"], 400), (callback_state, 200)]:
        response = unwrap(oauth_callback)(
            SimpleNamespace(
                asset=asset, query={"code": ["callback-code"], "state": state}
            )
        )
        assert response.status_code == status
    assert all(
        kwargs["verify"] is False and client.is_closed for kwargs, client in clients
    )
    with helper.oauth_client(asset) as client:
        assert client.get_authorization_code() == "callback-code"
