# Cisco Webex

Publisher: Splunk \
Connector Version: 2.0.1 \
Product Vendor: Cisco \
Product Name: Cisco Webex \
Minimum Product Version: 6.3.0

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
[send message](#action-send-message) - Send message to user or room \
[create a room](#action-create-a-room) - Create a new Webex room (space) \
[add people](#action-add-people) - Add a people to a Webex room (space) as a member or moderator \
[schedule meeting](#action-schedule-meeting) - Schedule a Webex meeting with specific details and invitees \
[retrieve meeting participants](#action-retrieve-meeting-participants) - Retrieve all participants in an in-progress or ended Webex meeting \
[list messages](#action-list-messages) - Retrieve a list of messages from a Webex room or 1:1 conversation \
[get message details](#action-get-message-details) - Retrieve the details of a specific Webex message by message ID \
[get meeting details](#action-get-meeting-details) - Retrieve details of a specific Webex meeting using meeting ID or meeting number

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

## action: 'create a room'

Create a new Webex room (space)

Type: **generic** \
Read only: **False**

Creates a new Webex room with optional team, lock(moderate), public, classification, and announcement settings. Public rooms require a description. Announcement mode requires the room to be locked. Team rooms cannot be locked. Requires permissions spark:rooms_write; spark:teams:read is needed if using team_id; classification needs spark:compliance_read.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**title** | required | A user-friendly name for the room | string | |
**team_id** | optional | The ID for the team with which this room is associated | string | |
**classification_id** | optional | The classification_id for the room | string | |
**is_locked** | optional | Set the space as locked/moderated; creator becomes a moderator | boolean | |
**is_public** | optional | If true, the room is discoverable by anyone in the org; description must be provided | boolean | |
**description** | optional | The description of the space | string | |
**is_announcement_only** | optional | Sets the space into announcement-only mode | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.id | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.type | string | | group |
action_result.data.\*.title | string | | test room |
action_result.data.\*.created | string | | 2025-05-09T09:57:17.803Z |
action_result.data.\*.ownerId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.isLocked | boolean | | True False |
action_result.data.\*.isPublic | boolean | | True False |
action_result.data.\*.creatorId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.lastActivity | string | | 2025-05-09T09:57:17.803Z |
action_result.parameter.title | string | | |
action_result.parameter.team_id | string | | |
action_result.parameter.classification_id | string | | |
action_result.parameter.is_locked | boolean | | |
action_result.parameter.is_public | boolean | | |
action_result.parameter.description | string | | |
action_result.parameter.is_announcement_only | boolean | | |
summary.total_objects_successful | numeric | | |
action_result.status | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | |

## action: 'add people'

Add a people to a Webex room (space) as a member or moderator

Type: **generic** \
Read only: **False**

Adds a person to a Webex room using their ID or email. You can optionally assign them as a moderator. Requires `spark:memberships_write` scope. Compliance officers cannot add users to empty team spaces.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**room_id** | required | The ID of the room to add the person to | string | |
**person_id** | optional | The ID of the person to add (use either person_id or person_email) | string | |
**person_email** | optional | The email address of the person to add (use either person_email or person_id) | string | |
**is_moderator** | optional | Set to true to make the person a room moderator | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.id | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.roomId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.created | string | | 2025-05-09T09:58:50.433Z |
action_result.data.\*.personId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.roomType | string | | group |
action_result.data.\*.isMonitor | boolean | | True False |
action_result.data.\*.isModerator | boolean | | True False |
action_result.data.\*.personEmail | string | | example@example.com |
action_result.data.\*.personOrgId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.isRoomHidden | boolean | | True False |
action_result.data.\*.personDisplayName | string | | TEST USER |
action_result.parameter.room_id | string | | |
action_result.parameter.person_id | string | | |
action_result.parameter.person_email | string | | |
action_result.parameter.is_moderator | boolean | | |
summary.total_objects_successful | numeric | | |
action_result.status | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | |

## action: 'schedule meeting'

Schedule a Webex meeting with specific details and invitees

Type: **generic** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**title** | required | Title of the meeting (max 128 chars) | string | |
**start** | required | Meeting start time (ISO 8601) | string | |
**end** | required | Meeting end time (ISO 8601) | string | |
**timezone** | optional | IANA time zone for the meeting (e.g., America/Los_Angeles) | string | |
**description** | optional | Meeting description (max 1300 chars) | string | |
**password** | optional | Password to join the meeting | string | |
**enabled_auto_record_meeting** | optional | Automatically record when meeting starts | boolean | |
**allow_any_user_to_be_co_host** | optional | Allow any qualified user to be cohost | boolean | |
**enabled_join_before_host** | optional | Allow attendees to join before host | boolean | |
**join_before_host_minutes** | optional | Minutes attendees can join before host (0,5,10,15) | numeric | |
**enable_connect_audio_before_host** | optional | Allow audio connect before host | boolean | |
**invitees** | optional | List of emails to invite (comma‑separated) | string | |
**recurrence** | optional | Meeting series rule (RFC‑2445, e.g. FREQ=DAILY;INTERVAL=1) | string | |
**adhoc** | optional | Create an ad‑hoc (instant) meeting in a room | boolean | |
**room_id** | optional | Room (space) ID for ad‑hoc meeting | string | |
**send_email** | optional | Whether to email host & invitees | boolean | |
**host_email** | optional | Host email (admin scopes required) | string | |
**session_type_id** | optional | Session type ID (required for webinars) | numeric | |
**scheduled_type** | optional | Type of meeting: meeting, webinar, or personal_room_meeting | string | |
**enable_automatic_lock** | optional | Automatically lock the meeting after start | boolean | |
**automatic_lock_minutes** | optional | Minutes after start to auto‑lock | numeric | |
**public_meeting** | optional | List on public calendar | boolean | |
**reminder_time** | optional | Minutes before start to send host reminder | numeric | |
**unlocked_meeting_join_security** | optional | How non‑invitees join: allowJoin, allowJoinWithLobby, blockFromJoin | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.id | string | | test92d8997b4d36bc3ac1893c7ftest8 |
action_result.data.\*.end | string | | 2025-05-10T14:24:00Z |
action_result.data.\*.start | string | | 2025-05-10T13:24:00Z |
action_result.data.\*.state | string | | active |
action_result.data.\*.title | string | | test meeting |
action_result.data.\*.hostKey | string | | 210605 |
action_result.data.\*.siteUrl | string | | example.webex.com |
action_result.data.\*.webLink | string | | https://example.webex.com/example/j.php?MTID=m6325e89c172b9167381372a0b862a995 |
action_result.data.\*.password | string | | testdpXhe326 |
action_result.data.\*.timezone | string | | UTC |
action_result.data.\*.hostEmail | string | | ishans@example.com |
action_result.data.\*.telephony.links.\*.rel | string | | globalCallinNumbers |
action_result.data.\*.telephony.links.\*.href | string | | /v1/meetings/atest92d8997b4d36bc3ac1893c7ftest/globalCallinNumbers |
action_result.data.\*.telephony.links.\*.method | string | | GET |
action_result.data.\*.telephony.accessCode | string | | 26636572133 |
action_result.data.\*.telephony.callInNumbers.\*.label | string | | Call-in toll number (US/Canada) |
action_result.data.\*.telephony.callInNumbers.\*.tollType | string | | toll |
action_result.data.\*.telephony.callInNumbers.\*.callInNumber | string | | +1-000-525-6800 |
action_result.data.\*.hostUserId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.sipAddress | string | | 2660000000133@webex.com |
action_result.data.\*.meetingType | string | | meetingSeries |
action_result.data.\*.meetingNumber | string | | 26600002133 |
action_result.data.\*.publicMeeting | boolean | | True False |
action_result.data.\*.scheduledType | string | | meeting |
action_result.data.\*.sessionTypeId | numeric | | 159 |
action_result.data.\*.meetingOptions.enabledChat | boolean | | True False |
action_result.data.\*.meetingOptions.enabledVideo | boolean | | True False |
action_result.data.\*.meetingOptions.enabledFileTransfer | boolean | | True False |
action_result.data.\*.dialInIpAddress | string | | 173.243.2.68 |
action_result.data.\*.excludePassword | boolean | | True False |
action_result.data.\*.hostDisplayName | string | | test user |
action_result.data.\*.enabledLiveStream | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledAnnotate | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledChatHost | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledViewAnyPage | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledSaveDocument | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledShareContent | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledChatPresenter | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledPrintDocument | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledRemoteControl | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledViewThumbnails | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledViewAnyDocument | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledViewParticipantList | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledChatOtherParticipants | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledContactOperatorPrivately | boolean | | True False |
action_result.data.\*.enableAutomaticLock | boolean | | True False |
action_result.data.\*.enabledJoinBeforeHost | boolean | | True False |
action_result.data.\*.joinBeforeHostMinutes | numeric | | 5 |
action_result.data.\*.allowAnyUserToBeCoHost | boolean | | True False |
action_result.data.\*.audioConnectionOptions.entryAndExitTone | string | | noTone |
action_result.data.\*.audioConnectionOptions.audioConnectionType | string | | webexAudio |
action_result.data.\*.audioConnectionOptions.enabledGlobalCallIn | boolean | | True False |
action_result.data.\*.audioConnectionOptions.enabledTollFreeCallIn | boolean | | True False |
action_result.data.\*.audioConnectionOptions.muteAttendeeUponEntry | boolean | | True False |
action_result.data.\*.audioConnectionOptions.enabledAudienceCallBack | boolean | | True False |
action_result.data.\*.audioConnectionOptions.allowAttendeeToUnmuteSelf | boolean | | True False |
action_result.data.\*.audioConnectionOptions.allowHostToUnmuteParticipants | boolean | | True False |
action_result.data.\*.enabledVisualWatermark | boolean | | True False |
action_result.data.\*.enabledBreakoutSessions | boolean | | True False |
action_result.data.\*.allowFirstUserToBeCoHost | boolean | | True False |
action_result.data.\*.enabledAutoRecordMeeting | boolean | | True False |
action_result.data.\*.allowAuthenticatedDevices | boolean | | True False |
action_result.data.\*.simultaneousInterpretation.enabled | boolean | | True False |
action_result.data.\*.phoneAndVideoSystemPassword | string | | 97237943 |
action_result.data.\*.unlockedMeetingJoinSecurity | string | | allowJoin |
action_result.data.\*.enableConnectAudioBeforeHost | boolean | | True False |
action_result.parameter.title | string | | |
action_result.parameter.start | string | | |
action_result.parameter.end | string | | |
action_result.parameter.timezone | string | | |
action_result.parameter.description | string | | |
action_result.parameter.password | string | | |
action_result.parameter.enabled_auto_record_meeting | boolean | | |
action_result.parameter.allow_any_user_to_be_co_host | boolean | | |
action_result.parameter.enabled_join_before_host | boolean | | |
action_result.parameter.join_before_host_minutes | numeric | | |
action_result.parameter.enable_connect_audio_before_host | boolean | | |
action_result.parameter.invitees | string | | |
action_result.parameter.recurrence | string | | |
action_result.parameter.adhoc | boolean | | |
action_result.parameter.room_id | string | | |
action_result.parameter.send_email | boolean | | |
action_result.parameter.host_email | string | | |
action_result.parameter.session_type_id | numeric | | |
action_result.parameter.scheduled_type | string | | |
action_result.parameter.enable_automatic_lock | boolean | | |
action_result.parameter.automatic_lock_minutes | numeric | | |
action_result.parameter.public_meeting | boolean | | |
action_result.parameter.reminder_time | numeric | | |
action_result.parameter.unlocked_meeting_join_security | string | | |
summary.total_objects_successful | numeric | | |
action_result.status | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | |

## action: 'retrieve meeting participants'

Retrieve all participants in an in-progress or ended Webex meeting

Type: **generic** \
Read only: **True**

Retrieve a list of participants from a specific Webex meeting instance or series. Requires meetingId. Optional parameters include host email, time filters, and breakout session ID.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**meeting_id** | required | Unique identifier of the meeting (not personal room meeting) | string | |
**breakout_session_id** | optional | Unique ID of a breakout session in an ended meeting | string | |
**meeting_start_time_from** | optional | Start time to filter meetings (ISO 8601 format) | string | |
**meeting_start_time_to** | optional | End time to filter meetings (ISO 8601 format) | string | |
**host_email** | optional | Email address of the meeting host (admin-only use) | string | |
**join_time_from** | optional | Start of participant join time range (ISO 8601 format) | string | |
**join_time_to** | optional | End of participant join time range (ISO 8601 format) | string | |
**limit** | optional | Max number of participants to return (1–100) | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.id | string | | testef03e1a49be883320fe35fde314_I_65220test54323715_3118cefb-81e7-492d-8223-1fe0a353test |
action_result.data.\*.host | boolean | | True False |
action_result.data.\*.email | string | | example@example.com |
action_result.data.\*.muted | boolean | | True False |
action_result.data.\*.state | string | | end |
action_result.data.\*.coHost | boolean | | True False |
action_result.data.\*.devices.\*.leftTime | string | | 2025-05-08T12:40:55Z |
action_result.data.\*.devices.\*.deviceType | string | | mac |
action_result.data.\*.devices.\*.joinedTime | string | | 2025-05-08T12:40:49Z |
action_result.data.\*.devices.\*.correlationId | string | | test927a-496a-4678-ac62-bcbdaadctest |
action_result.data.\*.devices.\*.durationSecond | numeric | | 6 |
action_result.data.\*.invitee | boolean | | True False |
action_result.data.\*.siteUrl | string | | example.webex.com |
action_result.data.\*.leftTime | string | | 2025-05-08T12:40:55Z |
action_result.data.\*.hostEmail | string | | example@example.com |
action_result.data.\*.meetingId | string | | test2ef03e1a49be883320fe35fde314_I_65220661465432test |
action_result.data.\*.joinedTime | string | | 2025-05-08T12:40:49Z |
action_result.data.\*.displayName | string | | test user |
action_result.data.\*.spaceModerator | boolean | | True False |
action_result.data.\*.meetingStartTime | string | | 2025-05-08T12:40:49Z |
action_result.parameter.meeting_id | string | | |
action_result.parameter.breakout_session_id | string | | |
action_result.parameter.meeting_start_time_from | string | | |
action_result.parameter.meeting_start_time_to | string | | |
action_result.parameter.host_email | string | | |
action_result.parameter.join_time_from | string | | |
action_result.parameter.join_time_to | string | | |
action_result.parameter.limit | numeric | | |
summary.total_objects_successful | numeric | | |
action_result.status | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | |

## action: 'list messages'

Retrieve a list of messages from a Webex room or 1:1 conversation

Type: **generic** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**room_id** | required | The ID of the room to list messages from | string | |
**parent_id** | optional | List messages in a thread by parent message ID | string | |
**before** | optional | List messages sent before a specific date/time (ISO 8601 format) | string | |
**before_message** | optional | List messages sent before a specific message ID | string | |
**limit** | optional | The maximum number of messages to return (default 50, max 100) | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.id | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.html | string | | hello <spark-mention data-object-type="person" data-object-id="TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST">test</spark-mention> |
action_result.data.\*.text | string | | hello test |
action_result.data.\*.roomId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.created | string | | 2025-05-09T05:37:36.687Z |
action_result.data.\*.personId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.roomType | string | | group |
action_result.data.\*.personEmail | string | | example@example.com |
action_result.data.\*.parentId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.meetingId | string | | 9testf03e1a49be883320fe35fde314_I_6522066146543test |
action_result.parameter.room_id | string | | |
action_result.parameter.parent_id | string | | |
action_result.parameter.before | string | | |
action_result.parameter.before_message | string | | |
action_result.parameter.limit | numeric | | |
summary.total_objects_successful | numeric | | |
action_result.status | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | |

## action: 'get message details'

Retrieve the details of a specific Webex message by message ID

Type: **generic** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**message_id** | required | The unique identifier of the message to retrieve | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.id | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.html | string | | hello <spark-mention data-object-type="person" data-object-id="TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST">test</spark-mention> |
action_result.data.\*.text | string | | hello test |
action_result.data.\*.roomId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.created | string | | 2025-05-09T05:37:36.687Z |
action_result.data.\*.personId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.roomType | string | | group |
action_result.data.\*.personEmail | string | | example@example.com |
action_result.parameter.message_id | string | | |
summary.total_objects_successful | numeric | | |
action_result.status | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | |

## action: 'get meeting details'

Retrieve details of a specific Webex meeting using meeting ID or meeting number

Type: **generic** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**meeting_id** | required | The unique identifier of the meeting being requested (UUID format) | string | |
**current** | optional | Whether to retrieve only the current scheduled meeting of the series (true or false) | boolean | |
**host_email** | optional | Email address of the meeting host (for admin-level access) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.id | string | | ctest706b64041559c664a83e6bfcf60_20250509Ttest0Z |
action_result.data.\*.end | string | | 2025-05-09T13:20:00Z |
action_result.data.\*.start | string | | 2025-05-09T12:20:00Z |
action_result.data.\*.state | string | | ready |
action_result.data.\*.title | string | | MC Default |
action_result.data.\*.agenda | string | | |
action_result.data.\*.hostKey | string | | 889047 |
action_result.data.\*.siteUrl | string | | example.webex.com |
action_result.data.\*.webLink | string | | https://example.webex.com/example/j.php?MTID=me0a791a45ee400f06576ed07dd940d3e |
action_result.data.\*.password | string | | 72Xjx9PyYKA |
action_result.data.\*.timezone | string | | UTC |
action_result.data.\*.hostEmail | string | | example@example.com |
action_result.data.\*.telephony.links.\*.rel | string | | globalCallinNumbers |
action_result.data.\*.telephony.links.\*.href | string | | /v1/meetings/testa706b64041559c664a83e6btest/globalCallinNumbers |
action_result.data.\*.telephony.links.\*.method | string | | GET |
action_result.data.\*.telephony.accessCode | string | | 26620031238 |
action_result.data.\*.telephony.callInNumbers.\*.label | string | | Call-in toll number (US/Canada) |
action_result.data.\*.telephony.callInNumbers.\*.tollType | string | | toll |
action_result.data.\*.telephony.callInNumbers.\*.callInNumber | string | | +1-000-025-6800 |
action_result.data.\*.hostUserId | string | | TESTY29zcGFyazovL3VzL1JPT00vZmRkYmMzYjAtMmNTESTxMWYwLTgwZWItMjllNWE1OTTEST |
action_result.data.\*.isModified | boolean | | True False |
action_result.data.\*.sipAddress | string | | 26000031238@webex.com |
action_result.data.\*.hostDidJoin | boolean | | True False |
action_result.data.\*.meetingType | string | | scheduledMeeting |
action_result.data.\*.reminderTime | numeric | | 15 |
action_result.data.\*.meetingNumber | string | | 26620031238 |
action_result.data.\*.publicMeeting | boolean | | True False |
action_result.data.\*.scheduledType | string | | meeting |
action_result.data.\*.sessionTypeId | numeric | | 159 |
action_result.data.\*.meetingOptions.enabledChat | boolean | | True False |
action_result.data.\*.meetingOptions.enabledVideo | boolean | | True False |
action_result.data.\*.meetingOptions.enabledFileTransfer | boolean | | True False |
action_result.data.\*.attendeeDidJoin | boolean | | True False |
action_result.data.\*.dialInIpAddress | string | | 103.xx.xx.68 |
action_result.data.\*.excludePassword | boolean | | True False |
action_result.data.\*.hostDisplayName | string | | test user |
action_result.data.\*.meetingSeriesId | string | | testa706b64041559c664a83e6btest |
action_result.data.\*.enabledLiveStream | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledAnnotate | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledChatHost | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledViewAnyPage | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledSaveDocument | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledShareContent | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledChatPresenter | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledPrintDocument | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledRemoteControl | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledViewThumbnails | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledViewAnyDocument | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledViewParticipantList | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledChatOtherParticipants | boolean | | True False |
action_result.data.\*.attendeePrivileges.enabledContactOperatorPrivately | boolean | | True False |
action_result.data.\*.enableAutomaticLock | boolean | | True False |
action_result.data.\*.enabledJoinBeforeHost | boolean | | True False |
action_result.data.\*.joinBeforeHostMinutes | numeric | | 5 |
action_result.data.\*.allowAnyUserToBeCoHost | boolean | | True False |
action_result.data.\*.audioConnectionOptions.entryAndExitTone | string | | noTone |
action_result.data.\*.audioConnectionOptions.audioConnectionType | string | | webexAudio |
action_result.data.\*.audioConnectionOptions.enabledGlobalCallIn | boolean | | True False |
action_result.data.\*.audioConnectionOptions.enabledTollFreeCallIn | boolean | | True False |
action_result.data.\*.audioConnectionOptions.muteAttendeeUponEntry | boolean | | True False |
action_result.data.\*.audioConnectionOptions.enabledAudienceCallBack | boolean | | True False |
action_result.data.\*.audioConnectionOptions.allowAttendeeToUnmuteSelf | boolean | | True False |
action_result.data.\*.audioConnectionOptions.allowHostToUnmuteParticipants | boolean | | True False |
action_result.data.\*.enabledVisualWatermark | boolean | | True False |
action_result.data.\*.enabledBreakoutSessions | boolean | | True False |
action_result.data.\*.allowFirstUserToBeCoHost | boolean | | True False |
action_result.data.\*.enabledAutoRecordMeeting | boolean | | True False |
action_result.data.\*.allowAuthenticatedDevices | boolean | | True False |
action_result.data.\*.simultaneousInterpretation.enabled | boolean | | True False |
action_result.data.\*.phoneAndVideoSystemPassword | string | | 72959979 |
action_result.data.\*.unlockedMeetingJoinSecurity | string | | allowJoin |
action_result.data.\*.enableConnectAudioBeforeHost | boolean | | True False |
action_result.parameter.meeting_id | string | | |
action_result.parameter.current | boolean | | |
action_result.parameter.host_email | string | | |
summary.total_objects_successful | numeric | | |
action_result.status | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | |

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
