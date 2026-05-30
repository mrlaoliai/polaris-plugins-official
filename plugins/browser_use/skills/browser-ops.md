---
name: browser-ops
description: Use the browser MCP tool to interact with the web safely and effectively.
---

When interacting with the browser:
1. Always wait for the page to finish loading before interacting with elements.
2. Use precise coordinates or reliable accessibility IDs when clicking.
3. If an action fails, retry once before asking the user for help.
4. For any sensitive actions (like form submissions or payments), ask the user for permission first.
5. Handle Pop-ups/Overlays: If encountering cookie consent banners, ads, or overlays blocking target elements, attempt to close or accept them first.
6. Scroll for Visibility: If a target element is not found within the current viewport, attempt scrolling down the page before giving up.
7. State Verification: After submitting forms or clicking crucial links, verify the URL or look for expected page state changes to confirm the action succeeded.
