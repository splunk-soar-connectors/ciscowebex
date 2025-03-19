# File: ciscowebex_consts.py
#
# Copyright (c) 2021-2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

SCOPE = "spark:people_read spark:rooms_read spark:messages_write"
BASE_URL = "https://webexapis.com"
AUTHORIZATION_URL = "/v1/authorize?client_id={client_id}&response_type={response_type}&redirect_uri={redirect_uri}&scope={scope}&state={state}"

UNKNOWN_ERROR_MESSAGE = "Unknown error occurred. Please check the asset configuration and|or action parameters"
UNKNOWN_ERROR_CODE_MESSAGE = "Error code unavailable"

OAUTH_WAIT_INTERVALS = 35
OAUTH_WAIT_TIME = 3

WEBEX_STR_CODE = "code"
WEBEX_STR_TEXT = "text/plain"
WEBEX_STR_ACCESS_TOKEN = "access_token"
WEBEX_STR_TOKEN = "token"
WEBEX_STR_REFRESH_TOKEN = "refresh_token"
WEBEX_STR_CLIENT_ID = "client_id"
WEBEX_STR_SECRET = "client_secret"  # pragma: allowlist secret
WEBEX_STR_GRANT_TYPE = "grant_type"
WEBEX_STR_REDIRECT_URI = "redirect_uri"
WEBEX_STR_IS_ENCRYPTED = "is_encrypted"
WEBEX_STR_SCOPE = "scope"

WEBEX_SUCCESS_CODE_RECEIVED_MESSAGE = "Code received. Please close this window, the action will continue to get new token"
WEBEX_SUCCESS_TEST_CONNECTIVITY = "Test Connectivity Passed"
WEBEX_SUCCESS_SEND_MESSAGE = "Message sent successfully"

WEBEX_ERROR_EMPTY_RESPONSE = "Empty response and no information in the header Status Code: {}"
WEBEX_ERROR_ASSET_NAME_NOT_FOUND = "Asset Name for id: {0} not found"
WEBEX_ERROR_PHANTOM_BASE_URL_NOT_FOUND = "Phantom Base URL not found in System Settings. Please specify this value in System Settings"
WEBEX_ERROR_TIMEOUT = "Timeout. Please try again later"
WEBEX_ERROR_TOKEN_NOT_AVAILABLE = "Token not available. Please run Test Connectivity first"
WEBEX_ERROR_TEST_CONNECTIVITY = "Test Connectivity Failed"
WEBEX_ERROR_REQUIRED_CONFIG_PARAMS = "Please provide either api_key or client_id and client secret in config for authentication"
WEBEX_ERROR_USER_NOT_FOUND = "User not found"
WEBEX_ENCRYPTION_ERROR = "Error occurred while encrypting the state file"
WEBEX_DECRYPTION_ERROR = "Error occurred while decrypting the state file"
WEBEX_INVALID_ASSET_ERROR = "In _{}_app_state: Invalid asset_id"
WEBEX_STATE_FILE_ERROR_MESSAGE = "Unable to load state file"
WEBEX_AUTHORIZATION_ERROR_MESSAGE = "Authorization code not received or not given"

PHANTOM_ASSET_ENDPOINT = "/asset/{asset_id}"
PHANTOM_SYSTEM_INFO_ENDPOINT = "/system_info"

WEBEX_ACCESS_TOKEN_ENDPOINT = "/v1/access_token"
WEBEX_GET_ROOMS_ENDPOINT = "/v1/rooms"
WEBEX_GET_USER_ENDPOINT = "/v1/people?email={0}"
WEBEX_SEND_MESSAGE_ENDPOINT = "/v1/messages"
WEBEX_DEFAULT_TIMEOUT = 30
