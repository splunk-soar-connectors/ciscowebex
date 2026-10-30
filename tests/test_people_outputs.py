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
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.actions import get_user, list_users
from src.app import app


@pytest.mark.parametrize("module", [get_user, list_users])
@pytest.mark.parametrize(
    "people",
    [
        [
            {
                "id": "person-one",
                "emails": ["one@example.com", "alias@example.com"],
                "roles": ["role-one", "role-two"],
                "status": "active",
            },
            {
                "id": "person-two",
                "emails": ["two@example.com"],
                "roles": [],
                "status": "inactive",
            },
        ],
        [{"id": "person-one", "emails": [], "roles": []}],
        [{"id": "person-one", "emails": ["one@example.com"]}],
        [
            {
                "id": "person-one",
                "emails": ["one@example.com"],
                "roles": None,
                "status": None,
            }
        ],
    ],
    ids=["multiple-values-and-people", "empty-arrays", "omitted-roles", "null-roles"],
)
def test_people_arrays_survive_action_results(monkeypatch, module, people):
    """Exercise SDK validation and serialization, not only model construction."""
    request = Mock(return_value={"items": deepcopy(people)})
    monkeypatch.setattr(module, "make_rest_call", request)
    manager = Mock()
    monkeypatch.setattr(app, "actions_manager", manager)
    state = {}
    soar = SimpleNamespace(
        set_summary=lambda summary: state.update(summary=summary),
        get_summary=lambda: state.get("summary"),
        set_message=lambda message: state.update(message=message),
        get_message=lambda: state.get("message", ""),
    )
    action = getattr(module, module.__name__.rsplit(".", 1)[-1])
    params = (
        {"email_address": "one@example.com"}
        if module is get_user
        else {"email": "one@example.com"}
    )

    assert action(action.params_class(**params), soar=soar, asset=SimpleNamespace())

    manager.add_exception.assert_not_called()
    manager.add_result.assert_called_once()
    result = manager.add_result.call_args.args[0]
    assert result.get_status()
    assert [item["id"] for item in result.get_data()] == [
        person["id"] for person in people
    ]
    for person, output in zip(people, result.get_data(), strict=True):
        assert output["emails"] == person["emails"]
        assert output.get("roles") == person.get("roles")
        assert output.get("status") == person.get("status")
        if module is get_user:
            assert "user_status" not in output
    assert request.return_value == {"items": people}
    if module is get_user:
        assert result.get_summary() == {"found_user": True}
    else:
        assert result.get_summary()["total_people"] == len(people)

    fields = {
        field["data_path"]: field for field in action.meta.output._to_json_schema()
    }
    assert fields["action_result.data.*.emails.*"]["contains"] == ["email"]
    if module is list_users:
        assert fields["action_result.data.*.roles.*"]["data_type"] == "string"
