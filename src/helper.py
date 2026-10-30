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
from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import quote

import httpx
from soar_sdk.auth import AuthorizationCodeFlow, StaticTokenAuth, create_oauth_client
from soar_sdk.exceptions import ActionFailure

from . import consts


class _ErrorTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "footer", "nav"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "footer", "nav"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth and data.strip():
            self._chunks.append(data.strip())

    def text(self) -> str:
        return "\n".join(self._chunks)


def oauth_flow(asset, asset_id: str, redirect_uri: str) -> AuthorizationCodeFlow:
    if not asset.client_id or not asset.client_secret:
        raise ActionFailure(consts.WEBEX_ERROR_REQUIRED_CONFIG_PARAMS)
    return AuthorizationCodeFlow(
        asset.auth_state,
        asset_id,
        client_id=asset.client_id,
        client_secret=asset.client_secret,
        authorization_endpoint=f"{consts.BASE_URL}/authorize",
        token_endpoint=f"{consts.BASE_URL}{consts.WEBEX_ACCESS_TOKEN_ENDPOINT}",
        redirect_uri=redirect_uri,
        scope=asset.scope.split() if asset.scope else [],
        poll_timeout=consts.OAUTH_WAIT_INTERVALS * consts.OAUTH_WAIT_TIME,
        poll_interval=consts.OAUTH_WAIT_TIME,
    )


def encode_path_identifier(value: str | None) -> str | None:
    if not isinstance(value, str) or not value or value in {".", ".."}:
        return None
    return quote(value, safe="")


def remove_password_fields(value):
    if isinstance(value, dict):
        return {
            key: remove_password_fields(item)
            for key, item in value.items()
            if "password" not in key.lower()
        }
    if isinstance(value, list):
        return [remove_password_fields(item) for item in value]
    return value


def _request(asset, method: str, url: str, **kwargs) -> httpx.Response:
    verify = asset.verify_server_cert if asset.verify_server_cert is not None else True
    try:
        if asset.authorization_key:
            with httpx.Client(
                auth=StaticTokenAuth(asset.authorization_key),
                verify=verify,
                timeout=consts.WEBEX_DEFAULT_TIMEOUT,
            ) as client:
                return client.request(method, url, **kwargs)
        with create_oauth_client(
            asset,
            client_id=asset.client_id,
            client_secret=asset.client_secret,
            token_endpoint=f"{consts.BASE_URL}{consts.WEBEX_ACCESS_TOKEN_ENDPOINT}",
            scope=asset.scope.split() if asset.scope else [],
            verify=verify,
            timeout=consts.WEBEX_DEFAULT_TIMEOUT,
        ) as client:
            return client.request(method, url, **kwargs)
    except httpx.RequestError as exc:
        raise ActionFailure(f"Error Connecting to server. Details: {exc}") from exc


def make_rest_call(
    asset,
    endpoint: str,
    *,
    method: str = "get",
    params: dict | None = None,
    json_data=None,
    data=None,
    files=None,
    headers: dict | None = None,
):
    url = endpoint if endpoint.startswith("https") else f"{consts.BASE_URL}{endpoint}"
    response = _request(
        asset,
        method.upper(),
        url,
        params=params,
        json=json_data,
        data=data,
        files=files,
        headers=headers,
    )
    if response.status_code == 401:
        raise ActionFailure("Access token is expired or invalid")

    content_type = response.headers.get("Content-Type", "")
    if "json" in content_type:
        try:
            response_json = response.json()
        except Exception as exc:
            raise ActionFailure(f"Unable to parse JSON response. Error: {exc}") from exc
        if 200 <= response.status_code < 399:
            return response_json
        text = response.text.replace("{", "{{").replace("}", "}}")
        raise ActionFailure(
            f"Error from server. Status Code: {response.status_code} Data from server: {text}"
        )

    if "html" in content_type:
        parser = _ErrorTextParser()
        parser.feed(response.text)
        error_text = parser.text() or "Cannot parse error details"
        raise ActionFailure(
            f"Status Code: {response.status_code}. Data from server:\n{error_text}\n"
        )

    if not response.text and response.status_code in {200, 204}:
        return {}
    if not response.text:
        raise ActionFailure(
            f"Empty response and no information in the header Status Code: {response.status_code}"
        )
    text = response.text.replace("{", "{{").replace("}", "}}")
    raise ActionFailure(
        f"Can't process response from server. Status Code: {response.status_code} Data from server: {text}"
    )


def validate_integer(value, key: str) -> int | None:
    if value is None or value == "":
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ActionFailure(consts.ERROR_INVALID_INT_PARAM.format(key=key)) from exc
    if parsed < 0:
        raise ActionFailure(consts.ERROR_NEG_INT_PARAM.format(key=key))
    if parsed == 0:
        raise ActionFailure(consts.ERROR_ZERO_INT_PARAM.format(key=key))
    return parsed
