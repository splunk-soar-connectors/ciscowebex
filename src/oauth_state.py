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
from typing import TYPE_CHECKING

from soar_sdk.auth.models import OAuthState
from soar_sdk.exceptions import ActionFailure
from soar_sdk.shims.phantom.encryption_helper import encryption_helper

if TYPE_CHECKING:
    from .app import Asset


def migrate_legacy_oauth_state(asset: "Asset") -> None:
    """Seed SDK auth state once from the legacy connector's token dictionary."""
    auth_state = asset.auth_state
    current_state = auth_state.get_all()
    # Preserve SDK tokens, pending authorization, and deliberately cleared tokens.
    # Re-importing legacy state after SDK authorization changes could revive old credentials.
    if "oauth" in current_state:
        return
    if not asset.client_id or not asset.client_secret:
        return

    legacy_state = auth_state.backend.load_state() or {}
    if not isinstance(legacy_state, dict):
        raise ActionFailure("Invalid legacy OAuth state. Please run Test Connectivity.")
    legacy_token = legacy_state.get("token")
    if legacy_token is None:
        return
    if not isinstance(legacy_token, dict):
        raise ActionFailure("Invalid legacy OAuth token. Please run Test Connectivity.")

    access_token = legacy_token.get("access_token")
    refresh_token = legacy_token.get("refresh_token")
    if any(
        value is not None and not isinstance(value, str)
        for value in (access_token, refresh_token)
    ):
        raise ActionFailure("Invalid legacy OAuth token. Please run Test Connectivity.")
    if not access_token and not refresh_token:
        return

    if legacy_state.get("is_encrypted"):
        try:
            if access_token:
                access_token = encryption_helper.decrypt(
                    access_token, auth_state.asset_id
                )
            if refresh_token:
                refresh_token = encryption_helper.decrypt(
                    refresh_token, auth_state.asset_id
                )
        except Exception:
            # Platform encryption helpers can raise different exception types. Do not
            # include their messages or ciphertext in action results or logs.
            raise ActionFailure(
                "Unable to decrypt legacy OAuth tokens. Please run Test Connectivity."
            ) from None

    token: dict[str, str | int] = {
        "access_token": access_token or "",
        "token_type": legacy_token.get("token_type") or "Bearer",
    }
    if refresh_token:
        token["refresh_token"] = refresh_token
        # Legacy expires_in is a duration without an issuance time. Never restart
        # its lifetime during upgrade: obtain a fresh token before the first request.
        token["expires_at"] = 0
    if legacy_token.get("scope"):
        token["scope"] = legacy_token["scope"]

    try:
        oauth = OAuthState.model_validate(
            {"token": token, "client_id": asset.client_id}
        )
    except ValueError:
        raise ActionFailure(
            "Invalid legacy OAuth token. Please run Test Connectivity."
        ) from None

    migrated_state = dict(current_state)
    migrated_state["oauth"] = oauth.model_dump(mode="json", exclude_none=True)
    auth_state.put_all(migrated_state)
