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
from urllib.parse import parse_qsl, unquote, urlsplit

import httpx
from soar_sdk.action_results import MakeRequestOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import MakeRequestParams, Param

from .. import consts
from ..app import Asset, app
from ..helper import request, validate_integer

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]


class WebexMakeRequestParams(MakeRequestParams):
    http_method: str = Param(
        description="HTTP method to use for the Webex API request.",
        required=False,
        default="GET",
        value_list=HTTP_METHODS,
    )
    endpoint: str = Param(
        description="Webex API path relative to https://webexapis.com/v1, for example '/rooms'. Do not include the base URL or '/v1' prefix."
    )
    body: str | None = Param(
        description="Request body. Must be valid JSON when Content-Type contains 'json' (the default); otherwise sent as raw text."
    )
    timeout: int = Param(
        description="Positive request timeout in seconds, including OAuth token requests.",
        required=False,
        default=consts.WEBEX_DEFAULT_TIMEOUT,
    )
    verify_ssl: bool | None = Param(
        description="Override certificate verification for this request and OAuth token requests. Omit to use the asset setting."
    )


def _build_url(endpoint: str) -> httpx.URL:
    if (
        not endpoint
        or any(
            char.isspace() or ord(char) < 32 or ord(char) == 127 for char in endpoint
        )
        or "\\" in endpoint
    ):
        raise ActionFailure(
            "endpoint must be a nonempty Webex API path without whitespace or control characters"
        )
    try:
        parsed = urlsplit(endpoint)
    except ValueError:
        raise ActionFailure("Invalid Webex API endpoint") from None
    if parsed.scheme or parsed.netloc or parsed.fragment:
        raise ActionFailure(
            "endpoint must be a Webex API path without a base URL or fragment"
        )
    path = parsed.path
    if not path or any(part in {".", ".."} for part in unquote(path).split("/")):
        raise ActionFailure("endpoint must be a Webex API path without dot segments")
    endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    return httpx.URL(f"{consts.BASE_URL}{endpoint}")


def _headers(value: str | None) -> httpx.Headers:
    headers = httpx.Headers({"Content-Type": "application/json"})
    if value:
        try:
            extra = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            raise ActionFailure(
                "headers must be a JSON object of string values"
            ) from None
        if not isinstance(extra, dict) or any(
            not isinstance(item, str) or "\r" in item or "\n" in item
            for item in extra.values()
        ):
            raise ActionFailure("headers must be a JSON object of string values")
        try:
            headers.update(extra)
        except (ValueError, TypeError, UnicodeError):
            raise ActionFailure("Invalid HTTP headers") from None
    return headers


@app.make_request()
def make_request(params: WebexMakeRequestParams, asset: Asset) -> MakeRequestOutput:
    """Send an authenticated Webex API request and return its HTTP status and response text."""
    method = params.http_method.upper()
    if method not in HTTP_METHODS:
        raise ActionFailure("Unsupported http_method")
    timeout = validate_integer(params.timeout, "timeout")
    url = _build_url(params.endpoint)
    headers = _headers(params.headers)
    if params.query_parameters:
        try:
            query = json.loads(params.query_parameters)
        except json.JSONDecodeError:
            query = parse_qsl(
                params.query_parameters.removeprefix("?"), keep_blank_values=True
            )
        else:
            if not isinstance(query, dict):
                raise ActionFailure("query_parameters JSON must be an object")
        url = url.copy_with(
            query=str(httpx.QueryParams(url.query).merge(query)).encode()
        )
    if params.body is not None and "json" in headers.get("Content-Type", "").lower():
        try:
            json.loads(params.body)
        except json.JSONDecodeError:
            raise ActionFailure(
                "body must be valid JSON for the selected Content-Type"
            ) from None

    response = request(
        asset,
        method,
        str(url),
        headers=headers,
        content=params.body,
        timeout=timeout,
        verify_ssl=params.verify_ssl,
    )
    return MakeRequestOutput(
        status_code=response.status_code, response_body=response.text
    )
