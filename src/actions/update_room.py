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
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params

from .. import consts
from ..app import Asset, app
from ..output_models import WebexOutput
from ..helper import encode_path_identifier, make_rest_call


class UpdateARoomParams(Params):
    room_id: str = Param(
        description='The unique identifier for the room.  example = "Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0"',  # pragma: allowlist secret
        primary=True,
        column_name="room_id",
    )
    description: str | None = Param(
        description="The description of the space.", column_name="description"
    )
    team_id: str | None = Param(
        description="The teamId to which this space should be assigned. Only unowned spaces can be assigned to a team. Assignment between teams is unsupported.",
        default="",
        column_name="team_id",
    )
    title: str = Param(
        description="A user-friendly name for the room.", column_name="title"
    )
    is_locked: str | None = Param(
        description="Set the space as locked/moderated and the creator becomes a moderator",
        default="",
        value_list=["", "true", "false"],
        column_name="is_locked",
    )
    is_public: str | None = Param(
        description="The room is public and therefore discoverable within the org. Anyone can find and join that room. When true the description must be filled in.",
        value_list=["", "true", "false"],
        column_name="is_public",
    )
    is_read_only: str | None = Param(
        description="A compliance officer can set a direct room to read-only, which will disallow any new information exchanges in this space, while maintaining historical data.",
        value_list=["", "true", "false"],
        column_name="is_read_only",
    )
    is_announcement_only: str | None = Param(
        description="Sets the space into announcement-only mode. The room must be locked to be set to announcement-only mode.",
        value_list=["", "true", "false"],
        column_name="is_announcement_only",
    )
    classification_id: str | None = Param(
        description="The classification_id for the room",
        column_name="classification_id",
    )


class UpdateARoomOutput(WebexOutput):
    id: str | None = OutputField()
    title: str | None = OutputField()
    description: str | None = OutputField()
    teamId: str | None = OutputField()
    classificationId: str | None = OutputField()
    type: str | None = OutputField()
    created: str | None = OutputField()
    ownerId: str | None = OutputField()
    creatorId: str | None = OutputField()
    lastActivity: str | None = OutputField()
    isLocked: bool | None = OutputField()
    isPublic: bool | None = OutputField()
    isReadOnly: bool | None = OutputField()
    isAnnouncementOnly: bool | None = OutputField()
    status: str = OutputField(
        column_name="status", example_values=["success", "failed"]
    )


@app.action(
    name="update a room",
    description="Updates details for a room by ID",
    action_type="generic",
    read_only=False,
    render_as="table",
    verbose="Specify the room ID in the room_id parameter in the URI.\nA space can only be put into announcement mode when it is locked.\nAny space participant or compliance officer can convert a space from public to private. Only a compliance officer can convert a space from private to public and only if the space is classified with the lowest category (usually public), and the space has a description.\nTo remove a description please use a space character by itself.",
)
def update_room(
    params: UpdateARoomParams, soar: SOARClient, asset: Asset
) -> UpdateARoomOutput:
    if not params.room_id or not params.title:
        raise ActionFailure("Missing required parameter: room_id or title")
    room_id = encode_path_identifier(params.room_id)
    if not room_id:
        raise ActionFailure("Invalid room_id")
    request_data = {
        "title": params.title,
        "description": params.description,
        "teamId": params.team_id,
        "classificationId": params.classification_id,
        "isLocked": params.is_locked == "true" if params.is_locked else None,
        "isPublic": params.is_public == "true" if params.is_public else None,
        "isReadOnly": params.is_read_only == "true" if params.is_read_only else None,
        "isAnnouncementOnly": params.is_announcement_only == "true"
        if params.is_announcement_only
        else None,
    }
    request_data = {
        key: value
        for key, value in request_data.items()
        if value is not None and value != ""
    }
    if request_data.get("isPublic") and not request_data.get("description"):
        raise ActionFailure("When room is public 'description' must be set.")
    response = make_rest_call(
        asset,
        consts.WEBEX_UPDATE_ROOM_ENDPOINT.format(room_id=room_id),
        method="put",
        json_data=request_data,
    )
    soar.set_message(consts.WEBEX_SUCCESS_UPDATE_ROOM)
    return UpdateARoomOutput(**response, status="success")
