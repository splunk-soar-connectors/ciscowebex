# File: ciscowebex_connector.py
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
#
#
import json
import os
import pathlib
import time
import urllib.parse as urllib

import phantom.app as phantom
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from encryption_helper import decrypt, encrypt
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

import ciscowebex_consts as consts


class RetVal(tuple):
    def __new__(cls, val1, val2):
        return tuple.__new__(RetVal, (val1, val2))


def _get_error_message_from_exception(e, app_connector=None):
    """This function is used to get appropriate error message from the exception.
    :param e: Exception object
    :return: error code and message
    """
    error_message = consts.UNKNOWN_ERROR_MESSAGE
    error_code = consts.UNKNOWN_ERROR_CODE_MESSAGE
    if app_connector:
        app_connector.error_print("Exception occurred.", dump_object=e)
    try:
        if e.args:
            if len(e.args) > 1:
                error_code = e.args[0]
                error_message = e.args[1]
            elif len(e.args) == 1:
                error_code = consts.UNKNOWN_ERROR_CODE_MESSAGE
                error_message = e.args[0]
        else:
            error_code = consts.UNKNOWN_ERROR_CODE_MESSAGE
            error_message = consts.UNKNOWN_ERROR_MESSAGE
    except:
        error_code = consts.UNKNOWN_ERROR_CODE_MESSAGE
        error_message = consts.UNKNOWN_ERROR_MESSAGE

    return error_code, error_message


def _handle_rest_request(request, path_parts):
    """Handle requests for authorization.

    :param request: Data given to REST endpoint
    :param path_parts: Parts of the URL passed
    :return: Dictionary containing response parameters
    """

    if len(path_parts) < 2:
        return HttpResponse("error: True, message: Invalid REST endpoint request", content_type=consts.WEBEX_STR_TEXT, status=404)  # nosemgrep

    call_type = path_parts[1]

    # To handle authorize request in test connectivity action
    if call_type == "start_oauth":
        return _handle_login_redirect(request, "authorization_url")

    # To handle response from Webex login page
    if call_type == "result":
        return_val = _handle_login_response(request)
        asset_id = request.GET.get("state")  # nosemgrep
        if asset_id and asset_id.isalnum():
            app_dir = pathlib.Path(__file__).resolve()
            auth_status_file_path = app_dir.with_name("{}_{}".format(asset_id, "oauth_task.out"))
            real_auth_status_file_path = os.path.abspath(auth_status_file_path)
            if not os.path.dirname(real_auth_status_file_path) == str(auth_status_file_path.parent):
                return HttpResponse("Error: Invalid asset_id", content_type=consts.WEBEX_STR_TEXT, status=400)  # nosemgrep
            open(auth_status_file_path, "w").close()

        return return_val
    return HttpResponse("error: Invalid endpoint", content_type=consts.WEBEX_STR_TEXT, status=404)  # nosemgrep


def _handle_login_response(request):
    """This function is used to get the login response of authorization request from Webex login page.

    :param request: Data given to REST endpoint
    :return: HttpResponse. The response displayed on authorization URL page
    """

    asset_id = request.GET.get("state")
    if not asset_id:
        return HttpResponse(  # nosemgrep
            f"ERROR: Asset ID not found in URL\n{json.dumps(request.GET)}", content_type=consts.WEBEX_STR_TEXT, status=400
        )

    # Check for error in URL
    error = request.GET.get("error")
    error_description = request.GET.get("error_description")

    # If there is an error in response
    if error:
        message = f"Error: {error}"
        if error_description:
            message = f"{message} Details: {error_description}"
        return HttpResponse(f"Server returned {message}", content_type=consts.WEBEX_STR_TEXT, status=400)  # nosemgrep

    code = request.GET.get(consts.WEBEX_STR_CODE)

    # If code is not available
    if not code:
        return HttpResponse(  # nosemgrep
            f"Error while authenticating\n{json.dumps(request.GET)}", content_type=consts.WEBEX_STR_TEXT, status=400
        )

    state = _load_app_state(asset_id)
    state[consts.WEBEX_STR_CODE] = code
    _save_app_state(state, asset_id, None)

    return HttpResponse(consts.WEBEX_SUCCESS_CODE_RECEIVED_MESSAGE, content_type=consts.WEBEX_STR_TEXT)  # nosemgrep


