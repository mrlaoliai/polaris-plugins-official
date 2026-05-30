# PolarisAGI Plugins Official

🌎 [English](README.md) | 🇨🇳 [中文](README_zh.md)

[![Website](https://img.shields.io/badge/Website-polarisagi.online-brightgreen.svg)](https://polarisagi.online/)
[![MCP](https://img.shields.io/badge/Anthropic-MCP-blue.svg)](https://modelcontextprotocol.io)
[![Codex Plugin](https://img.shields.io/badge/OpenAI-Codex_Plugin-black.svg)](https://developers.openai.com/codex/plugins)

**PolarisAGI Plugins Official** is the official extension library for [PolarisAGI AI Agent](https://github.com/polarisagi/polarisagi-harness), fully compatible with:

- **Anthropic MCP** (Model Context Protocol) — stdio JSON-RPC 2.0, protocol version `2024-11-05`
- **OpenAI Codex Plugin** (`.codex-plugin/plugin.json` + `.mcp.json`) — current standard

> **Note**: The legacy `ai-plugin.json` format (ChatGPT Plugin Store) was deprecated in March 2024 and is not used here.

---

## Plugins

### 1. [Computer Use (TypeScript)](plugins/computer_use)

**Capabilities**: Screenshot, mouse move/click/drag, keyboard input  
**Drivers**: `@nut-tree-fork/nut-js`  
**Highlights**: Pure TypeScript, natively calls OS APIs, cross-platform (macOS / Windows / Linux)

### 2. [Browser Use](plugins/browser_use)

**Capabilities**: Navigate URLs, click elements, fill forms, capture screenshots  
**Powered by**: [Playwright MCP](https://github.com/microsoft/playwright-mcp) (official Microsoft)  
**Highlights**: No binary to install — `npx` downloads automatically; Node.js required

### 3. [Knowledge Base (TypeScript)](plugins/knowledge_base)

**Capabilities**: List directory contents, read file content for RAG  
**Drivers**: Native Node.js `fs` module  
**Highlights**: Pure TypeScript, zero external dependencies; `POLARISAGI_KB_ALLOWED_DIR` env var for path sandboxing

---

## Installation

### Step 1: Prerequisites

Ensure you have **Node.js** (v18 or newer) installed on your system. No manual binary downloads are required!

### Step 2: Configure your agent

#### Claude Code / Claude Desktop

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "polarisagi-computer-use": {
      "command": "npx",
      "args": ["-y", "polarisagi-computer-mcp@latest"]
    },
    "polarisagi-browser-use": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--stdio"]
    },
    "polarisagi-knowledge-base": {
      "command": "npx",
      "args": ["-y", "polarisagi-knowledge-base@latest"],
      "env": { "POLARISAGI_KB_ALLOWED_DIR": "/your/allowed/dir" }
    }
  }
}
```

#### OpenAI Codex (plugin marketplace)

```bash
codex plugin marketplace add polarisagi/polarisagi-plugins-official --sparse .agents/plugins
```

Then browse and install from the **PolarisAGI Official Plugins** marketplace in the Codex App.

#### PolarisAGI AI Agent (automatic)

PolarisAGI `pkg/extensions/marketplace/` auto-discovers and installs plugins from this repo. Learn more at [polarisagi.online](https://polarisagi.online/).

---

## Repository Structure

```
plugins/
  computer_use/
    .codex-plugin/plugin.json   # Codex plugin manifest
    .mcp.json                    # MCP server config (command: npx)
    src/index.ts                 # TypeScript MCP server
    package.json
  browser_use/
    .codex-plugin/plugin.json
    .mcp.json                    # MCP server config (command: npx @playwright/mcp)
  knowledge_base/
    .codex-plugin/plugin.json
    .mcp.json                    # MCP server config (command: npx)
    src/index.ts                 # TypeScript MCP server
    package.json

.agents/plugins/
  marketplace.json               # Codex repo-level marketplace catalog
```

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

## Support & Sponsorship

If this project helps you, consider sponsoring the author to support independent development! ☕️

## About PolarisAGI

**PolarisAGI** is an open-source self-hosted AI Agent project.

- **Official Website**: [polarisagi.online](https://polarisagi.online/)
- **GitHub**: [github.com/polarisagi/polarisagi-harness](https://github.com/polarisagi/polarisagi-harness)
- **Contact**: polarisagi.online@gmail.com

## Author

**mrlaoliai** — Independent AI Developer

Find me on:
- **Xiaohongshu (小红书)**: mrlaoliai
- **Douyin (抖音)**: mrlaoliai
- **TikTok**: mrlaoliai
- **X (Twitter)**: mrlaoliai

Contact: polarisagi.online@gmail.com
