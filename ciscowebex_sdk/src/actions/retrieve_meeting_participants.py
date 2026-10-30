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
from ..helper import encode_path_identifier, make_rest_call, validate_integer
from soar_sdk.exceptions import ActionFailure


class RetrieveMeetingParticipantsParams(Params):
    meeting_id: str = Param(
        description="Unique identifier of the meeting (not personal room meeting)",
        primary=True,
        cef_types=["webex meeting id"],
    )
    breakout_session_id: str | None = Param(
        description="Unique ID of a breakout session in an ended meeting"
    )
    meeting_start_time_from: str | None = Param(
        description="Start time to filter meetings (ISO 8601 format)"
    )
    meeting_start_time_to: str | None = Param(
        description="End time to filter meetings (ISO 8601 format)"
    )
    host_email: str | None = Param(
        description="Email address of the meeting host (admin-only use)",
        primary=True,
        cef_types=["email"],
    )
    join_time_from: str | None = Param(
        description="Start of participant join time range (ISO 8601 format)"
    )
    join_time_to: str | None = Param(
        description="End of participant join time range (ISO 8601 format)"
    )
    limit: float | None = Param(
        description="Max number of participants to return (1-100)", default=10
    )


class DevicesOutput(WebexOutput):
    deviceType: str = OutputField(example_values=["mac"], column_name="Device Type")
    joinedTime: str = OutputField(
        example_values=["2025-05-08T12:40:49Z"], column_name="Joined Time"
    )
    correlationId: str = OutputField(
        example_values=["test927a-496a-4678-ac62-bcbdaadctest"]
    )
    durationSecond: float = OutputField(example_values=[6])
    leftTime: str = OutputField(example_values=["2025-05-08T12:40:55Z"])


class RetrieveMeetingParticipantsOutput(WebexOutput):
    id: str = OutputField(
        cef_types=["webex user id"],
        example_values=[
            "testef03e1a49be883320fe35fde314_I_65220test54323715_3118cefb-81e7-492d-8223-1fe0a353test"
        ],
        column_name="ID",
    )
    email: str = OutputField(
        cef_types=["email"],
        example_values=["example@example.com"],
        column_name="Email",
    )
    devices: list[DevicesOutput] | None = OutputField()
    leftTime: str = OutputField(
        example_values=["2025-05-08T12:40:55Z"], column_name="Laft Time"
    )
    meetingId: str = OutputField(
        cef_types=["webex meeting id"],
        example_values=["test2ef03e1a49be883320fe35fde314_I_65220661465432test"],
        column_name="Meeting ID",
    )
    coHost: bool | None = OutputField()
    displayName: str = OutputField(example_values=["test user"])
    host: bool | None = OutputField()
    hostEmail: str = OutputField(example_values=["example@example.com"])
    invitee: bool | None = OutputField()
    joinedTime: str = OutputField(example_values=["2025-05-08T12:40:49Z"])
    meetingStartTime: str = OutputField(example_values=["2025-05-08T12:40:49Z"])
    muted: bool | None = OutputField()
    siteUrl: str = OutputField(example_values=["example.webex.com"])
    spaceModerator: bool | None = OutputField()
    state: str = OutputField(example_values=["end"])


class RetrieveMeetingParticipantsSummary(WebexOutput):
    message: str | None = OutputField()
    total_participants: int | None = OutputField()


@app.action(
    description="Retrieve all participants in an in-progress or ended Webex meeting",
    render_as="table",
    summary_type=RetrieveMeetingParticipantsSummary,
    action_type="investigate",
    read_only=True,
    verbose="Retrieve a list of participants from a specific Webex meeting instance or series",
)
def retrieve_meeting_participants(
    params: RetrieveMeetingParticipantsParams, soar: SOARClient, asset: Asset
) -> list[RetrieveMeetingParticipantsOutput]:
    meeting_id = encode_path_identifier(params.meeting_id)
    if not meeting_id:
        raise ActionFailure("Invalid meeting_id")

    limit = validate_integer(params.limit or 100, "limit")
    query_params = {"meetingId": params.meeting_id}
    for (
        api_name,
        param_name,
    ) in consts.PARAMETER_LIST_FOR_RETRIEVE_MEETING_PARTICIPANTS.items():
        value = getattr(params, param_name, None)
        if value:
            query_params[api_name] = value
    if limit:
        query_params["max"] = limit

    response = make_rest_call(
        asset, consts.WEBEX_MEETING_PARTICIPANTS_ENDPOINT, params=query_params
    )
    participants = response.get("items", [])
    if not isinstance(participants, list):
        participants = [participants]
    soar.set_summary(
        RetrieveMeetingParticipantsSummary(
            message="Participants retrieved successfully",
            total_participants=len(participants),
        )
    )
    return [RetrieveMeetingParticipantsOutput(**item) for item in participants]
