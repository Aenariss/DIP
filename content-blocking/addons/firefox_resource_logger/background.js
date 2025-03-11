/**
* Background script logging requested resources.
* Copyright (C) 2025 Vojtěch Fiala
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License along with this program.
* If not, see <https://www.gnu.org/licenses/>.
*/

let trackedTabId = null;

// Only do anything if a message from content script on a testpage came
browser.runtime.onMessage.addListener((message, sender) => {
    if (message.action === "startTracking") {
        trackedTabId = sender.tab.id;
    }
});

/* Adblockers should block at onBeforeRequest. onSendHeaders is two levels after
 * so if the request got here, it was not blocked. After this point, the request
 * can still be blocked because of network error (because of firewall rules :wink:)
 * which perfectly suits my purpose.
 */
browser.webRequest.onSendHeaders.addListener(
    (details) => {
        // Check it's the test page
        if (details.tabId === trackedTabId) {

            // Send message to content script
            /*
            browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
                if (tabs.length > 0) {
                    browser.tabs.sendMessage(tabs[0].id, { url: details.url })
                }
            });
            */
            browser.tabs.sendMessage(trackedTabId, { url: details.url })
        }
    },
    { urls: ["<all_urls>"] }
);