def _handle_login_redirect(request, key):
    """This function is used to redirect login request to Cisco webex login page.

    :param request: Data given to REST endpoint
    :param key: Key to search in state file
    :return: response authorization_url/admin_consent_url
    """

    asset_id = request.GET.get("asset_id")
    if not asset_id:
        return HttpResponse("ERROR: Asset ID not found in URL", content_type=consts.WEBEX_STR_TEXT, status=400)  # nosemgrep
    state = _load_app_state(asset_id)
    if not state:
        return HttpResponse("ERROR: Invalid asset_id", content_type=consts.WEBEX_STR_TEXT, status=400)  # nosemgrep
    url = state.get(key)
    if not url:
        return HttpResponse(
            f"App state is invalid, {key} not found.",  # nosemgrep
            content_type=consts.WEBEX_STR_TEXT,
            status=400,
        )  # nosemgrep
    response = HttpResponse(status=302)
    response["Location"] = url
    return response


def _load_app_state(asset_id, app_connector=None):
    """This function is used to load the current state file.

    :param asset_id: asset_id
    :param app_connector: Object of app_connector class
    :return: state: Current state file as a dictionary
    """

    asset_id = str(asset_id)
    if not asset_id or not asset_id.isalnum():
        if app_connector:
            app_connector.debug_print(consts.WEBEX_INVALID_ASSET_ERROR.format("load"))
        return {}

    app_dir = pathlib.Path(__file__).resolve()
    state_file = app_dir.with_name(f"{asset_id}_state.json")
    real_state_file_path = os.path.abspath(state_file)
    if not os.path.dirname(real_state_file_path) == str(state_file.parent):
        if app_connector:
            app_connector.debug_print(consts.WEBEX_INVALID_ASSET_ERROR.format("load"))
        return {}

    state = {}
    try:
        with open(real_state_file_path) as state_file_obj:
            state = json.load(state_file_obj)
    except Exception as e:
        if app_connector:
            error_code, error_message = _get_error_message_from_exception(e)
            app_connector.debug_print(f"In _load_app_state: Error Code: {error_code}. Error Message: {error_message}")

    if app_connector:
        app_connector.debug_print("Loaded state: ", state)

    try:
        if consts.WEBEX_STR_CODE in state:
            state[consts.WEBEX_STR_CODE] = decrypt(state[consts.WEBEX_STR_CODE], asset_id)
    except Exception as ex:
        _, error_message = _get_error_message_from_exception(ex)
        if app_connector:
            app_connector.debug_print(f"{consts.WEBEX_DECRYPTION_ERROR}: {error_message}")

    return state


def _save_app_state(state, asset_id, app_connector=None):
    """This function is used to save current state in file.

    :param state: Dictionary which contains data to write in state file
    :param asset_id: asset_id
    :param app_connector: Object of app_connector class
    :return: status: phantom.APP_SUCCESS|phantom.APP_ERROR
    """

    asset_id = str(asset_id)
    if not asset_id or not asset_id.isalnum():
        if app_connector:
            app_connector.debug_print(consts.WEBEX_INVALID_ASSET_ERROR.format("save"))
        return {}

    app_dir = pathlib.Path(__file__).resolve()
    state_file = app_dir.with_name(f"{asset_id}_state.json")

    real_state_file_path = os.path.abspath(state_file)
    if not os.path.dirname(real_state_file_path) == str(state_file.parent):
        if app_connector:
            app_connector.debug_print(consts.WEBEX_INVALID_ASSET_ERROR.format("save"))
        return {}

    try:
        if consts.WEBEX_STR_CODE in state:
            state[consts.WEBEX_STR_CODE] = encrypt(state[consts.WEBEX_STR_CODE], asset_id)
    except Exception as ex:
        _, error_message = _get_error_message_from_exception(ex)
        if app_connector:
            app_connector.debug_print(f"{consts.WEBEX_ENCRYPTION_ERROR}: {error_message}")

    if app_connector:
        app_connector.debug_print("Saving state: ", state)

    try:
        with open(real_state_file_path, "w+") as state_file_obj:
            state_file_obj.write(json.dumps(state))
    except Exception as e:
        error_code, error_message = _get_error_message_from_exception(e)
        if app_connector:
            app_connector.debug_print(f"Unable to save state file: Error Code: {error_code}. Error Message: {error_message}")
        return phantom.APP_ERROR

    return phantom.APP_SUCCESS


