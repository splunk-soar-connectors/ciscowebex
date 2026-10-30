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
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.actions import ai_meeting_summary as module
from src.app import app


@pytest.mark.parametrize(
    "name_fields",
    [{}, {"recordName": None}, {"recordName": "Meeting recording"}],
    ids=["missing", "null", "present"],
)
def test_ai_summary_preserves_content_with_optional_recording_name(
    monkeypatch, name_fields
):
    metadata = {
        "recordUUID": "recording-one",
        "suggestedNoteUrl": "https://example.webex.com/notes",
        "actionItemUrl": "https://example.webex.com/actions",
        **name_fields,
    }
    api = Mock(
        side_effect=[
            metadata,
            {
                "content": json.dumps(
                    {
                        "description": {"text": "Summary"},
                        "notes": [{"text": "Important note"}],
                    }
                )
            },
            {"content": json.dumps([{"content": "Follow up"}])},
        ]
    )
    monkeypatch.setattr(module, "make_rest_call", api)
    manager = Mock()
    monkeypatch.setattr(app, "actions_manager", manager)
    state = {}
    soar = SimpleNamespace(
        set_message=lambda message: state.update(message=message),
        get_message=lambda: state.get("message", ""),
        get_summary=lambda: None,
    )
    params = module.AiMeetingSummaryParams(
        recording_id="recording-one", site_url="example.webex.com"
    )

    assert module.ai_meeting_summary(params, soar=soar, asset=SimpleNamespace())

    manager.add_exception.assert_not_called()
    manager.add_result.assert_called_once()
    result = manager.add_result.call_args.args[0]
    assert result.get_status()
    assert (
        result.get_message()
        == "AI generated meeting summary and actions items retrieved successfully"
    )
    assert len(result.get_data()) == 1
    output = result.get_data()[0]
    assert output["recordingId"] == "recording-one"
    assert output["recordingName"] == name_fields.get("recordName")
    assert output["suggestedNote"] == "Summary\nImportant note"
    assert output["actionItems"] == "Follow up"
    assert api.call_count == 3
    assert module.ai_meeting_summary.meta.render_as == "table"
