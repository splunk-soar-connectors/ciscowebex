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
from soar_sdk.params import Params

from .. import consts
from ..app import Asset, app
from ..output_models import WebexOutput
from ..helper import make_rest_call


class ListRoomsOutput(WebexOutput):
    title: str = OutputField(
        column_name="Room Name", example_values=["Test Alert Space"]
    )
    id: str = OutputField(
        column_name="ID",
        cef_types=["webex room id"],
        example_values=[
            "L2lzY69zcGFylsdovL3VzL1JPT00vMzg2NzFhODAtZjFjMi0xMWU3LTg1OWUtNDMzYWYEXAMPLE"  # pragma: allowlist secret
        ],
    )
    created: str = OutputField(example_values=["2018-01-05T02:43:33.032Z"])
    creatorId: str = OutputField(
        cef_types=["creater id"],
        example_values=[
            "L2lzY69zcBFyazoxL3VzL1BFT1BMRS9iMmMwZjIwMS03NGQyLTRkYTEtYWM0Yi1mNzcEXAMPLE"  # pragma: allowlist secret
        ],
    )
    isLocked: bool | None = OutputField()
    lastActivity: str = OutputField(
        example_values=["2018-01-08T21:26:38.851Z", "2018-01-16T18:37:12.037Z"]
    )
    ownerId: str = OutputField(
        example_values=[
            "L2lzY29zcAByazovL3VzL09SR0FOSVpABCElPTi9hOGY3ZDhlMi04MjY1LTQ4OWEtOWE1My00NzlkZjQTESTEXAMPLE"  # pragma: allowlist secret
        ]
    )
    type: str = OutputField(example_values=["group"])
    status: str = OutputField(
        column_name="Status", example_values=["success", "failed"]
    )


class ListRoomsSummary(WebexOutput):
    total_rooms: int | None = OutputField()


@app.action(
    description="List webex rooms",
    action_type="investigate",
    read_only=True,
    render_as="table",
    summary_type=ListRoomsSummary,
)
def list_rooms(params: Params, soar: SOARClient, asset: Asset) -> list[ListRoomsOutput]:
    response = make_rest_call(asset, consts.WEBEX_ROOMS_ENDPOINT)
    items = response.get("items", [])
    if not isinstance(items, list):
        items = [items]
    soar.set_summary(ListRoomsSummary(total_rooms=len(items)))
    soar.set_message("Total rooms")
    return [ListRoomsOutput(**item, status="success") for item in items]