def _get_dir_name_from_app_name(app_name):
    """Get name of the directory for the app.

    :param app_name: Name of the application for which directory name is required
    :return: app_name: Name of the directory for the application
    """

    app_name = "".join([x for x in app_name if x.isalnum()])
    app_name = app_name.lower()
    if not app_name:
        app_name = "app_for_phantom"
    return app_name


class CiscoWebexConnector(BaseConnector):
    def __init__(self):
        # Call the BaseConnectors init first
        super().__init__()

        self._asset_id = None
        self._api_key = None
        self._state = None
        self._client_id = None
        self._client_secret = None
        self._access_token = None
        self._refresh_token = None
        self._scopes = None

        # Variable to hold a base_url in case the app makes REST calls
        # Do note that the app json defines the asset config, so please
        # modify this as you deem fit.
        self._base_url = None

    def load_state(self):
        """
        Load the contents of the state file to the state dictionary and decrypt it.
        :return: loaded state
        """
        state = super().load_state()
        if not isinstance(state, dict):
            self.debug_print("Resetting the state file with the default format")
            state = {"app_version": self.get_app_json().get("app_version")}
            return state
        return self.decrypt_state(state)

    def save_state(self, state):
        """
        Encrypt and save the current state dictionary to the state file.
        :param state: state dictionary
        :return: status
        """
        return super().save_state(self.encrypt_state(state))

    @staticmethod
    def _process_empty_response(response, action_result):
        if response.status_code in [200, 204]:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(action_result.set_status(phantom.APP_ERROR, consts.WEBEX_ERROR_EMPTY_RESPONSE.format(response.status_code)), None)

    @staticmethod
    def _process_html_response(response, action_result):
        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove the script, style, footer and navigation part from the HTML message
            for element in soup(["script", "style", "footer", "nav"]):
                element.extract()
            error_text = soup.text
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except:
            error_text = "Cannot parse error details"

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"

        message = message.replace("{", "{{").replace("}", "}}")

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    @staticmethod
    def _process_json_response(r, action_result):
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Unable to parse JSON response. Error: {e!s}"), None)

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        message = "Error from server. Status Code: {} Data from server: {}".format(r.status_code, r.text.replace("{", "{{").replace("}", "}}"))

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if r.status_code == 401:
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Access token is expired or invalid"), None)

        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if "json" in r.headers.get("Content-Type", ""):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if "html" in r.headers.get("Content-Type", ""):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            r.status_code, r.text.replace("{", "{{").replace("}", "}}")
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _make_rest_call(self, endpoint, action_result, headers=None, params=None, data=None, method="get", verify=False):
        resp_json = None

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Invalid method: {method}"), resp_json)

        try:
            r = request_func(endpoint, json=data, headers=headers, verify=verify, params=params)
        except Exception as e:
            _, error_message = _get_error_message_from_exception(e, self)
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Error Connecting to server. Details: {error_message}"), resp_json)

        return self._process_response(r, action_result)

    def _get_asset_name(self, action_result):
        """Get name of the asset using Phantom URL.

        :param action_result: object of ActionResult class
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message), asset name
        """

        asset_id = self.get_asset_id()
        rest_endpoint = consts.PHANTOM_ASSET_ENDPOINT.format(asset_id=asset_id)
        url = "{}{}".format(self.get_phantom_base_url() + "rest", rest_endpoint)
        ret_val, resp_json = self._make_rest_call(action_result=action_result, endpoint=url)

        if phantom.is_fail(ret_val):
            return ret_val, None

        asset_name = resp_json.get("name")
        if not asset_name:
            return action_result.set_status(phantom.APP_ERROR, consts.WEBEX_ERROR_ASSET_NAME_NOT_FOUND.format(asset_id), None)

        return phantom.APP_SUCCESS, asset_name

    def _get_phantom_base_url(self, action_result):
        """Get base url of phantom.

        :param action_result: object of ActionResult class
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        base url of phantom
        """

        url = "{}{}{}".format(BaseConnector._get_phantom_base_url(), "rest", consts.PHANTOM_SYSTEM_INFO_ENDPOINT)
        ret_val, resp_json = self._make_rest_call(action_result=action_result, endpoint=url, verify=False)
        if phantom.is_fail(ret_val):
            return ret_val, None

        phantom_base_url = resp_json.get("base_url")
        if not phantom_base_url:
            return action_result.set_status(phantom.APP_ERROR, consts.WEBEX_ERROR_PHANTOM_BASE_URL_NOT_FOUND), None

        return phantom.APP_SUCCESS, phantom_base_url.rstrip("/")

    def _get_app_rest_url(self, action_result):
        """Get URL for making rest calls.

        :param action_result: object of ActionResult class
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        URL to make rest calls
        """

        ret_val, phantom_base_url = self._get_phantom_base_url(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status(), None

        ret_val, asset_name = self._get_asset_name(action_result)
        if phantom.is_fail(ret_val):
            return action_result.get_status(), None

        self.save_progress(f"Using Phantom base URL as: {phantom_base_url}")
        app_json = self.get_app_json()
        app_name = app_json["name"]

        app_dir_name = _get_dir_name_from_app_name(app_name)
        url_to_app_rest = "{}/rest/handler/{}_{}/{}".format(phantom_base_url, app_dir_name, app_json["appid"], asset_name)
        return phantom.APP_SUCCESS, url_to_app_rest

    def _generate_new_access_token(self, action_result, data):
        """This function is used to generate new access token using the code obtained on authorization.
        :param action_result: object of ActionResult class
        :param data: Data to send in REST call
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS
        """

        req_url = f"{self._base_url}{consts.WEBEX_ACCESS_TOKEN_ENDPOINT}"
        ret_val, resp_json = self._make_rest_call(action_result=action_result, endpoint=req_url, data=data, method="post")
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        # If there is any error while generating access_token, API returns 200 with error and error_description fields
        if not resp_json.get(consts.WEBEX_STR_ACCESS_TOKEN):
            if resp_json.get("message"):
                return action_result.set_status(phantom.APP_ERROR, status_message=resp_json["message"])

            return action_result.set_status(phantom.APP_ERROR, status_message="Error while generating access_token")

        self._state[consts.WEBEX_STR_TOKEN] = resp_json
        self._access_token = resp_json[consts.WEBEX_STR_ACCESS_TOKEN]
        self._refresh_token = resp_json[consts.WEBEX_STR_REFRESH_TOKEN]
        self.save_state(self._state)

        return phantom.APP_SUCCESS

    def _wait(self, action_result):
        """This function is used to hold the action till user login.

        :param action_result: Object of ActionResult class
        :return: status (success/failed)
        """

        app_dir = pathlib.Path(__file__).resolve()
        # file to check whether the request has been granted or not
        auth_status_file_path = app_dir.with_name("{}_{}".format(self._asset_id, "oauth_task.out"))
        time_out = False

        # wait-time while request is being granted
        for _ in range(consts.OAUTH_WAIT_INTERVALS):
            self.send_progress("Waiting...")
            if os.path.isfile(auth_status_file_path):
                time_out = True
                os.unlink(auth_status_file_path)
                break
            time.sleep(consts.OAUTH_WAIT_TIME)

        if not time_out:
            return action_result.set_status(phantom.APP_ERROR, status_message=consts.WEBEX_ERROR_TIMEOUT)
        self.send_progress("Authenticated")
        return phantom.APP_SUCCESS

    def _update_request(self, action_result, endpoint, headers=None, params=None, data=None, method="get"):
        """This function is used to update the headers with access_token before making REST call.

        :param endpoint: REST endpoint that needs to appended to the service address
        :param action_result: object of ActionResult class
        :param headers: request headers
        :param params: request parameters
        :param data: request body
        :param method: GET/POST/PUT/DELETE/PATCH (Default will be GET)
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        response obtained by making an API call
        """

        if not endpoint.startswith(self._base_url):
            endpoint = f"{self._base_url}{endpoint}"

        if headers is None:
            headers = {}

        token_data = {
            consts.WEBEX_STR_CLIENT_ID: self._client_id,
            consts.WEBEX_STR_SECRET: self._client_secret,
            consts.WEBEX_STR_GRANT_TYPE: consts.WEBEX_STR_REFRESH_TOKEN,
            consts.WEBEX_STR_REFRESH_TOKEN: self._refresh_token,
        }

        if not self._access_token:
            if not self._refresh_token:
                # If none of the access_token and refresh_token is available
                return action_result.set_status(phantom.APP_ERROR, status_message=consts.WEBEX_ERROR_TOKEN_NOT_AVAILABLE), None

            self.debug_print("Access token is not available, generating new token using refresh token")
            # If refresh_token is available and access_token is not available, generate new access_token
            status = self._generate_new_access_token(action_result=action_result, data=token_data)

            if phantom.is_fail(status):
                return action_result.get_status(), None

        headers.update({"Authorization": f"Bearer {self._access_token}"})
        if not headers.get("Content-Type"):
            headers.update({"Content-Type": "application/json"})

        ret_val, resp_json = self._make_rest_call(
            action_result=action_result, endpoint=endpoint, headers=headers, params=params, data=data, method=method
        )

        # If token is expired, generate new token
        if "Access token is expired or invalid" in action_result.get_message():
            self.debug_print("Token is invalid, generating new token")
            status = self._generate_new_access_token(action_result=action_result, data=token_data)

            if phantom.is_fail(status):
                return action_result.get_status(), None

            headers.update({"Authorization": f"Bearer {self._access_token}"})
            ret_val, resp_json = self._make_rest_call(
                action_result=action_result, endpoint=endpoint, headers=headers, params=params, data=data, method=method
            )
        if phantom.is_fail(ret_val):
            return action_result.get_status(), None

        return phantom.APP_SUCCESS, resp_json

    def _handle_test_connectivity(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))

        app_state = {}

        # If API key exists, skipping oAuth authentication
        if self._api_key:
            self.save_progress("Validating API Key")
            ret_val, response = self._make_rest_call_using_api_key(consts.WEBEX_GET_ROOMS_ENDPOINT, action_result, params=None)
            if phantom.is_fail(ret_val):
                self.save_progress(consts.WEBEX_ERROR_TEST_CONNECTIVITY)
                return action_result.get_status()

            self.save_progress(consts.WEBEX_SUCCESS_TEST_CONNECTIVITY)
            return action_result.set_status(phantom.APP_SUCCESS)

        # Get initial REST URL
        ret_val, app_rest_url = self._get_app_rest_url(action_result)
        if phantom.is_fail(ret_val):
            self.save_progress(f"Rest URL not available. Error: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, status_message=consts.WEBEX_ERROR_TEST_CONNECTIVITY)

        # Append /result to create redirect_uri
        redirect_uri = f"{app_rest_url}/result"
        app_state[consts.WEBEX_STR_REDIRECT_URI] = redirect_uri

        self.save_progress("Using OAuth URL:")
        self.save_progress(redirect_uri)
        try:
            self._scopes = urllib.quote(self._scopes)
        except Exception as ex:
            self.save_progress(consts.WEBEX_ERROR_TEST_CONNECTIVITY)
            error_message = _get_error_message_from_exception(ex, self)
            self.save_progress(error_message)
            return action_result.set_status(phantom.APP_ERROR, error_message)

        # Authorization URL used to make request for getting code which is used to generate access token
        authorization_url = consts.AUTHORIZATION_URL.format(
            client_id=self._client_id, redirect_uri=redirect_uri, response_type=consts.WEBEX_STR_CODE, state=self._asset_id, scope=self._scopes
        )

        authorization_url = f"{self._base_url}{authorization_url}"
        app_state["authorization_url"] = authorization_url

        # URL which would be shown to the user
        url_for_authorize_request = f"{app_rest_url}/start_oauth?asset_id={self._asset_id}&"
        _save_app_state(app_state, self._asset_id, self)

        self.save_progress("Please authorize user in a separate tab using URL")
        self.save_progress(url_for_authorize_request)  # nosemgrep

        # Wait time for authorization
        time.sleep(15)

        # Wait for some while user login to Cisco webex
        status = self._wait(action_result=action_result)

        # Empty message to override last message of waiting
        self.send_progress("")
        if phantom.is_fail(status):
            return action_result.get_status()

        self.save_progress("Code Received")
        self._state = _load_app_state(self._asset_id, self)

        # Deleting the local state file because of it replicates with actual state file while installing the app
        current_file_path = pathlib.Path(__file__).resolve()
        input_file = f"{self._asset_id}_state.json"
        state_file_path = current_file_path.with_name(input_file)
        state_file_path.unlink()

        # if code is not available in the state file
        if not self._state:
            self.save_progress(consts.WEBEX_STATE_FILE_ERROR_MESSAGE)
            self.save_progress(consts.WEBEX_ERROR_TEST_CONNECTIVITY)
            return action_result.set_status(phantom.APP_ERROR)

        if not self._state.get(consts.WEBEX_STR_CODE):
            self.save_progress(consts.WEBEX_AUTHORIZATION_ERROR_MESSAGE)
            self.save_progress(consts.WEBEX_ERROR_TEST_CONNECTIVITY)
            return action_result.set_status(phantom.APP_ERROR)

        current_code = self._state[consts.WEBEX_STR_CODE]
        self._state.pop(consts.WEBEX_STR_CODE)

        self.save_progress("Generating access token")

        data = {
            consts.WEBEX_STR_CLIENT_ID: self._client_id,
            consts.WEBEX_STR_SECRET: self._client_secret,
            consts.WEBEX_STR_GRANT_TYPE: "authorization_code",
            consts.WEBEX_STR_REDIRECT_URI: redirect_uri,
            consts.WEBEX_STR_CODE: current_code,
        }

        # For first time access, new access token is generated
        ret_val = self._generate_new_access_token(action_result=action_result, data=data)
        if phantom.is_fail(ret_val):
            self.save_progress(consts.WEBEX_ERROR_TEST_CONNECTIVITY)
            return action_result.get_status()

        self.save_progress("Getting info about the rooms to verify token")

        url = f"{self._base_url}{consts.WEBEX_GET_ROOMS_ENDPOINT}"
        ret_val, response = self._update_request(action_result=action_result, endpoint=url)

        if phantom.is_fail(ret_val):
            self.save_progress(consts.WEBEX_ERROR_TEST_CONNECTIVITY)
            return action_result.get_status()

        self.save_progress("Got room details successfully")

        self.save_progress(consts.WEBEX_SUCCESS_TEST_CONNECTIVITY)
        return action_result.set_status(phantom.APP_SUCCESS)

    def _make_rest_call_using_api_key(self, endpoint, action_result, params=None, data=None, method="get", verify=False):
        # Create a URL to connect to
        url = self._base_url + endpoint
        authToken = "Bearer " + self._api_key
        headers = {"Content-Type": "application/json", "Authorization": authToken}

        return self._make_rest_call(url, action_result, params=params, headers=headers, data=data, method=method, verify=verify)

    def _handle_list_rooms(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        if self._api_key:
            ret_val, response = self._make_rest_call_using_api_key(consts.WEBEX_GET_ROOMS_ENDPOINT, action_result)
        else:
            ret_val, response = self._update_request(action_result, consts.WEBEX_GET_ROOMS_ENDPOINT)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        self.debug_print("Updating the summary")
        summary = action_result.update_summary({"total_rooms": 0})
        resp_value = response.get("items", [])
        if type(resp_value) != list:
            resp_value = [resp_value]

        for curr_item in resp_value:
            action_result.add_data(curr_item)

        summary["total_rooms"] = action_result.get_data_size()
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_get_user(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))
        uri_endpoint = consts.WEBEX_GET_USER_ENDPOINT.format(param["email_address"])

        if self._api_key:
            ret_val, response = self._make_rest_call_using_api_key(uri_endpoint, action_result, params=None)
        else:
            ret_val, response = self._update_request(action_result, uri_endpoint)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        self.debug_print("Updating the summary")
        summary = action_result.update_summary({"found_user": False})
        resp_value = response.get("items", [])

        for resp in resp_value:
            action_result.add_data(resp)

        is_user_found = True if action_result.get_data_size() > 0 else False
        summary["found_user"] = is_user_found

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        if not is_user_found:
            return action_result.set_status(phantom.APP_ERROR, consts.WEBEX_ERROR_USER_NOT_FOUND)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_send_message(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))
        dest_type = param["destination_type"]
        is_markdown = param.get("is_markdown", False)

        sendto_field = "toPersonId" if (dest_type == "user") else "roomId"
        message_field = "markdown" if is_markdown else "text"

        uri_endpoint = consts.WEBEX_SEND_MESSAGE_ENDPOINT
        user_id = param["endpoint_id"]
        message = param["message"]
        data = {sendto_field: user_id, message_field: message}

        if self._api_key:
            ret_val, response = self._make_rest_call_using_api_key(uri_endpoint, action_result, data=data, method="post")
        else:
            ret_val, response = self._update_request(action_result, uri_endpoint, data=data, method="post")

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        action_result.add_data(response)

        message = consts.WEBEX_SUCCESS_SEND_MESSAGE

        self.debug_print("Updating the summary")
        summary = action_result.update_summary({})
        summary["message"] = message

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, message)

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS

        action_id = self.get_action_identifier()

        if action_id == "test_connectivity":
            ret_val = self._handle_test_connectivity(param)

        elif action_id == "list_rooms":
            ret_val = self._handle_list_rooms(param)

        elif action_id == "get_user":
            ret_val = self._handle_get_user(param)

        elif action_id == "send_message":
            ret_val = self._handle_send_message(param)

        return ret_val

    def decrypt_state(self, state):
        if not state.get(consts.WEBEX_STR_IS_ENCRYPTED):
            return state

        access_token = state.get(consts.WEBEX_STR_TOKEN, {}).get(consts.WEBEX_STR_ACCESS_TOKEN)
        if access_token:
            try:
                state[consts.WEBEX_STR_TOKEN][consts.WEBEX_STR_ACCESS_TOKEN] = decrypt(access_token, self._asset_id)
            except Exception as ex:
                _, error_message = _get_error_message_from_exception(ex, self)
                self.debug_print(f"{consts.WEBEX_DECRYPTION_ERROR}: {error_message}")
                state[consts.WEBEX_STR_TOKEN][consts.WEBEX_STR_ACCESS_TOKEN] = None

        refresh_token = state.get(consts.WEBEX_STR_TOKEN, {}).get(consts.WEBEX_STR_REFRESH_TOKEN)
        if refresh_token:
            try:
                state[consts.WEBEX_STR_TOKEN][consts.WEBEX_STR_REFRESH_TOKEN] = decrypt(refresh_token, self._asset_id)
            except Exception as ex:
                _, error_message = _get_error_message_from_exception(ex, self)
                self.debug_print(f"{consts.WEBEX_DECRYPTION_ERROR}: {error_message}")
                state[consts.WEBEX_STR_TOKEN][consts.WEBEX_STR_REFRESH_TOKEN] = None
        state[consts.WEBEX_STR_IS_ENCRYPTED] = False
        return state

    def encrypt_state(self, state):
        if state.get(consts.WEBEX_STR_IS_ENCRYPTED):
            return state

        access_token = state.get(consts.WEBEX_STR_TOKEN, {}).get(consts.WEBEX_STR_ACCESS_TOKEN)
        if access_token:
            try:
                state[consts.WEBEX_STR_TOKEN][consts.WEBEX_STR_ACCESS_TOKEN] = encrypt(access_token, self._asset_id)
            except Exception as ex:
                _, error_message = _get_error_message_from_exception(ex, self)
                self.debug_print(f"{consts.WEBEX_ENCRYPTION_ERROR}: {error_message}")
                state[consts.WEBEX_STR_TOKEN][consts.WEBEX_STR_ACCESS_TOKEN] = None

        refresh_token = state.get(consts.WEBEX_STR_TOKEN, {}).get(consts.WEBEX_STR_REFRESH_TOKEN)
        if refresh_token:
            try:
                state[consts.WEBEX_STR_TOKEN][consts.WEBEX_STR_REFRESH_TOKEN] = encrypt(refresh_token, self._asset_id)
            except Exception as ex:
                _, error_message = _get_error_message_from_exception(ex, self)
                self.debug_print(f"{consts.WEBEX_ENCRYPTION_ERROR}: {error_message}")
                state[consts.WEBEX_STR_TOKEN][consts.WEBEX_STR_REFRESH_TOKEN] = None

        state[consts.WEBEX_STR_IS_ENCRYPTED] = True
        return state

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._asset_id = self.get_asset_id()
        self._state = self.load_state()

        config = self.get_config()
        self._base_url = consts.BASE_URL
        self._api_key = config.get("authorization_key", None)

        self._client_id = config.get(consts.WEBEX_STR_CLIENT_ID, None)
        self._client_secret = config.get(consts.WEBEX_STR_SECRET, None)

        self._scopes = list(filter(None, [scope.strip() for scope in config.get(consts.WEBEX_STR_SCOPE, consts.SCOPE).split(" ")]))
        self._scopes = " ".join(self._scopes)

        if not self._api_key and (not self._client_id and not self._client_secret):
            return self.set_status(phantom.APP_ERROR, status_message=consts.WEBEX_ERROR_REQUIRED_CONFIG_PARAMS)

        if not self._api_key and ((self._client_id and not self._client_secret) or (self._client_secret and not self._client_id)):
            return self.set_status(phantom.APP_ERROR, status_message=consts.WEBEX_ERROR_REQUIRED_CONFIG_PARAMS)

        self._access_token = self._state.get(consts.WEBEX_STR_TOKEN, {}).get(consts.WEBEX_STR_ACCESS_TOKEN)
        self._refresh_token = self._state.get(consts.WEBEX_STR_TOKEN, {}).get(consts.WEBEX_STR_REFRESH_TOKEN)

        return phantom.APP_SUCCESS

    def finalize(self):
        # Save the state, this data is saved accross actions and app upgrades
        self.save_state(self._state)
        return phantom.APP_SUCCESS


