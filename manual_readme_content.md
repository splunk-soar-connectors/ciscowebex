## Authentication

This app supports two types of authentication:

### 1. Personal Access Token

- Use your **[Webex Personal Access Token](https://developer.webex.com/docs/getting-your-personal-access-token)**.
- Personal access tokens are valid for **12 hours** after logging into the Developer Portal.

### 2. OAuth

- Use your **Client ID**, **Client Secret**, and required **Scopes**.

#### Steps:

1. **Create a Webex App** at [https://developer.webex.com/my-apps](https://developer.webex.com/my-apps)
1. Choose the app type: **Integration**
1. Provide default required scopes to run all actions: `spark:people_read spark:rooms_read spark:messages_write spark:rooms_write spark:memberships_write spark:messages_read meeting:participants_read meeting:schedules_read meeting:recordings_read meeting:schedules_write`.
1. Collect:
   - **Client ID**
   - **Client Secret**
   - Required **Scopes**
1. In Splunk SOAR, create a new asset and provide credentials as per the method selected.
1. Run **Test Connectivity** and copy the URI printed after **Register this OAuth redirect URI in your Webex integration:**.
1. In the Webex integration settings, register that exact value as a **Redirect URI**. The SDK callback has the form `https://<soar-host>:<webhook-port>/webhook/<app-directory>/<asset-id>/oauth_callback`. Use the generated URI, including its port and asset ID, rather than constructing it manually.
1. Run **Test Connectivity** again and open the authorization URL it prints to complete authorization. If the earlier attempt timed out while you updated Webex, use the new attempt's authorization URL.

#### Upgrading from the legacy connector

The SDK uses a different OAuth callback route from the legacy connector. Update the Webex integration's registered Redirect URI to the exact URI printed by the upgraded asset's **Test Connectivity** before authorizing it again. Replace the old `/rest/handler/.../result` registration with the generated `/webhook/.../oauth_callback` URI; changing only the final path component is insufficient.

Existing OAuth tokens are migrated automatically when available, so normal actions do not require reauthorization solely because the callback changed. The new registered URI is required when you next run **Test Connectivity** or reauthorize the asset. Personal Access Token authentication does not use this callback.

- Webex Developer Portal: [https://developer.webex.com](https://developer.webex.com)
- Webex Scopes: [https://developer.webex.com/docs/integrations](https://developer.webex.com/docs/integrations)

**OAuth Required Scopes per Action are listed below.**

## Supported Actions and Required Scopes

| Action | Description | Required Scopes |
|-----------------------------|-------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| **Test Connectivity** | Verifies the app configuration and connectivity to the Webex API | `spark:people_read`, `spark:rooms_read`, `spark:messages_write`, `spark:rooms_write`, `spark:memberships_write`, `spark:messages_read`, `meeting:participants_read`, `meeting:schedules_read`, `meeting:recordings_read`, and `meeting:schedules_write` |
| **List Rooms** | List Webex rooms (spaces) | `spark:rooms_read`|
| **Get User** | Get user ID from email address | `spark:people_read`, for admin (`spark-admin:people_read`) |
| **Send Message** | Send a message to a user or room | `spark:messages_write`, `spark:rooms_read` (if room name lookup is used) |
| **Create a Room** | Create a new Webex room (space) | `spark:rooms_write` |
| **Add People** | Add a person to a Webex room (as member or moderator) | `spark:memberships_write`, for admin (`spark-admin:people_read`)|
| **Schedule Meeting** | Schedule a Webex meeting with details and invitees | `meeting:schedules_write`, for admin(`meeting:admin_schedule_write`) |
| **Retrieve Meeting Participants** | Retrieve participants in an in-progress or ended Webex meeting | `meeting:participants_read`, for admin(`meeting:admin_participants_read`) |
| **List Messages** | Retrieve a list of messages from a Webex room or 1:1 conversation | `spark:messages_read`, for admin (`spark-admin:messages_read`) |
| **Get Message Details** | Retrieve the details of a specific Webex message by message ID | `spark:messages_read`, for admin (`spark-admin:messages_read`) |
| **Get Meeting Details** | Retrieve details of a specific meeting using meeting ID or meeting number | `meeting:schedules_read`, for admin (`meeting:admin_schedule_read`) |
| **List Users** | List users in your Webex org using filters like email, name, ID, etc. | `spark:people_read`, for admin (`spark-admin:people_read`) to retrieve other user details |
| **Get Recording Details** | Retrieve details of a Webex meeting recording using its recording ID | `meeting:recordings_read`, for admin (`spark-admin:recordings_read`) |
| **AI Meeting Summary** | Retrieve AI-Generated meeting summary and actions items using its recording ID and site url | `meeting:recordings_read`, for admin (`spark-admin:recordings_read`) |
| **Make Request** | Send a request to a Webex API path using the asset's authentication | Scopes required by the selected endpoint |

### Make Request

Use a path relative to `https://webexapis.com/v1`, such as `/rooms` or `/people`.
Do not include a hostname or repeat the `/v1` prefix. The action uses the same
Personal Access Token or OAuth authentication and token refresh as other actions.

- `http_method` defaults to `GET` and supports `GET`, `POST`, `PUT`, `DELETE`,
  `PATCH`, `HEAD`, and `OPTIONS`.
- `query_parameters` accepts a JSON object or a query string, including repeated
  keys. Parameters supplied here override matching keys in the endpoint query.
- `headers` accepts a JSON object of string values. Header names are
  case-insensitive. Authentication comes from the asset.
- `body` is sent as text. With the default `Content-Type: application/json`, it
  must be valid JSON; change Content-Type to send another text format.
- `timeout` is a positive number of whole seconds (default 30).
  `verify_ssl`, when omitted, uses the asset's certificate verification setting.
  Both settings apply to API and OAuth token requests.

The action returns `status_code` and `response_body` as response text, including
non-JSON, empty, and HTTP error responses. Inspect `status_code` to determine
whether Webex accepted the request. Invalid inputs, connection failures, and
token acquisition or refresh errors fail the action. The action makes one resource request, apart from the
existing OAuth retry after a rejected token; it does not paginate results.

______________________________________________________________________

### If You Have a Free Webex Account

Some features and settings are **not available** for free accounts:

- **Create Room:** You cannot use `isAnnouncementOnly`, `isPublic`, `isLocked`, or `classificationId`.
- **Add People:** You can’t set `isModerator`.
- **List Users:** You may not be able to use `roles` or `orgId`.
- **Schedule Meeting:** The following won’t work: `host`, `adhoc`, `roomId`, `enabledJoinBeforeHost`, `joinBeforeHostMinutes`, `recording`, `publicMeeting` (needs admin), and `sessionTypeId` (webinars only).
- **AI Meeting Summary:** You can't perform this action.

If you want these features, you will need to upgrade to a paid [Webex plan](https://pricing.webex.com/us/en/hybrid-work/meetings/).
