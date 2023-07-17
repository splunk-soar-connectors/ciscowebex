**Unreleased**
* Added new parameter 'is_markdown' in the 'send message' action to support markdown language
* Added new configuration parameter 'Scopes' for passing required and additional scopes 
* Added encryption for the sensitive values stored in the state file
* Updated minimum required scopes for running all the actions of the connector (Please refer the documentation for more details) 
* Removing django and requests in order to use platform packages instead [PAPP-31087, PAPP-31082, PAPP-30822]
