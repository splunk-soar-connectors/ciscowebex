**Unreleased**
* Migrated Cisco Webex actions, OAuth handling, and custom result views to the SOAR SDK.
* Display recording details and AI meeting summaries in native SOAR tables, preserving action output fields and download URLs.
* Fix user actions failing on Webex email and role arrays, preserving their values in action results.
* Preserve existing OAuth authorization on SDK upgrade by migrating legacy tokens without overwriting SDK authentication state.
* Apply the asset's server certificate verification setting consistently to OAuth token exchange, refresh, and API requests.
* Print the SDK OAuth callback URI during Test Connectivity and document redirect URI registration for new and upgraded assets.
* Preserve Webex user status in get user results instead of replacing it with execution status or a renamed user_status field.
* Restore shared positive-integer validation for message, user, and participant limits, preserving declared defaults and rejecting zero or fractional values before API requests.
* Retain completed recording details when a later recording request fails, while returning typed outputs on full success.
* Restore the list rooms table to Room Name and ID by removing the synthetic success-status column, preserving Webex response fields.
* Return AI meeting summaries when Webex omits the recording name or returns a null name, preserving the available summary content.
* Add make request for Webex API paths with the asset's existing personal-token or OAuth authentication, returning HTTP status and response text.
