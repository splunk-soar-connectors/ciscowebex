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
from soar_sdk.app import App
from soar_sdk.asset import AssetField, BaseAsset, FieldCategory
from soar_sdk.auth import (
    OAuthConfig,
    SOARAssetOAuthClient,
    create_oauth_callback_handler,
)
from soar_sdk.logging import getLogger
from soar_sdk.webhooks.models import WebhookRequest, WebhookResponse

from . import consts
from .helper import make_rest_call, oauth_flow

logger = getLogger()


class Asset(BaseAsset):
    authorization_key: str | None = AssetField(
        description="Personal Access Token",
        sensitive=True,
        category=FieldCategory.CONNECTIVITY,
    )
    client_id: str | None = AssetField(
        description="Client ID", category=FieldCategory.CONNECTIVITY
    )
    client_secret: str | None = AssetField(
        description="Client Secret", sensitive=True, category=FieldCategory.CONNECTIVITY
    )
    scope: str | None = AssetField(
        description="Scopes (Append extra space-seperated scopes which are added during app creation from webex portal)",
        default="spark:people_read spark:rooms_read spark:messages_write spark:rooms_write spark:memberships_write spark:messages_read meeting:participants_read meeting:schedules_read meeting:recordings_read meeting:schedules_write",
        category=FieldCategory.CONNECTIVITY,
    )
    verify_server_cert: bool | None = AssetField(
        description="Verify the Webex server certificate",
        default=True,
        category=FieldCategory.CONNECTIVITY,
    )


app = App(
    name="Cisco Webex",
    app_type="information",
    logo="logo_ciscowebex.svg",
    logo_dark="logo_ciscowebex_dark.svg",
    product_vendor="Cisco",
    product_name="Cisco Webex",
    publisher="Splunk",
    appid="34624d1a-f0ae-47d6-a731-8499d5617cf7",
    fips_compliant=True,
    encrypt_cache_state=True,
    encrypt_ingest_state=True,
    asset_cls=Asset,
).enable_webhooks(default_requires_auth=False)


def _get_oauth_client(asset: Asset) -> SOARAssetOAuthClient:
    config = OAuthConfig(
        client_id=asset.client_id,
        client_secret=asset.client_secret,
        token_endpoint=f"{consts.BASE_URL}{consts.WEBEX_ACCESS_TOKEN_ENDPOINT}",
    )
    return SOARAssetOAuthClient(config, asset.auth_state)


@app.webhook("oauth_callback")
def oauth_callback(request: WebhookRequest[Asset]) -> WebhookResponse:
    return create_oauth_callback_handler(
        _get_oauth_client,
        success_message=consts.WEBEX_SUCCESS_CODE_RECEIVED_MESSAGE,
    )(request)


@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    if not asset.authorization_key:
        flow = oauth_flow(
            asset, soar.get_asset_id(), app.get_webhook_url("oauth_callback")
        )
        authorization_url = flow.get_authorization_url()
        logger.progress("Please authorize user in a separate tab using URL")
        logger.progress(authorization_url)
        flow.wait_for_authorization(on_progress=lambda _: logger.progress("Waiting..."))
    make_rest_call(asset, consts.WEBEX_ROOMS_ENDPOINT)
    logger.progress(consts.WEBEX_SUCCESS_TEST_CONNECTIVITY)


from . import actions  # noqa: F401


if __name__ == "__main__":
    app.cli()
