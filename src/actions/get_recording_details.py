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
from .custom_views import recording_details_view


class GetRecordingDetailsParams(Params):
    recording_id: str | None = Param(
        description="Unique identifier of the Webex recording.",
        cef_types=["webex recording id"],
    )
    meeting_id: str | None = Param(
        description="Unique identifier of the Webex meeting.",
        cef_types=["webex meeting id"],
    )
    host_email: str | None = Param(
        description="Email address of the meeting host (admin only).",
        cef_types=["email"],
    )


class TemporarydirectdownloadlinksOutput(WebexOutput):
    audioDownloadLink: str = OutputField(
        example_values=[
            "https://company.dmz.webex.com/nbr/MultiThreadDownloadServlet/audio.mp3?siteid=00240&recordid=197000062&"
        ]
    )
    expiration: str = OutputField(example_values=["2025-05-22T13:44:50Z"])
    recordingDownloadLink: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://company.dmz.webex.com/nbr/MultiThreadDownloadServlet?siteid=00240&recordid=197000062"
        ],
        column_name="Recording Download Link",
    )
    transcriptDownloadLink: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://company.dmz.webex.com/nbr/MultiThreadDownloadServlet/transcript.txt?siteid=00240&recordid=197000062&confid=6547000000000001771&from=MBS"
        ],
        column_name="Transcript Download Link",
    )


class GetRecordingDetailsOutput(WebexOutput):
    createTime: str = OutputField(example_values=["2025-05-22T08:31:19Z"])
    downloadUrl: str = OutputField(
        example_values=[
            "https://company.webex.com/siteurl/lsr.php?RCID=1a417c966testaef288e9043adatest"
        ]
    )
    durationSeconds: float = OutputField(example_values=[219])
    format: str = OutputField(example_values=["MP4"])
    hostEmail: str = OutputField(example_values=["example@example.com"])
    id: str = OutputField(
        cef_types=["webex recording id"],
        example_values=["test06506faa48c790592a4198c3test"],
        column_name="Recording ID",
    )
    meetingId: str = OutputField(
        example_values=["test5560719471599d7test2a4c1b72_I_6547053376test"]
    )
    meetingSeriesId: str = OutputField(example_values=["test5560719471599d76418test"])
    playbackUrl: str = OutputField(
        cef_types=["url"],
        example_values=[
            "https://company.webex.com/siteurl/ldr.php?RCID=testcc66c2ee8536aabdd0ec607test"
        ],
        column_name="Playback URL",
    )
    scheduledMeetingId: str = OutputField(
        example_values=["test60719471599d764182a4c1b7test250522T150000Z"]
    )
    serviceType: str = OutputField(example_values=["MeetingCenter"])
    shareToMe: bool = OutputField(example_values=[False])
    siteUrl: str = OutputField(example_values=["company.webex.com"])
    sizeBytes: float = OutputField(example_values=[1067115])
    status: str = OutputField(example_values=["available"])
    temporaryDirectDownloadLinks: TemporarydirectdownloadlinksOutput | None = (
        OutputField()
    )
    timeRecorded: str = OutputField(example_values=["2025-05-22T08:23:05Z"])
    topic: str = OutputField(example_values=["soar test-20250522 0829-1"])


@app.action(
    description="Retrieve details of a Webex meeting recording using its recording ID",
    action_type="investigate",
    read_only=True,
    view_handler=recording_details_view,
)
def get_recording_details(
    params: GetRecordingDetailsParams, soar: SOARClient, asset: Asset
) -> list[GetRecordingDetailsOutput]:
    recording_id = params.recording_id
    meeting_id = params.meeting_id
    if not recording_id and not meeting_id:
        raise ActionFailure(
            "Missing required parameter. please provide either 'recording_id' or 'meeting_id'"
        )

    query_params = {"hostEmail": params.host_email} if params.host_email else {}
    if recording_id:
        encoded_id = encode_path_identifier(recording_id)
        if not encoded_id:
            raise ActionFailure("Invalid recording_id")
        response = make_rest_call(
            asset,
            consts.WEBEX_RECORDING_DETAILS_BY_RECORDING_ID_ENDPOINT.format(
                recording_id=encoded_id
            ),
            params=query_params,
        )
        items = [response]
    else:
        response = make_rest_call(
            asset,
            consts.WEBEX_RECORDING_DETAILS_BY_MEETING_ID_ENDPOINT,
            params={**query_params, "meetingId": meeting_id},
        )
        recordings = response.get("items", [])
        if not isinstance(recordings, list):
            recordings = [recordings]
        if not recordings:
            raise ActionFailure(
                f"Recording details not found for meeting id: {meeting_id}"
            )
        items = []
        for item in recordings:
            encoded_id = encode_path_identifier(item.get("id"))
            if not encoded_id:
                raise ActionFailure("Invalid recording_id returned by Webex")
            details = make_rest_call(
                asset,
                consts.WEBEX_RECORDING_DETAILS_BY_RECORDING_ID_ENDPOINT.format(
                    recording_id=encoded_id
                ),
                params=query_params,
            )
            items.append(details)

    soar.set_message("Recording details retrieved successfully")
    return [GetRecordingDetailsOutput(**remove_password_fields(item)) for item in items]
