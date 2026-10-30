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
from ..helper import encode_path_identifier, make_rest_call
from soar_sdk.exceptions import ActionFailure


class GetMessageDetailsParams(Params):
    message_id: str = Param(
        description="The unique identifier of the message to retrieve",
        primary=True,
        cef_types=["webex message id"],
    )


class GetMessageDetailsOutput(WebexOutput):
    id: str = OutputField(
        cef_types=["webex message id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
        column_name="ID",
    )
    text: str = OutputField(example_values=["hello test"], column_name="Text")
    roomId: str = OutputField(
        cef_types=["webex room id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
        column_name="Room ID",
    )
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
        column_name="Person Email",
    )
    created: str = OutputField(example_values=["2025-05-09T05:37:36.687Z"])
    html: str = OutputField(
        example_values=[
            'hello <spark-mention data-object-type="person" data-object-id="TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST">test</spark-mention>'  # pragma: allowlist secret
        ]
    )
    roomType: str = OutputField(example_values=["group"])


@app.action(
    description="Retrieve the details of a specific Webex message by message ID",
    action_type="investigate",
    render_as="table",
    read_only=True,
)
def get_message_details(
    params: GetMessageDetailsParams, soar: SOARClient, asset: Asset
) -> GetMessageDetailsOutput:
    message_id = encode_path_identifier(params.message_id)
    if not message_id:
        raise ActionFailure("Invalid message_id")
    response = make_rest_call(
        asset,
        consts.WEBEX_GET_MESSAGES_DETAILS_ENDPOINT.format(message_id=message_id),
    )
    soar.set_message("Message details retrieved successfully")
    return GetMessageDetailsOutput(**response)
