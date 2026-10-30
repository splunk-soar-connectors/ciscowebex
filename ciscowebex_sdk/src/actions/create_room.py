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

from .. import consts
from ..app import Asset, app
from ..output_models import WebexOutput
from ..helper import make_rest_call


class CreateARoomParams(Params):
    title: str = Param(description="A user-friendly name for the room")
    description: str | None = Param(description="The description of the space")
    team_id: str | None = Param(
        description="The ID for the team with which this room is associated"
    )
    classification_id: str | None = Param(
        description="The classification_id for the room"
    )
    is_locked: bool | None = Param(
        description="Set the space as locked/moderated; creator becomes a moderator"
    )
    is_public: bool | None = Param(
        description="If true, the room is discoverable by anyone in the org; description must be provided"
    )
    is_announcement_only: bool | None = Param(
        description="Sets the space into announcement-only mode"
    )


class CreateARoomOutput(WebexOutput):
    id: str = OutputField(
        column_name="ID",
        cef_types=["webex room id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
    )
    title: str = OutputField(column_name="Title", example_values=["test room"])
    ownerId: str = OutputField(
        column_name="Owner ID",
        cef_types=["webex user id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
    )
    isLocked: bool = OutputField(column_name="Is Locked")
    isPublic: bool = OutputField(column_name="Is Public")
    created: str = OutputField(
        column_name="Created At", example_values=["2025-05-09T09:57:17.803Z"]
    )
    creatorId: str = OutputField(
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ]
    )
    description: str = OutputField(example_values=["test"])
    isAnnouncementOnly: bool | None = OutputField()
    lastActivity: str = OutputField(example_values=["2025-05-09T09:57:17.803Z"])
    madePublic: str = OutputField(example_values=["2025-05-23T04:53:54.268Z"])
    teamId: str = OutputField(
        example_values=[
            "testzcGFyazovL3VzL1RFQU0vMDM3ZWZlZTAtMtestzc5My0xMWYwLWFhY2EtODM2Mjg3test"  # pragma: allowlist secret
        ]
    )
    type: str = OutputField(example_values=["group"])


@app.action(
    name="create a room",
    description="Create a new Webex room (space)",
    action_type="generic",
    read_only=False,
    render_as="table",
    verbose="<ul><li>Public rooms require a description.</li><li>Announcement mode requires the room to be locked.</li><li>Team rooms cannot be locked.</li><li>Requires permission: <code>spark:rooms_write</code>.</li></ul>",
)
def create_room(
    params: CreateARoomParams, soar: SOARClient, asset: Asset
) -> CreateARoomOutput:
    request_data = {
        "title": params.title,
        "teamId": params.team_id,
        "classificationId": params.classification_id,
        "isLocked": params.is_locked,
        "isPublic": params.is_public,
        "description": params.description,
        "isAnnouncementOnly": params.is_announcement_only,
    }
    request_data = {
        key: value for key, value in request_data.items() if value or key == "title"
    }
    response = make_rest_call(
        asset,
        consts.WEBEX_ROOMS_ENDPOINT,
        method="post",
        json_data=request_data,
    )
    soar.set_message("Room created successfully")
    return CreateARoomOutput(**response)
