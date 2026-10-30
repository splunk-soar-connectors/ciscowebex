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
from ..helper import encode_path_identifier, make_rest_call, remove_password_fields
from soar_sdk.exceptions import ActionFailure


class GetMeetingDetailsParams(Params):
    meeting_id: str = Param(
        description="The unique identifier of the meeting being requested (UUID format)",
        primary=True,
        cef_types=["webex meeting id"],
    )
    host_email: str | None = Param(
        description="Email address of the meeting host (for admin-level access)",
        primary=True,
        cef_types=["email"],
    )
    current: bool | None = Param(
        description="Whether to retrieve only the current scheduled meeting of the series (true or false)",
        default=False,
    )


class AttendeeprivilegesOutput(WebexOutput):
    enabledAnnotate: bool | None = OutputField()
    enabledChatHost: bool | None = OutputField()
    enabledChatOtherParticipants: bool | None = OutputField()
    enabledChatPresenter: bool | None = OutputField()
    enabledContactOperatorPrivately: bool | None = OutputField()
    enabledPrintDocument: bool | None = OutputField()
    enabledRemoteControl: bool | None = OutputField()
    enabledSaveDocument: bool | None = OutputField()
    enabledShareContent: bool | None = OutputField()
    enabledViewAnyDocument: bool | None = OutputField()
    enabledViewAnyPage: bool | None = OutputField()
    enabledViewParticipantList: bool | None = OutputField()
    enabledViewThumbnails: bool | None = OutputField()


class AudioconnectionoptionsOutput(WebexOutput):
    allowAttendeeToUnmuteSelf: bool | None = OutputField()
    allowHostToUnmuteParticipants: bool | None = OutputField()
    audioConnectionType: str = OutputField(example_values=["webexAudio"])
    enabledAudienceCallBack: bool | None = OutputField()
    enabledGlobalCallIn: bool | None = OutputField()
    enabledTollFreeCallIn: bool | None = OutputField()
    entryAndExitTone: str = OutputField(example_values=["noTone"])
    muteAttendeeUponEntry: bool | None = OutputField()


class MeetingoptionsOutput(WebexOutput):
    enabledChat: bool | None = OutputField()
    enabledFileTransfer: bool | None = OutputField()
    enabledVideo: bool | None = OutputField()


class SimultaneousinterpretationOutput(WebexOutput):
    enabled: bool | None = OutputField()


class CallinnumbersOutput(WebexOutput):
    callInNumber: str = OutputField(example_values=["+1-000-025-6800"])
    label: str = OutputField(example_values=["Call-in toll number (US/Canada)"])
    tollType: str = OutputField(example_values=["toll"])


class LinksOutput(WebexOutput):
    href: str = OutputField(
        example_values=[
            "/v1/meetings/testa706b64041559c664a83e6btest/globalCallinNumbers"
        ]
    )
    method: str = OutputField(example_values=["GET"])
    rel: str = OutputField(example_values=["globalCallinNumbers"])


class TelephonyOutput(WebexOutput):
    accessCode: str = OutputField(example_values=["26620031238"])
    callInNumbers: list[CallinnumbersOutput] | None = OutputField()
    links: list[LinksOutput] | None = OutputField()


