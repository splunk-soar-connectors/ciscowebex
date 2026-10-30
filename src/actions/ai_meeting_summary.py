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
import json
from .. import consts
from ..helper import encode_path_identifier, make_rest_call
from soar_sdk.exceptions import ActionFailure
from .custom_views import ai_meeting_summary_view


class AiMeetingSummaryParams(Params):
    recording_id: str = Param(
        description="Unique identifier of the Webex recording.",
        primary=True,
        cef_types=["webex recording id"],
    )
    site_url: str = Param(
        description="Unique identifier of the Webex recording.eg: company.webex.com",
        primary=True,
    )


class AiMeetingSummaryOutput(WebexOutput):
    recordingId: str = OutputField(
        cef_types=["webex recording id"],
        example_values=["test06506faa48c790592a4198c3test"],
        column_name="Recording ID",
    )
    suggestedNote: str = OutputField(
        cef_types=["webex meeting notes"],
        example_values=[
            "AI-Generated meeting summary and actions items retrieved successfully"
        ],
        column_name="Suggested Note",
    )
    actionItems: str = OutputField(
        cef_types=["webex meeting actions items"],
        example_values=["AI-Generated actions items retrieved successfully"],
        column_name="Action Items",
    )
    actions_items: str = OutputField(
        example_values=["AI-Generated actions items retrieved successfully"]
    )
    recordingName: str = OutputField(example_values=["test recording"])
    summary: str = OutputField(
        example_values=[
            "AI-Generated meeting summary and actions items retrieved successfully"
        ]
    )


@app.action(
    description="Retrieve AI-Generated meeting summary and actions items using its recording ID and site url",
    action_type="investigate",
    read_only=True,
    view_handler=ai_meeting_summary_view,
)
def ai_meeting_summary(
    params: AiMeetingSummaryParams, soar: SOARClient, asset: Asset
) -> list[AiMeetingSummaryOutput]:
    if not params.recording_id or not params.site_url:
        raise ActionFailure(
            "Please provide both recording_id and site_url to retrieve the meeting summary"
        )

    site_url = params.site_url.strip().rstrip("/")
    if site_url.startswith("https://"):
        base_url = site_url
    elif "://" in site_url:
        raise ActionFailure("site_url must use HTTPS")
    else:
        base_url = f"https://{site_url}"

    from urllib.parse import urlsplit

    hostname = (urlsplit(base_url).hostname or "").lower()
    if not hostname.endswith((".webex.com", ".webexapis.com", ".webexcontent.com")):
        raise ActionFailure("site_url must be a Webex host")

    endpoint = (
        f"{base_url}/recordingservice/api/v1/recordings/"
        f"{encode_path_identifier(params.recording_id)}/stream"
    )
    response = make_rest_call(asset, endpoint)
    output = {
        "recordingId": response.get("recordUUID") or params.recording_id,
        "recordingName": response.get("recordName"),
    }

    suggested_url = response.get("suggestedNoteUrl")
    if suggested_url:
        note_response = make_rest_call(
            asset, suggested_url, headers=consts.WEBEX_JSON_HEADERS
        )
        content = note_response.get("content")
        if content:
            try:
                parsed = json.loads(content) if isinstance(content, str) else content
                description = (parsed.get("description") or {}).get("text", "")
                notes = [
                    note.get("text", "")
                    for note in parsed.get("notes", [])
                    if isinstance(note, dict)
                ]
                output["suggestedNote"] = "\n".join(
                    value for value in [description, *notes] if value
                )
            except (json.JSONDecodeError, AttributeError, TypeError):
                output["suggestedNote"] = content

    action_item_url = response.get("actionItemUrl")
    if action_item_url:
        action_response = make_rest_call(
            asset, action_item_url, headers=consts.WEBEX_JSON_HEADERS
        )
        content = action_response.get("content")
        if content:
            try:
                parsed = json.loads(content) if isinstance(content, str) else content
                if isinstance(parsed, list):
                    output["actionItems"] = "\n".join(
                        str(item.get("content", ""))
                        for item in parsed
                        if isinstance(item, dict) and item.get("content")
                    )
                else:
                    output["actionItems"] = str(parsed)
            except (json.JSONDecodeError, TypeError):
                output["actionItems"] = content

    if not (output.get("actionItems") or output.get("suggestedNote")):
        raise ActionFailure("AI generated meeting summary and actions items not found")
    soar.set_message(
        "AI generated meeting summary and actions items retrieved successfully"
    )
    return [AiMeetingSummaryOutput(**output)]
