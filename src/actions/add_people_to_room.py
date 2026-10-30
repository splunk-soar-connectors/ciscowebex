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
from ..helper import make_rest_call


class AddPeopleParams(Params):
    room_id: str = Param(
        description="The ID of the room to add the person to",
        primary=True,
        cef_types=["webex room id"],
    )
    person_id: str | None = Param(
        description="The ID of the person to add (use either person_id or person_email)",
        primary=True,
        cef_types=["webex user id"],
    )
    person_email: str | None = Param(
        description="The email address of the person to add (use either person_email or person_id)",
        primary=True,
        cef_types=["email"],
    )
    is_moderator: bool | None = Param(
        description="Set to true to make the person a room moderator"
    )


class AddPeopleOutput(WebexOutput):
    id: str = OutputField(
        column_name="ID",
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
    )
    personDisplayName: str = OutputField(
        column_name="Person Name", example_values=["TEST USER"]
    )
    roomId: str = OutputField(
        column_name="Room ID",
        cef_types=["webex room id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
    )
    personId: str = OutputField(
        column_name="Person ID",
        cef_types=["webex user id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
    )
    personEmail: str = OutputField(
        column_name="Email",
        cef_types=["email"],
        example_values=["example@example.com"],
    )
    personOrgId: str = OutputField(
        column_name="Person Org ID",
        cef_types=["webex org id"],
        example_values=[
            "TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST"  # pragma: allowlist secret
        ],
    )
    created: str = OutputField(example_values=["2025-05-09T09:58:50.433Z"])
    isModerator: bool | None = OutputField()
    isMonitor: bool | None = OutputField()
    isRoomHidden: bool | None = OutputField()
    roomType: str = OutputField(example_values=["group"])


@app.action(
    name="add people",
    description="Add a people to a Webex room (space) as a member or moderator",
    action_type="generic",
    read_only=False,
    render_as="table",
    verbose="Adds a person to a Webex room using their ID or email. You can optionally assign them as a moderator. Requires `spark:memberships_write` scope. Compliance officers cannot add users to empty team spaces.",
)
def add_people_to_room(
    params: AddPeopleParams, soar: SOARClient, asset: Asset
) -> AddPeopleOutput:
    if not params.person_id and not params.person_email:
        raise ActionFailure("You must provide either 'person_id' or 'person_email'.")
    request_data = {
        "roomId": params.room_id,
        "isModerator": params.is_moderator or False,
    }
    if params.person_id:
        request_data["personId"] = params.person_id
    if params.person_email:
        request_data["personEmail"] = params.person_email
    response = make_rest_call(
        asset,
        consts.WEBEX_ADD_USER_ENDPOINT,
        method="post",
        json_data=request_data,
    )
    soar.set_message("User added to the room successfully")
    return AddPeopleOutput(**response)
