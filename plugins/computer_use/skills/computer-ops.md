---
name: computer-ops
description: Standard operating procedure for the computer MCP tool utilizing hybrid UI automation.
---

## 1. Operating Paradigm
You are interacting with a live operating system. Your primary automation strategy must be structured UI parsing rather than visual coordinate estimation.

## 2. Standard Workflow
1. **Activation**: Use `open_app` to launch or focus the target application natively. Do not use visual search for app icons.
2. **Inspection**: Use `get_ui_tree` to retrieve the active window's accessibility elements (JSON).
3. **Interaction**: Use `click_element_by_name` to interact with target elements found in the UI tree.
4. **Verification**: Always execute a subsequent `get_ui_tree` or `screenshot` to confirm state changes (e.g., modals opening, pages loading) before issuing further commands.

## 3. Fallback Protocol (Visual Mode)
Initiate visual fallback ONLY if `get_ui_tree` fails or returns empty (e.g., unsupported platforms or custom rendering engines).
1. Use `screenshot` to capture the screen state.
2. Determine the exact `[x, y]` coordinate of the target.
3. Use legacy commands: `mouse_move`, `left_click`, `right_click`, `double_click`.

## 4. Input & Navigation Rules
- **Text Entry**: Focus the target input field via `click_element_by_name` or coordinates, then use `type`.
- **Shortcuts & Keys**: Use the `key` action for standard keyboard shortcuts (e.g., `enter`, `esc`, `ctrl`, `shift`).
- **Error Recovery**: If an interaction fails, use `key` (e.g., `esc`) to dismiss blocking modals or `mouse_move` to clear hover states before retrying.
