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
from typing import Any

from pydantic import ConfigDict, model_validator
from soar_sdk.action_results import ActionOutput


class WebexOutput(ActionOutput):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="before")
    @classmethod
    def allow_sparse_response_fields(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        values = dict(values)
        for name, field in cls.model_fields.items():
            if name in values or (field.alias and field.alias in values):
                continue
            if field.is_required():
                annotation = field.annotation
                if getattr(annotation, "__origin__", None) is list:
                    values[name] = []
                elif isinstance(annotation, type) and issubclass(
                    annotation, ActionOutput
                ):
                    values[name] = {}
                else:
                    values[name] = None
        return values
