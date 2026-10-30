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
import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from src.actions import make_request as module
from src.app import app
from tests.test_oauth_state_migration import make_asset


@pytest.fixture
def run_action(monkeypatch):
    def run(parameters, asset=None):
        manager = Mock()
        monkeypatch.setattr(app, "actions_manager", manager)
        status = module.make_request(
            parameters, soar=SimpleNamespace(), asset=asset or SimpleNamespace()
        )
        manager.add_result.assert_called_once()
        return status, manager.add_result.call_args.args[0]

    return run


@pytest.mark.parametrize(
    "parameters,query",
    [
        (
            {
                "endpoint": "rooms?existing=keep&replace=old",
                "query_parameters": '{"replace":"new","max":0,"empty":"","enabled":false,"tag":["a","b"]}',
            },
            {
                "existing": ["keep"],
                "replace": ["new"],
                "max": ["0"],
                "empty": [""],
                "enabled": ["false"],
                "tag": ["a", "b"],
            },
        ),
        (
            {
                "endpoint": "/rooms?existing=keep",
                "query_parameters": "?tag=a&tag=b&empty=",
            },
            {"existing": ["keep"], "tag": ["a", "b"], "empty": [""]},
        ),
    ],
)
def test_query_formats_merge_without_losing_values(
    monkeypatch, run_action, parameters, query
):
    request = Mock(return_value=httpx.Response(200, text="ok"))
    monkeypatch.setattr(module, "request", request)
    status, result = run_action(parameters)
    assert status
    url = httpx.URL(request.call_args.args[2])
    assert url.scheme == "https"
    assert url.host == "webexapis.com"
    assert url.path == "/v1/rooms"
    assert {key: url.params.get_list(key) for key in url.params} == query
    assert result.get_data() == [{"status_code": 200, "response_body": "ok"}]


@pytest.mark.parametrize("body", ['{"text":"hello"}', "[1,2]", "null", "false", "0"])
def test_json_body_is_validated_and_sent_without_reshaping(
    monkeypatch, run_action, body
):
    request = Mock(return_value=httpx.Response(201, text="created"))
    monkeypatch.setattr(module, "request", request)
    status, _ = run_action(
        {"endpoint": "/messages", "http_method": "post", "body": body}
    )
    assert status
    assert request.call_args.args[1] == "POST"
    assert request.call_args.kwargs["content"] == body
    assert request.call_args.kwargs["headers"]["content-type"] == "application/json"


def test_header_names_are_case_insensitive_and_raw_body_is_preserved(
    monkeypatch, run_action
):
    request = Mock(return_value=httpx.Response(200, text="ok"))
    monkeypatch.setattr(module, "request", request)
    status, _ = run_action(
        {
            "endpoint": "/messages",
            "http_method": "POST",
            "headers": '{"content-type":"text/plain","X-Test":"value"}',
            "body": "not JSON",
        }
    )
    assert status
    assert request.call_args.kwargs["content"] == "not JSON"
    headers = request.call_args.kwargs["headers"]
    assert headers.get_list("content-type") == ["text/plain"]
    assert headers["x-test"] == "value"


@pytest.mark.parametrize(
    "parameters",
    [
        {"endpoint": "https://other.example/rooms"},
        {"endpoint": "//other.example/rooms"},
        {"endpoint": "/../rooms"},
        {"endpoint": "/%2e%2e/rooms"},
        {"endpoint": "/rooms#fragment"},
        {"endpoint": "/rooms\n"},
        {"endpoint": "/rooms with spaces"},
        {"endpoint": ""},
        {"endpoint": "/rooms", "headers": "[]"},
        {"endpoint": "/rooms", "headers": '{"X-Test":123}'},
        {"endpoint": "/rooms", "headers": '{"X-Test":"sensitive-header\\nvalue"}'},
        {"endpoint": "/rooms", "headers": "{"},
        {"endpoint": "/rooms", "query_parameters": "[]"},
        {"endpoint": "/rooms", "body": "{"},
        {"endpoint": "/rooms", "http_method": "TRACE"},
        {"endpoint": "/rooms", "timeout": 0},
        {"endpoint": "/rooms", "timeout": -1},
        {"endpoint": "/rooms", "timeout": 1.5},
    ],
)
def test_invalid_input_fails_before_request(monkeypatch, run_action, parameters):
    request = Mock()
    monkeypatch.setattr(module, "request", request)
    status, result = run_action(parameters)
    assert not status
    request.assert_not_called()
    assert result.get_message()
    assert "sensitive-header" not in result.get_message()


