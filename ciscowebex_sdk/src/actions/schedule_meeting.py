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
from ..helper import make_rest_call, remove_password_fields
from soar_sdk.exceptions import ActionFailure


class ScheduleMeetingParams(Params):
    title: str = Param(description="Title of the meeting (max 128 chars)")
    start: str = Param(description="Meeting start time (ISO 8601 format)")
    end: str = Param(description="Meeting end time (ISO 8601 format)")
    timezone: str | None = Param(
        description="IANA time zone for the meeting (e.g., America/Los_Angeles)"
    )
    description: str | None = Param(description="Meeting description (max 1300 chars)")
    invitees: str | None = Param(
        description="List of emails to invite (comma-separated)"
    )
    password: str | None = Param(
        description="Password to join the meeting", sensitive=True
    )
    send_email: bool | None = Param(
        description="Whether to email host & invitees", default=True
    )
    host_email: str | None = Param(description="Host email (admin scopes required)")
    scheduled_type: str | None = Param(
        description="Type of meeting: meeting, webinar, or personal_room_meeting",
        value_list=["meeting", "webinar", "event", "personalRoomMeeting"],
    )
    adhoc: bool | None = Param(
        description="Create an ad-hoc (instant) meeting in a room"
    )
    room_id: str | None = Param(
        description="Room (space) ID for ad-hoc meeting",
        primary=True,
        cef_types=["webex room id"],
    )
    recurrence: str | None = Param(
        description="Meeting series rule (RFC-2445, e.g. FREQ=DAILY;INTERVAL=1)"
    )
    session_type_id: float | None = Param(
        description="Session type ID (required for webinars)"
    )
    enabled_auto_record_meeting: bool | None = Param(
        description="Automatically record when meeting starts"
    )
    allow_any_user_to_be_co_host: bool | None = Param(
        description="Allow any qualified user to be cohost"
    )
    enabled_join_before_host: bool | None = Param(
        description="Allow attendees to join before host"
    )
    join_before_host_minutes: float | None = Param(
        description="Minutes attendees can join before host (0,5,10,15)"
    )
    enable_connect_audio_before_host: bool | None = Param(
        description="Allow audio connect before host"
    )
    enable_automatic_lock: bool | None = Param(
        description="Automatically lock the meeting after start"
    )
    automatic_lock_minutes: float | None = Param(
        description="Minutes after start to auto-lock"
    )
    public_meeting: bool | None = Param(description="List on public calendar")
    reminder_time: float | None = Param(
        description="Minutes before start to send host reminder"
    )
    unlocked_meeting_join_security: str | None = Param(
        description="How non-invitees join: allowJoin, allowJoinWithLobby, blockFromJoin",
        value_list=["allowJoin", "allowJoinWithLobby", "blockFromJoin"],
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
    callInNumber: str = OutputField(example_values=["+1-000-525-6800"])
    label: str = OutputField(example_values=["Call-in toll number (US/Canada)"])
    tollType: str = OutputField(example_values=["toll"])


class LinksOutput(WebexOutput):
    href: str = OutputField(
        example_values=[
            "/v1/meetings/atest92d8997b4d36bc3ac1893c7ftest/globalCallinNumbers"  # pragma: allowlist secret
        ]
    )
    method: str = OutputField(example_values=["GET"])
    rel: str = OutputField(example_values=["globalCallinNumbers"])


class TelephonyOutput(WebexOutput):
    accessCode: str = OutputField(example_values=["26636572133"])
    callInNumbers: list[CallinnumbersOutput] | None = OutputField()
    links: list[LinksOutput] | None = OutputField()


class ScheduleMeetingOutput(WebexOutput):
    id: str = OutputField(
        cef_types=["webex meeting id"],
        example_values=["test92d8997b4d36bc3ac1893c7ftest8"],
        column_name="ID",
    )
    title: str = OutputField(example_values=["test meeting"], column_name="Title")
    webLink: str = OutputField(
        example_values=[
            "https://example.webex.com/example/j.php?MTID=m6325e89c172b9167381372a0b862a995"
        ],
        column_name="Meeting Weblink",
    )
    start: str = OutputField(
        example_values=["2025-05-10T13:24:00Z"], column_name="Start Time"
    )
    end: str = OutputField(
        example_values=["2025-05-10T14:24:00Z"], column_name="End Time"
    )
    timezone: str = OutputField(example_values=["UTC"], column_name="Time Zone")
    agenda: str = OutputField(
        example_values=[
            "漢字©¬ɸѠ֍۞ਊ௵൬༃ဤᄨᇗኖᏌᔠᛯᜠឦᡤᢻᤐᦪᨃᩔ᪸᭒ᮈᯡᰦ᳀ᴞᵆᵝḈὒ⁇ℰ⅏ⅷ∰⋐⏻サイバーセキュリティインシデント日本標準時⛰⛱⛲⛳⛵✔❤ﬗ╬⎋⌚ ⅍ⅎ€ ₭⁂ᾧ҈₮₯⅏⌛ ⎎☆Ḃ平仮名, ひらがな~"  # noqa: RUF001
        ]
    )
    allowAnyUserToBeCoHost: bool | None = OutputField()
    allowAuthenticatedDevices: bool | None = OutputField()
    allowFirstUserToBeCoHost: bool | None = OutputField()
    attendeePrivileges: AttendeeprivilegesOutput | None = OutputField()
    audioConnectionOptions: AudioconnectionoptionsOutput | None = OutputField()
    automaticLockMinutes: float = OutputField(example_values=[20])
    dialInIpAddress: str = OutputField(example_values=["173.243.2.68"])
    enableAutomaticLock: bool | None = OutputField()
    enableConnectAudioBeforeHost: bool | None = OutputField()
    enabledAutoRecordMeeting: bool | None = OutputField()
    enabledBreakoutSessions: bool | None = OutputField()
    enabledJoinBeforeHost: bool | None = OutputField()
    enabledLiveStream: bool | None = OutputField()
    enabledVisualWatermark: bool | None = OutputField()
    enabledWebcastView: bool | None = OutputField()
    excludePassword: bool | None = OutputField()
    hostDisplayName: str = OutputField(example_values=["test user"])
    hostEmail: str = OutputField(example_values=["ishans@example.com"])
    hostKey: str = OutputField(example_values=["210605"])
    hostUserId: str = OutputField(
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ]
    )
    joinBeforeHostMinutes: float = OutputField(example_values=[5])
    maxWebinarAttendeeCapacity: float = OutputField(example_values=[50000])
    meetingNumber: str = OutputField(example_values=["26600002133"])
    meetingOptions: MeetingoptionsOutput | None = OutputField()
    meetingType: str = OutputField(example_values=["meetingSeries"])
    publicMeeting: bool | None = OutputField()
    reminderTime: float = OutputField(example_values=[10])
    requireAttendeeLogin: bool | None = OutputField()
    restrictToInvitees: bool | None = OutputField()
    scheduledType: str = OutputField(example_values=["meeting"])
    sessionTypeId: float = OutputField(example_values=[159])
    simultaneousInterpretation: SimultaneousinterpretationOutput | None = OutputField()
    sipAddress: str = OutputField(example_values=["2660000000133@webex.com"])
    siteUrl: str = OutputField(example_values=["example.webex.com"])
    state: str = OutputField(example_values=["active"])
    telephony: TelephonyOutput | None = OutputField()
    unlockedMeetingJoinSecurity: str = OutputField(example_values=["allowJoin"])


