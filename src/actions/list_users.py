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
from ..helper import make_rest_call, validate_integer


class ListUsersParams(Params):
    email: str | None = Param(
        description="Filter people by email address", primary=True, cef_types=["email"]
    )
    display_name: str | None = Param(
        description="Filter people whose name starts with this string"
    )
    id: str | None = Param(
        description="Comma-separated list of person IDs to retrieve (max 85)",
        primary=True,
        cef_types=["webex user id"],
    )
    org_id: str | None = Param(
        description="List users in this organization (admin only)"
    )
    roles: str | None = Param(
        description="Comma-separated list of role IDs to filter by (admin only)"
    )
    calling_data: bool | None = Param(
        description="Whether to include Webex Calling data (admin only)", default=False
    )
    location_id: str | None = Param(
        description="List users present in this location (admin only)"
    )
    limit: float = Param(
        description="Maximum number of people to return (default 100, max varies based on flags)",
        required=False,
        default=100,
    )


class AddressesOutput(WebexOutput):
    country: str = OutputField(example_values=["US"])
    locality: str = OutputField(example_values=["SAN JOSE"])
    postalCode: str = OutputField(example_values=["95128"])
    region: str = OutputField(example_values=["CALIFORNIA"])
    streetAddress: str = OutputField(example_values=["3098 Test Drive"])
    type: str = OutputField(example_values=["work"])


class PhonenumbersOutput(WebexOutput):
    primary: bool | None = OutputField()
    type: str = OutputField(example_values=["work"])
    value: str = OutputField(example_values=["+1 000-895-000"])


class PronounsOutput(WebexOutput):
    value: str = OutputField(example_values=["He/Him/His"])
    visibility: str = OutputField(example_values=["Internal"])


class SipaddressesOutput(WebexOutput):
    primary: bool | None = OutputField()
    type: str = OutputField(example_values=["personal-room"])
    value: str = OutputField(example_values=["4229032891@sademo2ci.dmz.webex.com"])


class ListUsersOutput(WebexOutput):
    id: str = OutputField(cef_types=["webex user id"], column_name="User ID")
    emails: list[str] = OutputField(cef_types=["email"], column_name="Emails")
    displayName: str | None = OutputField(column_name="Display Name")
    addresses: list[AddressesOutput] | None = OutputField()
    avatar: str = OutputField(
        example_values=[
            "https://test-prod-us-east-2.webexcontent.com/Avtr~V1~1ebtest43-417f-9974-ad72catest/V1~test8f27546e523b2945ea2f7ff36tst141b3544e232718885c17cad0d1~test0570bbc40b193112b2c957test~1600"
        ]
    )
    created: str = OutputField(example_values=["2024-11-08T10:16:05.408Z"])
    department: str = OutputField(example_values=["020122475"])
    extension: str = OutputField(example_values=["3432432"])
    firstName: str = OutputField(example_values=["User"])
    invitePending: bool | None = OutputField()
    lastActivity: str = OutputField(example_values=["2025-05-22T08:00:26.197Z"])
    lastModified: str = OutputField(example_values=["2025-04-15T01:50:15.733Z"])
    lastName: str = OutputField(example_values=["Test"])
    locationId: str = OutputField(
        example_values=[
            "Y2lzY29zcGFyazovL3VzL0xPQ0FUSU9OL2YzYjJkYmI3LWQ3MTQtNGM5YS05OTkyLWVmMjA0NWNkMmQwZA"  # pragma: allowlist secret
        ]
    )
    loginEnabled: bool | None = OutputField()
    manager: str = OutputField(example_values=["Test User"])
    managerId: str = OutputField(
        example_values=[
            "test29zcGFyazovL3VzL1BFT1BMRS8wMDI3MjIrtestTJjLTQzM2QtODA5Yy05YWJmNWZiNDtest"  # pragma: allowlist secret
        ]
    )
    nickName: str = OutputField(example_values=["User"])
    orgId: str = OutputField(cef_types=["webex org id"])
    phoneNumbers: list[PhonenumbersOutput] | None = OutputField()
    pronouns: PronounsOutput | None = OutputField()
    roles: list[str] | None = OutputField()
    sipAddresses: list[SipaddressesOutput] | None = OutputField()
    status: str | None = OutputField()
    timeZone: str = OutputField(example_values=["Asia/Shanghai"])
    title: str = OutputField(example_values=["Software Engineer [C]"])
    type: str = OutputField(example_values=["person"])
    userName: str = OutputField(example_values=["example@example.com"])


class ListUsersSummary(WebexOutput):
    message: str | None = OutputField()
    total_people: int | None = OutputField()


@app.action(
    description="List users in your Webex organization using filters like email, name, ID, roles, or location",
    render_as="table",
    summary_type=ListUsersSummary,
    action_type="investigate",
    read_only=True,
)
def list_users(
    params: ListUsersParams, soar: SOARClient, asset: Asset
) -> list[ListUsersOutput]:
    limit = validate_integer(params.limit, "limit")
    query_params = {}
    for api_name, param_name in consts.PARAMETER_LIST_FOR_LIST_USERS.items():
        value = getattr(params, param_name, None)
        if value:
            query_params[api_name] = value
    if params.calling_data:
        query_params["callingData"] = "true"
    if limit:
        query_params["max"] = limit

    response = make_rest_call(
        asset, consts.WEBEX_LIST_USERS_ENDPOINT, params=query_params
    )
    people = response.get("items", [])
    if not isinstance(people, list):
        people = [people]
    soar.set_summary(
        ListUsersSummary(
            message="Users retrieved successfully", total_people=len(people)
        )
    )
    return [ListUsersOutput(**person) for person in people]
