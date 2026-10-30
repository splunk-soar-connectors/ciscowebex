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
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import OutputField
from soar_sdk.params import Param, Params
from ..app import Asset, app
from ..output_models import WebexOutput
from .. import consts
from ..helper import make_rest_call, validate_integer
from soar_sdk.exceptions import ActionFailure


class ListMessagesParams(Params):
    room_id: str = Param(
        description="The ID of the room to list messages from",
        primary=True,
        cef_types=["webex room id"],
    )
    parent_id: str | None = Param(
        description="List messages in a thread by parent message ID",
        primary=True,
        cef_types=["webex message id"],
    )
    before: str | None = Param(
        description="List messages sent before a specific date/time (ISO 8601 format)"
    )
    before_message: str | None = Param(
        description="List messages sent before a specific message ID"
    )
    limit: float | None = Param(
        description="The maximum number of messages to return (default 50, max 100)",
        default=50,
    )


class ListMessagesOutput(WebexOutput):
    id: str = OutputField(
        cef_types=["webex message id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
        column_name="ID",
    )
    text: str = OutputField(example_values=["hello test"], column_name="Text")
    personId: str = OutputField(
        cef_types=["webex user id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
        column_name="Person ID",
    )
    personEmail: str = OutputField(
        cef_types=["email"],
        example_values=["example@example.com"],
        column_name="Email",
    )
    created: str = OutputField(example_values=["2025-05-09T05:37:36.687Z"])
    html: str = OutputField(
        example_values=[
            'hello <spark-mention data-object-type="person" data-object-id="TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST">test</spark-mention>'  # pragma: allowlist secret
        ]
    )
    meetingId: str = OutputField(
        cef_types=["webex meeting id"],
        example_values=["9testf03e1a49be883320fe35fde314_I_6522066146543test"],
    )
    parentId: str = OutputField(
        cef_types=["webex message id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
    )
    roomId: str = OutputField(
        cef_types=["webex room id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
    )
    roomType: str = OutputField(example_values=["group"])


class ListMessagesSummary(WebexOutput):
    message: str | None = OutputField()
    total_messages: int | None = OutputField()


@app.action(
    description="Retrieve a list of messages from a Webex room or 1:1 conversation",
    render_as="table",
    summary_type=ListMessagesSummary,
    action_type="investigate",
    read_only=True,
)
def list_messages(
    params: ListMessagesParams, soar: SOARClient, asset: Asset
) -> list[ListMessagesOutput]:
    limit = validate_integer(params.limit or 50, "limit")
    if not params.room_id and not params.parent_id:
        raise ActionFailure("You must provide at least 'room_id' or 'parent_id'.")

    query_params = {}
    for api_name, param_name in consts.PARAMETER_LIST_FOR_LIST_MESSAGES.items():
        value = getattr(params, param_name, None)
        if value:
            query_params[api_name] = value
    if limit:
        query_params["max"] = limit

    response = make_rest_call(asset, consts.WEBEX_MESSAGE_ENDPOINT, params=query_params)
    messages = response.get("items", [])
    if not isinstance(messages, list):
        messages = [messages]
    soar.set_summary(
        ListMessagesSummary(
            message="Messages retrieved successfully", total_messages=len(messages)
        )
    )
    return [ListMessagesOutput(**item) for item in messages]
