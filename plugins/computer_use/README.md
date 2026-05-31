# PolarisAGI Computer Use MCP

[![npm version](https://img.shields.io/npm/v/polarisagi-computer-mcp.svg)](https://www.npmjs.com/package/polarisagi-computer-mcp)

An official Model Context Protocol (MCP) server plugin for [PolarisAGI](https://polarisagi.online/), providing cross-platform computer automation capabilities.

## Features

- **Screenshot**: Capture the current screen.
- **Mouse Control**: Move, left click, right click, double click, drag.
- **Keyboard Control**: Type text and press specific keys.

## Architecture

This plugin is written in pure **Python** and natively invokes OS-level APIs via `mss` (for high-speed, direct-to-memory screen capture) and `pynput` (for cross-platform keyboard/mouse simulation). It also includes custom, locale-aware adapters (like `WeChatAdapter`) to handle complex UI layouts that standard accessibility trees miss.

## Usage with PolarisAGI

Configure your AI agent with the following MCP server setting:

```json
{
  "mcpServers": {
    "polarisagi-computer-use": {
      "command": "python",
      "args": ["/path/to/polarisagi-plugins-official/plugins/computer_use/src/main.py"]
    }
  }
}
```

## Requirements
- Python 3.10+
- `uv` (Astral's Python package manager)

**Optional Dependencies (for UI tree parsing):**
- Windows: `pywinauto` (Automatically installed via uv on Windows)
- Linux: `sudo apt install python3-pyatspi`