if __name__ == "__main__":
    import argparse
    import sys

    import pudb

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument("input_test_json", help="Input Test JSON file")
    argparser.add_argument("-u", "--username", help="username", required=False)
    argparser.add_argument("-p", "--password", help="password", required=False)
    argparser.add_argument("-v", "--verify", action="store_true", help="verify", required=False, default=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password
    verify = args.verify

    if username is not None and password is None:
        # User specified a username but not a password, so ask
        import getpass

        password = getpass.getpass("Password: ")

    if username and password:
        try:
            print("Accessing the Login page")
            r = requests.get(BaseConnector._get_phantom_base_url() + "login", verify=verify, timeout=consts.WEBEX_DEFAULT_TIMEOUT)
            csrftoken = r.cookies["csrftoken"]

            data = dict()
            data["username"] = username
            data["password"] = password
            data["csrfmiddlewaretoken"] = csrftoken

            headers = dict()
            headers["Cookie"] = "csrftoken=" + csrftoken
            headers["Referer"] = BaseConnector._get_phantom_base_url()

            print("Logging into Platform to get the session id")
            r2 = requests.post(
                BaseConnector._get_phantom_base_url(), verify=verify, data=data, headers=headers, timeout=consts.WEBEX_DEFAULT_TIMEOUT
            )
            session_id = r2.cookies["sessionid"]
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            sys.exit(1)

    if len(sys.argv) < 2:
        print("No test json specified as input")
        sys.exit(0)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = CiscoWebexConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json["user_session_token"] = session_id

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)