@pytest.mark.parametrize("auth_mode", ["pat", "oauth"])
@pytest.mark.parametrize(
    "asset_verify,override", [(False, None), (True, False), (False, True)]
)
def test_shared_auth_tls_timeout_and_cleanup(
    monkeypatch, run_action, auth_mode, asset_verify, override
):
    asset, _ = make_asset(
        {"token": {"access_token": "old-access", "refresh_token": "old-refresh"}}
    )
    asset.authorization_key = "synthetic-pat" if auth_mode == "pat" else None
    asset.verify_server_cert = asset_verify
    seen = []

    def handler(request):
        seen.append(request)
        if request.url.path == "/v1/access_token":
            return httpx.Response(
                200, json={"access_token": "fresh-access", "expires_in": 3600}
            )
        expected_token = "synthetic-pat" if auth_mode == "pat" else "fresh-access"
        assert request.headers["Authorization"] == "Bearer " + expected_token
        assert json.loads(request.content) == {"text": "hello"}
        return httpx.Response(202, text="accepted")

    clients = []
    client_cls = httpx.Client

    def create(**kwargs):
        client = client_cls(**kwargs, transport=httpx.MockTransport(handler))
        clients.append((kwargs, client))
        return client

    monkeypatch.setattr(httpx, "Client", create)
    parameters = {
        "endpoint": "/messages",
        "http_method": "POST",
        "body": '{"text":"hello"}',
        "headers": '{"Authorization":"ignored-override"}',
        "timeout": 7,
    }
    if override is not None:
        parameters["verify_ssl"] = override
    status, result = run_action(parameters, asset)
    assert status
    assert result.get_data() == [{"status_code": 202, "response_body": "accepted"}]
    verify = asset_verify if override is None else override
    assert all(
        kwargs["verify"] is verify and kwargs["timeout"] == 7 for kwargs, _ in clients
    )
    assert all(client.is_closed for _, client in clients)
    assert [r.url.path for r in seen] == (
        ["/v1/messages"] if auth_mode == "pat" else ["/v1/access_token", "/v1/messages"]
    )


@pytest.mark.parametrize(
    "code,body,content_type",
    [
        (200, '{"items":[]}', "application/json"),
        (404, "not found", "text/plain"),
        (500, "<p>unavailable</p>", "text/html"),
        (204, "", ""),
    ],
)
def test_response_status_and_text_are_returned_verbatim(
    monkeypatch, run_action, code, body, content_type
):
    monkeypatch.setattr(
        module,
        "request",
        Mock(
            return_value=httpx.Response(
                code, text=body, headers={"Content-Type": content_type}
            )
        ),
    )
    status, result = run_action({"endpoint": "/rooms"})
    assert status
    assert result.get_data() == [{"status_code": code, "response_body": body}]


def test_transport_failure_is_reported_through_shared_helper(monkeypatch, run_action):
    asset, _ = make_asset()
    asset.authorization_key = "synthetic-pat"

    def handler(request):
        raise httpx.ConnectError("network unavailable", request=request)

    client_cls = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: client_cls(**kw, transport=httpx.MockTransport(handler)),
    )
    status, result = run_action({"endpoint": "/rooms"}, asset)
    assert not status
    assert "Error Connecting to server" in result.get_message()


def test_make_request_registration_and_defaults():
    action = module.make_request
    assert action.meta.identifier == "make_request"
    assert action.meta.action == "make request"
    assert not action.meta.read_only
    params = action.params_class(endpoint="/rooms")
    assert params.http_method == "GET"
    assert params.timeout == 30
    assert params.verify_ssl is None
    fields = {field["data_path"] for field in action.meta.output._to_json_schema()}
    assert fields == {
        "action_result.data.*.status_code",
        "action_result.data.*.response_body",
    }


def test_oauth_401_retry_reuses_auth_and_preserves_request_body(
    monkeypatch, run_action
):
    asset, _ = make_asset(
        sdk={
            "oauth": {
                "client_id": "client-id",
                "token": {
                    "access_token": "old-access",
                    "refresh_token": "refresh",
                    "expires_at": 9999999999,
                },
            }
        }
    )
    requests = []
    bodies = []

    def handler(request):
        requests.append(request.url.path)
        if request.url.path == "/v1/access_token":
            return httpx.Response(
                200, json={"access_token": "fresh-access", "expires_in": 3600}
            )
        bodies.append(request.content)
        if len(bodies) == 1:
            assert request.headers["Authorization"] == "Bearer old-access"
            return httpx.Response(401, json={"message": "expired"})
        assert request.headers["Authorization"] == "Bearer fresh-access"
        return httpx.Response(200, text="created")

    client_cls = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: client_cls(**kw, transport=httpx.MockTransport(handler)),
    )
    status, result = run_action(
        {
            "endpoint": "/messages",
            "http_method": "POST",
            "body": '{"text":"retry safely after rejected token"}',
        },
        asset,
    )
    assert status
    assert result.get_data() == [{"status_code": 200, "response_body": "created"}]
    assert requests == ["/v1/messages", "/v1/access_token", "/v1/messages"]
    assert len(bodies) == 2
    assert bodies[0] == bodies[1]
