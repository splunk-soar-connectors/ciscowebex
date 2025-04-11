# Cisco Webex

Publisher: Splunk \
Connector Version: 2.0.1 \
Product Vendor: Cisco \
Product Name: Cisco Webex \
Minimum Product Version: 6.0.2

This app integrates with Cisco Webex to implement investigative and genric actions

### Configuration variables

This table lists the configuration variables required to operate Cisco Webex. These variables are specified when configuring a Cisco Webex asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**authorization_key** | optional | password | Personal Access Token |
**client_id** | optional | string | Client ID |
**client_secret** | optional | password | Client Secret |
**scope** | optional | string | Scopes (Append extra space-seperated scopes which are added during app creation from webex portal) |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration \
[list rooms](#action-list-rooms) - List webex rooms \
[get user](#action-get-user) - Get user ID from e-mail address \
[send message](#action-send-message) - Send message to user or room

## action: 'test connectivity'

Validate the asset configuration for connectivity using supplied configuration

Type: **test** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'list rooms'

List webex rooms

Type: **investigate** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.data.\*.created | string | | 2018-01-05T02:43:33.032Z |
action_result.data.\*.creatorId | string | `creater id` | L2lzY69zcBFyazoxL3VzL1BFT1BMRS9iMmMwZjIwMS03NGQyLTRkYTEtYWM0Yi1mNzcEXAMPLE |
action_result.data.\*.id | string | `webex room id` | L2lzY69zcGFylsdovL3VzL1JPT00vMzg2NzFhODAtZjFjMi0xMWU3LTg1OWUtNDMzYWYEXAMPLE |
action_result.data.\*.isLocked | boolean | | True False |
action_result.data.\*.lastActivity | string | | 2018-01-08T21:26:38.851Z 2018-01-16T18:37:12.037Z |
action_result.data.\*.ownerId | string | | |
action_result.data.\*.title | string | | Test Alert Space |
action_result.data.\*.type | string | | group |
action_result.summary.total_rooms | numeric | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get user'

Get user ID from e-mail address

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**email_address** | required | User webex e-mail address | string | `email` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.email_address | string | `email` | examplemail@test.com |
action_result.data.\*.created | string | | |
action_result.data.\*.displayName | string | | Test User |
action_result.data.\*.firstName | string | | |
action_result.data.\*.id | string | `webex user id` | L2lzY29zcAByazovL3VzL1690T1BMRS9hMzMGQ4Mi01ZWE0LTQ3OTktOWM3Zi00M2E0MTEXAMPLE |
action_result.data.\*.lastModified | string | | |
action_result.data.\*.lastName | string | | |
action_result.data.\*.created | string | | 2018-01-04T20:46:30.734Z |
action_result.data.\*.emails | string | `email` | examplemail@test.com |
action_result.data.\*.lastActivity | string | | 2018-01-05T21:04:53.424Z |
action_result.data.\*.nickName | string | | Test User |
action_result.data.\*.orgId | string | | L2lzY29zcABCazovL3VzL09SR0FOSVpBVElPTi9jb2TEST |
action_result.data.\*.status | string | | inactive |
action_result.data.\*.type | string | | person |
action_result.summary.found_user | boolean | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'send message'

Send message to user or room

Type: **generic** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint_id** | required | User or Room ID | string | `webex user id` `webex room id` |
**destination_type** | required | Destination Type | string | |
**message** | required | Message | string | |
**is_markdown** | optional | Is the message Markdown formatted | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.destination_type | string | | room |
action_result.parameter.endpoint_id | string | `webex user id` `webex room id` | L2szY29zcGFyazovLABCVzL1JLT00vODliODk1ZWYtYjk2YS0zMTk0LTlhNDQtNDAxTEST5EXAMPLE |
action_result.parameter.message | string | | Compile Test hello room |
action_result.parameter.is_markdown | boolean | | True False |
action_result.data.\*.created | string | | 2018-01-08T21:27:31.755Z 2018-03-30T18:36:01.210Z |
action_result.data.\*.id | string | | L2szY29zcGFyazovLABCVzL1JLT00vODliODk1ZWYtYjk2YS0zMTk0LTlhNDQtNDATEST4MzEXAMPLE |
action_result.data.\*.personEmail | string | `email` | examplemail@test.com |
action_result.data.\*.personId | string | | L2szY29zcGFyazovLABCVzL1JLT00vODliODk1ZWYtYjk2YS0zMTk0TESTNDQtNDAxZTk4MzEXAMPLE |
action_result.data.\*.roomId | string | | L2szY29zcGFyazovLABCVzL1JLT00vODliODk1ZWYtYjk2YS0zMTESTTlhNDQtNDAxZTk4MzEXAMPLE |
action_result.data.\*.roomType | string | | direct group |
action_result.data.\*.text | string | | Compile Test hello room |
action_result.data.\*.toPersonId | string | | L2lzY1zcAByazovL3VzL1HNT1BMRS9hMzllMGQ4Mi01ZWE0LTQ3OTESTWM3Zi00M2E0MTI4MjEXAMPLE |
action_result.summary.message | string | | Message sent successfully |
action_result.message | string | | Message sent successfully |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2025 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
