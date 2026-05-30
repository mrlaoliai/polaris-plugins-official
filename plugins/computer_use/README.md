# PolarisAGI Computer Use MCP

[![npm version](https://img.shields.io/npm/v/polarisagi-computer-mcp.svg)](https://www.npmjs.com/package/polarisagi-computer-mcp)

An official Model Context Protocol (MCP) server plugin for [PolarisAGI](https://polarisagi.online/), providing cross-platform computer automation capabilities.

## Features

- **Screenshot**: Capture the current screen.
- **Mouse Control**: Move, left click, right click, double click, drag.
- **Keyboard Control**: Type text and press specific keys.

## Architecture

This plugin is written in pure TypeScript and natively invokes OS-level APIs via `@nut-tree-fork/nut-js`. It requires zero manual binary installations and supports Windows, macOS (Intel/Apple Silicon), and Linux.

## Usage with PolarisAGI

Configure your AI agent with the following MCP server setting:

```json
{
  "mcpServers": {
    "polarisagi-computer-use": {
      "command": "npx",
      "args": ["-y", "polarisagi-computer-mcp@latest"]
    }
  }
}
```

## Requirements
- Node.js v18 or newer.
