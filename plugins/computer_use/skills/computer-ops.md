---
name: computer-ops
description: Use the computer MCP tool to interact with desktop applications and the OS.
---

You have permission to operate a real computer. Please strictly follow these visual recognition and operation guidelines:

1. **Visual Feedback Loop**: Before executing any click (`left_click`) or input (`type`/`paste`), you MUST call `screenshot` to get the current screen state. Analyze the screenshot carefully to find the absolute coordinates `[x, y]` of the target UI element before clicking.
2. **Handling UI States / System Latency**: UI elements may have loading animations or network delays. After interacting with an element (e.g. clicking 'search'), do not assume the action completed instantly. Leave brief wait times between consecutive actions, and you MUST call `screenshot` again to verify the new UI state (like checking if a dropdown menu appeared) before proceeding.
3. **Text Input Rules**: When inputting Chinese characters or long text, you MUST prioritize the `paste` action. This bypasses input method editor (IME) interference and prevents text truncation. Only use `type` or `key` for pure English characters or shortcuts.
4. **Error Recovery**: If the screenshot does not match your expectations (e.g. click failed or text was typed in the wrong place), analyze the screen, use `mouse_move` to move the focus away, or send `key: escape` to cancel the current state, and retry.
5. **Safety and Destructive Operations**: Be extremely cautious with terminal commands or file modifications. If you encounter an unexpected state, immediately stop and alert the user. For destructive operations, ask for explicit human confirmation.
6. **Prioritize Shortcuts**: When performing standard actions like copy, paste, select all, or save, prefer using system keyboard shortcuts (e.g., Cmd+C/V) over mouse clicks, as they are generally more reliable.
7. **Manage Focus/Windows**: Before interacting, ensure the target application is in the foreground and not blocked by other windows. Click to activate it if necessary.