@app.action(
    description="Allows users to schedule a Webex meeting, webinar, or ad-hoc meeting",
    action_type="generic",
    render_as="table",
    read_only=False,
    verbose='<ul><li>To create a <strong>public meeting</strong> (<code>public_meeting=true</code>), your Webex admin must turn on this feature. If not, it will show an error.</li><li><strong>OAuth Scopes</strong>: <code>meeting:schedules_write</code>, <code>meeting:admin_schedule_write</code>. Also, make sure the user has the right access (for example, a webinar license if you\'re creating webinars). <a href=\\"https://developer.webex.com/docs/integrations#scopes\\" target=\\"_blank\\">Check required scopes</a></li><li>Use standard time zone names like <code>America/New_York</code> or <code>Asia/Kolkata</code>. This sets the correct time zone for your meeting. If you don’t set it, Webex will use the host’s time zone. <a href=\\"https://en.wikipedia.org/wiki/List_of_tz_database_time_zones\\" target=\\"_blank\\">See full list of time zones</a></li><li>If you want the meeting to repeat (daily, weekly, etc.), use the <code>recurrence</code> field. You must write it in a special format called <strong>RFC 5545</strong>.<br />Example: <code>FREQ=WEEKLY;BYDAY=MO,WE,FR</code> (means every Monday, Wednesday, and Friday)<br /><a href=\\"https://developer.webex.com/docs/api/v1/meetings/create-a-meeting\\" target=\\"_blank\\">More about recurrence rules</a></li><li>If you\'re creating an ad-hoc meeting (<code>adhoc=true</code>), you must give a <code>roomId</code> (Webex space ID).<br />In this case, <code>hostEmail</code> will be ignored — the meeting will use the Webex space owner as host.</li></ul>',  # noqa: RUF001
)
def schedule_meeting(
    params: ScheduleMeetingParams, soar: SOARClient, asset: Asset
) -> ScheduleMeetingOutput:
    if not params.title or not params.start or not params.end:
        raise ActionFailure(
            "Missing one of required parameters: 'title', 'start', 'end'."
        )

    request_data = {"title": params.title, "start": params.start, "end": params.end}
    for source, destination in consts.PARAMETER_LIST_FOR_SCHEDULE_MEETING:
        value = getattr(params, source, None)
        if value is not None:
            request_data[destination] = value

    if params.invitees:
        request_data["invitees"] = [
            {"email": email.strip()}
            for email in params.invitees.split(",")
            if email.strip()
        ]

    response = make_rest_call(
        asset,
        consts.WEBEX_SCHEDULE_MEETINGS_ENDPOINT,
        method="post",
        json_data=request_data,
    )
    soar.set_message("Meeting scheduled successfully")
    return ScheduleMeetingOutput(**remove_password_fields(response))
