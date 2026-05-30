---
name: browser-ops
description: Use the browser MCP tool to interact with the web safely and effectively.
---

When interacting with the browser, you MUST use the provided DOM extraction tools instead of blindly guessing coordinates or taking raw screenshots. Follow these strict rules:

1. **Get the Interactive DOM:** Before clicking or filling anything, ALWAYS call `get_interactive_dom` to get a list of all visible interactive elements (buttons, links, inputs).
2. **Use Polaris ID:** Each element returned by `get_interactive_dom` will have a unique `polaris-id`. Use this ID with the `action_by_id` tool to click, hover, or fill. **NEVER attempt to click using raw x, y coordinates.**
3. **Wait for Loading:** The `navigate` tool automatically waits for the page to load. Do not rush to interact if the network is busy.
4. **Scroll for Visibility:** If a target element is not found within the current viewport (not returned in `get_interactive_dom`), use `scroll_page` to scroll down and call `get_interactive_dom` again.
5. **Handle Pop-ups/Overlays:** If encountering cookie consent banners, ads, or overlays blocking target elements, identify their `polaris-id` and close/accept them first.
6. **State Verification:** After submitting forms or clicking crucial links, you can re-fetch `get_interactive_dom` to verify the new page state.
7. **Sensitive Actions:** For any sensitive actions (like form submissions or payments), ask the user for permission first before executing `action_by_id`.