class GetMeetingDetailsOutput(WebexOutput):
    id: str = OutputField(
        cef_types=["webex meeting id"],
        example_values=["ctest706b64041559c664a83e6bfcf60_20250509Ttest0Z"],
        column_name="ID",
    )
    title: str = OutputField(example_values=["Test meeting"], column_name="Title")
    webLink: str = OutputField(
        example_values=[
            "https://example.webex.com/example/j.php?MTID=me0a791a45ee400f06576ed07dd940d3e"
        ],
        column_name="Meeting Weblink",
    )
    start: str = OutputField(
        example_values=["2025-05-09T12:20:00Z"], column_name="Start Time"
    )
    end: str = OutputField(
        example_values=["2025-05-09T13:20:00Z"], column_name="End Time"
    )
    timezone: str = OutputField(example_values=["UTC"], column_name="Time Zone")
    agenda: str | None = OutputField()
    allowAnyUserToBeCoHost: bool | None = OutputField()
    allowAuthenticatedDevices: bool | None = OutputField()
    allowFirstUserToBeCoHost: bool | None = OutputField()
    attendeeDidJoin: bool | None = OutputField()
    attendeePrivileges: AttendeeprivilegesOutput | None = OutputField()
    audioConnectionOptions: AudioconnectionoptionsOutput | None = OutputField()
    dialInIpAddress: str = OutputField(example_values=["103.xx.xx.68"])
    enableAutomaticLock: bool | None = OutputField()
    enableConnectAudioBeforeHost: bool | None = OutputField()
    enabledAutoRecordMeeting: bool | None = OutputField()
    enabledBreakoutSessions: bool | None = OutputField()
    enabledJoinBeforeHost: bool | None = OutputField()
    enabledLiveStream: bool | None = OutputField()
    enabledVisualWatermark: bool | None = OutputField()
    excludePassword: bool | None = OutputField()
    hasChat: bool | None = OutputField()
    hasClosedCaption: bool | None = OutputField()
    hasPolls: bool | None = OutputField()
    hasQA: bool | None = OutputField()
    hasRecording: bool | None = OutputField()
    hasRegistrants: bool | None = OutputField()
    hasRegistration: bool | None = OutputField()
    hasSlido: bool | None = OutputField()
    hasTranscription: bool | None = OutputField()
    hostDidJoin: bool | None = OutputField()
    hostDisplayName: str = OutputField(example_values=["test user"])
    hostEmail: str = OutputField(example_values=["example@example.com"])
    hostKey: str = OutputField(example_values=["889047"])
    hostUserId: str = OutputField(
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ]
    )
    isModified: bool | None = OutputField()
    joinBeforeHostMinutes: float = OutputField(example_values=[5])
    meetingNumber: str = OutputField(example_values=["26620031238"])
    meetingOptions: MeetingoptionsOutput | None = OutputField()
    meetingSeriesId: str = OutputField(
        example_values=["testa706b64041559c664a83e6btest"]
    )
    meetingType: str = OutputField(example_values=["scheduledMeeting"])
    publicMeeting: bool | None = OutputField()
    reminderTime: float = OutputField(example_values=[15])
    scheduledMeetingId: str = OutputField(
        example_values=["937f2ef03e1a49be883320fe35fde314_20250508T140000Z"]
    )
    scheduledType: str = OutputField(example_values=["meeting"])
    sessionTypeId: float = OutputField(example_values=[159])
    simultaneousInterpretation: SimultaneousinterpretationOutput | None = OutputField()
    sipAddress: str = OutputField(example_values=["26000031238@webex.com"])
    siteUrl: str = OutputField(example_values=["example.webex.com"])
    state: str = OutputField(example_values=["ready"])
    telephony: TelephonyOutput | None = OutputField()
    unlockedMeetingJoinSecurity: str = OutputField(example_values=["allowJoin"])


@app.action(
    description="Retrieve details of a specific Webex meeting using meeting ID or meeting number",
    action_type="investigate",
    render_as="table",
    read_only=True,
)
def get_meeting_details(
    params: GetMeetingDetailsParams, soar: SOARClient, asset: Asset
) -> GetMeetingDetailsOutput:
    meeting_id = encode_path_identifier(params.meeting_id)
    if not meeting_id:
        raise ActionFailure("Invalid meeting_id")
    query_params = {}
    if params.current:
        query_params["current"] = str(params.current).lower()
    if params.host_email:
        query_params["hostEmail"] = params.host_email

    response = make_rest_call(
        asset,
        consts.WEBEX_GET_MEETINGS_DETAILS.format(meeting_id=meeting_id),
        params=query_params,
    )
    soar.set_message("Successfully retrieved meeting details")
    return GetMeetingDetailsOutput(**remove_password_fields(response))
