/**
* Content script exposing observed resources.
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

// Only do anything if it's on the test page
const targetPage = ":5000";

// Inject a script into the page to create a globally accessible array
const script = document.createElement("script");
script.textContent = `
    window.observedResources = [];
    window.addEventListener("newResource", (event) => {
        window.observedResources.push(event.detail);
    });
`;
document.documentElement.appendChild(script);

// Check it's the test page
if (window.location.href.includes(targetPage)) {
    // Notify the background script to start tracking this tab
    browser.runtime.sendMessage({ action: "startTracking" });

    // Listen for messages from background script
    browser.runtime.onMessage.addListener((message) => {
        if (message.url) {
            const event = new CustomEvent("newResource", { detail: message.url });
            window.dispatchEvent(event);
            console.log("Observed URL:", message.url);
        }
    });
}
