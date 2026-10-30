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

from src.actions import list_rooms as module
from src.app import app


@pytest.mark.parametrize(
    "items",
    [
        [],
        {"id": "room-one", "title": "One", "extra": {"keep": True}},
        [{"id": "room-one", "title": "One"}, {"id": "room-two", "title": "Two"}],
        [{"id": "room-one", "title": "One", "status": "vendor-status"}],
    ],
    ids=["empty", "singleton", "multiple", "vendor-field-preserved"],
)
def test_list_rooms_retains_legacy_columns_and_response_fields(monkeypatch, items):
    original = deepcopy(items)
    api = Mock(return_value={"items": items})
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
    action = module.list_rooms

    assert action(action.params_class(), soar=soar, asset=SimpleNamespace())

    manager.add_exception.assert_not_called()
    manager.add_result.assert_called_once()
    result = manager.add_result.call_args.args[0]
    assert result.get_status()
    expected = items if isinstance(items, list) else [items]
    assert result.get_summary() == {"total_rooms": len(expected)}
    assert [item["id"] for item in result.get_data()] == [
        item["id"] for item in expected
    ]
    for source, output in zip(expected, result.get_data(), strict=True):
        for field, value in source.items():
            assert output[field] == value
        if "status" not in source:
            assert "status" not in output
    assert items == original
    api.assert_called_once()
    assert api.call_args.args[1] == "/rooms"

    fields = list(action.meta.output._to_json_schema())
    columns = [
        field["column_name"].upper() for field in fields if "column_name" in field
    ]
    assert columns == ["ROOM NAME", "ID"]
    assert action.meta.render_as == "table"
