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


class GetUserParams(Params):
    email_address: str = Param(
        description="User webex e-mail address",
        primary=True,
        cef_types=["email"],
    )


class GetUserOutput(WebexOutput):
    status: str = OutputField(
        column_name="Status", example_values=["success", "failed"]
    )
    email_address: str | None = OutputField(column_name="Email Address")
    user_status: str | None = OutputField()
    displayName: str = OutputField(
        column_name="User Name", example_values=["Test User"]
    )
    id: str = OutputField(
        column_name="ID",
        cef_types=["webex user id"],
        example_values=[
            "L2lzY29zcAByazovL3VzL1690T1BMRS9hMzMGQ4Mi01ZWE0LTQ3OTktOWM3Zi00M2E0MTEXAMPLE"  # pragma: allowlist secret
        ],
    )
    created: str = OutputField(
        example_values=["2015-04-22T07:16:49.649Z", "2018-01-04T20:46:30.734Z"]
    )
    emails: str = OutputField(
        cef_types=["email"], example_values=["examplemail@test.com"]
    )
    firstName: str = OutputField(example_values=["abc"])
    lastActivity: str = OutputField(example_values=["2018-01-05T21:04:53.424Z"])
    lastModified: str = OutputField(example_values=["2021-08-25T11:54:51.623Z"])
    lastName: str = OutputField(example_values=["abc"])
    nickName: str = OutputField(example_values=["Test User"])
    orgId: str = OutputField(
        example_values=[
            "L2lzY29zcABCazovL3VzL09SR0FOSVpBVElPTi9jb2TEST",  # pragma: allowlist secret
        ]
    )
    type: str = OutputField(example_values=["person"])


class GetUserSummary(WebexOutput):
    found_user: bool | None = OutputField()


@app.action(
    description="Get user ID from e-mail address",
    action_type="investigate",
    read_only=True,
    render_as="table",
    summary_type=GetUserSummary,
)
def get_user(
    params: GetUserParams, soar: SOARClient, asset: Asset
) -> list[GetUserOutput]:
    response = make_rest_call(
        asset,
        consts.WEBEX_GET_USER_ENDPOINT,
        params={"email": params.email_address},
    )
    items = response.get("items", [])
    soar.set_summary(GetUserSummary(found_user=bool(items)))
    if not items:
        raise ActionFailure(consts.WEBEX_ERROR_USER_NOT_FOUND)
    soar.set_message("Found user")
    outputs = []
    for item in items:
        user = dict(item)
        user_status = user.pop("status", None)
        outputs.append(
            GetUserOutput(
                **user,
                status="success",
                email_address=params.email_address,
                user_status=user_status,
            )
        )
    return outputs
