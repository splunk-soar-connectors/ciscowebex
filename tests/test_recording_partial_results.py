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
from copy import deepcopy
from inspect import unwrap
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from soar_sdk.action_results import ActionResult
from soar_sdk.auth import OAuthClientError
from soar_sdk.exceptions import ActionFailure

from src.actions import get_recording_details as module
from src.app import app


@pytest.fixture
def context(monkeypatch):
    api = Mock()
    monkeypatch.setattr(module, "make_rest_call", api)
    manager = Mock()
    monkeypatch.setattr(app, "actions_manager", manager)
    state = {}
    soar = SimpleNamespace(
        set_message=lambda message: state.update(message=message),
        get_message=lambda: state.get("message", ""),
        get_summary=lambda: None,
    )
    return api, manager, soar


def first_recording():
    return {
        "id": "first",
        "topic": "Retain this recording",
        "password": "synthetic-password",  # pragma: allowlist secret
        "extra": {
            "password": "synthetic-password",  # pragma: allowlist secret
            "keep": "extra-data",
        },
    }


@pytest.mark.parametrize("mode", ["handler", "sdk"])
@pytest.mark.parametrize(
    "params",
    [{"recording_id": "first", "meeting_id": "ignored"}, {"meeting_id": "meeting"}],
)
def test_full_success_uses_typed_outputs_and_preserves_schema(context, mode, params):
    api, manager, soar = context
    recordings = [first_recording()]
    if "recording_id" in params:
        api.side_effect = deepcopy(recordings)
    else:
        recordings.append({"id": "second"})
        api.side_effect = [
            {"items": [{"id": "first"}, {"id": "second"}]},
            *deepcopy(recordings),
        ]
    model = module.GetRecordingDetailsParams(**params)
    action = module.get_recording_details
    if mode == "handler":
        outputs = unwrap(action)(model, soar, SimpleNamespace())
        assert isinstance(outputs, list)
        assert all(
            isinstance(item, module.GetRecordingDetailsOutput) for item in outputs
        )
        data = [item.model_dump(by_alias=True) for item in outputs]
    else:
        assert action(model, soar=soar, asset=SimpleNamespace())
        manager.add_result.assert_called_once()
        result = manager.add_result.call_args.args[0]
        assert result.get_status()
        assert result.get_message() == "Recording details retrieved successfully"
        data = result.get_data()
    assert [item["id"] for item in data] == [item["id"] for item in recordings]
    assert "password" not in data[0]
    assert data[0]["extra"] == {"keep": "extra-data"}
    assert action.meta.output is module.GetRecordingDetailsOutput
    assert action.meta.render_as == "table"
    fields = {item["data_path"]: item for item in action.meta.output._to_json_schema()}
    assert fields["action_result.data.*.id"]["contains"] == ["webex recording id"]
    if "recording_id" in params:
        assert [call.args[1] for call in api.call_args_list] == ["/recordings/first"]


@pytest.mark.parametrize("mode", ["handler", "sdk"])
@pytest.mark.parametrize(
    "failure",
    [
        ActionFailure("Webex denied second recording"),
        OAuthClientError("Refresh failed"),
        {"id": 123},
        None,
    ],
)
def test_later_failure_keeps_completed_sanitized_data(context, mode, failure):
    api, manager, soar = context
    api.side_effect = [
        {"items": [{"id": "first"}, {"id": "second"}]},
        first_recording(),
        failure,
    ]
    params = module.GetRecordingDetailsParams(
        meeting_id="meeting", host_email="host@example.com"
    )
    action = module.get_recording_details
    if mode == "handler":
        result = unwrap(action)(params, soar, SimpleNamespace())
        assert isinstance(result, ActionResult)
    else:
        assert not action(params, soar=soar, asset=SimpleNamespace())
        manager.add_result.assert_called_once()
        manager.add_exception.assert_not_called()
        result = manager.add_result.call_args.args[0]
    assert not result.get_status()
    assert [item["id"] for item in result.get_data()] == ["first"]
    assert result.get_data()[0]["topic"] == "Retain this recording"
    assert result.get_data()[0]["extra"] == {"keep": "extra-data"}
    assert "password" not in result.get_data()[0]
    assert "synthetic-password" not in result.get_message()
    assert "retrieved successfully" not in result.get_message()
    assert result.get_message()
    assert [call.args[1] for call in api.call_args_list] == [
        "/recordings",
        "/recordings/first",
        "/recordings/second",
    ]
    assert all(
        call.kwargs["params"]["hostEmail"] == "host@example.com"
        for call in api.call_args_list
    )


@pytest.mark.parametrize("bad_id", [None, "..", ""])
def test_later_invalid_id_retains_first_result_without_requesting_bad_id(
    context, bad_id
):
    api, manager, soar = context
    api.side_effect = [{"items": [{"id": "first"}, {"id": bad_id}]}, first_recording()]
    params = module.GetRecordingDetailsParams(meeting_id="meeting")
    assert not module.get_recording_details(params, soar=soar, asset=SimpleNamespace())
    result = manager.add_result.call_args.args[0]
    assert [item["id"] for item in result.get_data()] == ["first"]
    assert "Invalid recording_id returned by Webex" in result.get_message()
    assert api.call_count == 2


@pytest.mark.parametrize(
    "params,responses",
    [
        ({}, []),
        ({"recording_id": ".."}, []),
        ({"recording_id": "first"}, [ActionFailure("first failed")]),
        ({"meeting_id": "meeting"}, [{"items": []}]),
    ],
)
def test_failure_before_any_completed_recording_returns_empty_failure(
    context, params, responses
):
    api, manager, soar = context
    api.side_effect = responses
    result = unwrap(module.get_recording_details)(
        module.GetRecordingDetailsParams(**params), soar, SimpleNamespace()
    )
    assert isinstance(result, ActionResult)
    assert not result.get_status()
    assert result.get_data() == []
    assert result.get_message()
