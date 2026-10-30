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
import mimetypes

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import OutputField
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from .. import consts
from ..app import Asset, app
from ..output_models import WebexOutput
from ..helper import make_rest_call


class SendMessageParams(Params):
    endpoint_id: str = Param(
        description="User or Room ID",
        primary=True,
        cef_types=["webex user id", "webex room id"],
        column_name="Endpoint ID",
    )
    destination_type: str = Param(
        description="Destination Type", value_list=["room", "user"]
    )
    message: str | None = Param(description="Message", default="")
    card: str | None = Param(description="AdaptiveCard format card", default="")
    vault_id: str | None = Param(
        description="Vault ID to send file to webex", default=""
    )
    is_markdown: bool | None = Param(description="Is the message Markdown formatted")


class SendMessageOutput(WebexOutput):
    id: str = OutputField(
        cef_types=["webex message id"],
        example_values=[
            "testzcGFyazovLABCVzL1JLT00vODliODk1ZWYtYjk2YS0zMTk0LTlhNDQtNDATEST4MzEXAMPLE"  # pragma: allowlist secret
        ],
    )
    created: str = OutputField(
        example_values=["2018-01-08T21:27:31.755Z", "2018-03-30T18:36:01.210Z"]
    )
    personEmail: str = OutputField(
        cef_types=["email"], example_values=["examplemail@test.com"]
    )
    personId: str = OutputField(
        example_values=[
            "L2szY29zcGFyazovLABCVzL1JLT00vODliODk1ZWYtYjk2YS0zMTk0TESTNDQtNDAxZTk4MzEXAMPLE"  # pragma: allowlist secret
        ]
    )
    roomId: str = OutputField(
        example_values=[
            "L2szY29zcGFyazovLABCVzL1JLT00vODliODk1ZWYtYjk2YS0zMTESTTlhNDQtNDAxZTk4MzEXAMPLE"  # pragma: allowlist secret
        ]
    )
    roomType: str = OutputField(example_values=["direct", "group"])
    text: str = OutputField(example_values=["Compile Test", "hello room"])
    toPersonId: str = OutputField(
        example_values=[
            "L2lzY1zcAByazovL3VzL1HNT1BMRS9hMzllMGQ4Mi01ZWE0LTQ3OTESTWM3Zi00M2E0MTI4MjEXAMPLE"  # pragma: allowlist secret
        ]
    )
    status: str = OutputField(
        column_name="Status", example_values=["success", "failed"]
    )


class SendMessageSummary(WebexOutput):
    message: str | None = OutputField()


@app.action(
    description="Send message to user or room",
    action_type="generic",
    read_only=False,
    render_as="table",
    summary_type=SendMessageSummary,
)
def send_message(
    params: SendMessageParams, soar: SOARClient, asset: Asset
) -> SendMessageOutput:
    destination_field = "toPersonId" if params.destination_type == "user" else "roomId"
    message_field = "markdown" if params.is_markdown else "text"
    if not params.message and not params.card and not params.vault_id:
        raise ActionFailure(consts.WEBEX_ERROR_MESSAGE_REQUIRED)
    if params.card and params.vault_id:
        raise ActionFailure("Can only set one of card or vault_id.")

    message_payload = {
        destination_field: params.endpoint_id,
        message_field: params.message or "",
    }
    json_data = None
    data = None
    files = None
    if params.card:
        try:
            card_attachment = json.loads(params.card)
        except (TypeError, ValueError) as exc:
            raise ActionFailure(f"Error deserializing card attachment: {exc}") from exc
        message_payload["attachments"] = [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card_attachment,
            }
        ]
        json_data = message_payload
    elif params.vault_id:
        attachments = soar.vault.get_attachment(vault_id=params.vault_id)
        if not attachments:
            raise ActionFailure(consts.WEBEX_ERR_NOT_IN_VAULT)
        attachment = attachments[0]
        with attachment.open("rb") as file_obj:
            file_content = file_obj.read()
        mime_type = attachment.mime_type or mimetypes.guess_type(attachment.name)[0]
        data = message_payload
        files = {"files": (attachment.name, file_content, mime_type)}
    else:
        json_data = message_payload

    response = make_rest_call(
        asset,
        consts.WEBEX_MESSAGE_ENDPOINT,
        method="post",
        json_data=json_data,
        data=data,
        files=files,
    )
    soar.set_summary(SendMessageSummary(message=consts.WEBEX_SUCCESS_SEND_MESSAGE))
    soar.set_message(consts.WEBEX_SUCCESS_SEND_MESSAGE)
    return SendMessageOutput(**response, status="success")
