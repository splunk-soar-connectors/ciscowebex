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
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from soar_sdk.exceptions import ActionFailure

from src.actions import list_messages, list_users, retrieve_meeting_participants
from src.app import app
from src.helper import validate_integer


@pytest.mark.parametrize("value", [1, 1.0, "1", 100])
def test_shared_integer_validator_accepts_whole_positive_values(value):
    assert validate_integer(value, "limit") == int(value)


@pytest.mark.parametrize(
    "value", [None, "", "bad", 0, -1, 0.5, 1.5, "1.5", float("inf"), float("nan")]
)
def test_shared_integer_validator_rejects_invalid_values(value):
    with pytest.raises(ActionFailure, match="limit"):
        validate_integer(value, "limit")


@pytest.fixture(
    params=[
        (list_messages, {"room_id": "room"}, 50, "total_messages"),
        (list_users, {}, 100, "total_people"),
        (
            retrieve_meeting_participants,
            {"meeting_id": "meeting"},
            10,
            "total_participants",
        ),
    ],
    ids=["messages", "users", "participants"],
)
def action_context(request, monkeypatch):
    module, params, default, summary_key = request.param
    action = getattr(module, module.__name__.rsplit(".", 1)[-1])
    api = Mock(return_value={"items": []})
    monkeypatch.setattr(module, "make_rest_call", api)
    manager = Mock()
    monkeypatch.setattr(app, "actions_manager", manager)
    state = {}
    soar = SimpleNamespace(
        set_summary=lambda summary: state.update(summary=summary),
        get_summary=lambda: state.get("summary"),
        set_message=lambda message: state.update(message=message),
        get_message=lambda: state.get("message", ""),
    )
    return action, params, default, summary_key, api, manager, soar


@pytest.mark.parametrize("value", [0, -1, 0.5, 1.5, "1.5", float("inf"), float("nan")])
def test_invalid_limit_fails_before_api_request(action_context, value):
    action, params, _, _, api, manager, soar = action_context
    model = action.params_class(**params, limit=value)
    assert not action(model, soar=soar, asset=SimpleNamespace())
    api.assert_not_called()
    manager.add_exception.assert_not_called()
    manager.add_result.assert_called_once()
    result = manager.add_result.call_args.args[0]
    assert not result.get_status()
    assert "limit" in result.get_message()


@pytest.mark.parametrize("value", [None, "bad"])
def test_null_and_nonnumeric_limit_fail_model_validation(action_context, value):
    action, params, _, _, api, _, _ = action_context
    with pytest.raises(ValidationError):
        action.params_class(**params, limit=value)
    api.assert_not_called()


@pytest.mark.parametrize("value", ["omitted", 1, 1.0, 101])
def test_valid_limit_and_declared_defaults_reach_api_unchanged(action_context, value):
    action, params, default, summary_key, api, manager, soar = action_context
    if value != "omitted":
        params = {**params, "limit": value}
    model = action.params_class(**params)
    assert action(model, soar=soar, asset=SimpleNamespace())
    expected = default if value == "omitted" else int(value)
    assert api.call_args.kwargs["params"]["max"] == expected
    result = manager.add_result.call_args.args[0]
    assert result.get_summary()[summary_key] == 0
    # Bounds beyond positivity remain the vendor's responsibility, as in legacy.
    schema = action.params_class._to_json_schema()["limit"]
    assert schema["default"] == default
    assert not schema["required"]
