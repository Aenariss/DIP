## addons/firefox_resource_logger

Contains source code of the custom Firefox logging extension.

#### Folder contents:

Files:
- ``./background.js`` -- Background script to add ``onSendHeaders()`` listener that logs succesfull requests
- ``./content.js`` -- Content script to listen for messages from background that contain sucesfull requests. Saves the requests in an array to be later retrieved by the Selenium-driven Firefox browser which visits the test server.
- ``./manifest.json`` -- Manifest file which defines metadata and permissions
