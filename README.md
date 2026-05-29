# Polaris Plugins Official

🌎 [English](README.md) | 🇨🇳 [中文](README_zh.md)

[![Website](https://img.shields.io/badge/Website-polarisagi.online-brightgreen.svg)](https://polarisagi.online/)
[![MCP](https://img.shields.io/badge/Anthropic-MCP-blue.svg)](https://modelcontextprotocol.io)
[![Codex Plugin](https://img.shields.io/badge/OpenAI-Codex_Plugin-black.svg)](https://developers.openai.com/codex/plugins)

**Polaris Plugins Official** is the official extension library for [Polaris AI Agent](https://github.com/polarisagi/polarisagi-harness), fully compatible with:

- **Anthropic MCP** (Model Context Protocol) — stdio JSON-RPC 2.0, protocol version `2024-11-05`
- **OpenAI Codex Plugin** (`.codex-plugin/plugin.json` + `.mcp.json`) — current standard

> **Note**: The legacy `ai-plugin.json` format (ChatGPT Plugin Store) was deprecated in March 2024 and is not used here.

---

## Plugins

### 1. [Computer Use (Rust)](plugins/computer_use)

**Capabilities**: Screenshot, mouse move/click/drag, keyboard input  
**Drivers**: `enigo` + `xcap`  
**Highlights**: Native compiled, ultra-low latency, cross-platform (macOS / Windows / Linux)

### 2. [Browser Use](plugins/browser_use)

**Capabilities**: Navigate URLs, click elements, fill forms, capture screenshots  
**Powered by**: [Playwright MCP](https://github.com/microsoft/playwright-mcp) (official Microsoft)  
**Highlights**: No binary to install — `npx` downloads automatically; Node.js required

### 3. [Knowledge Base (Go)](plugins/knowledge_base)

**Capabilities**: List directory contents, read file content for RAG  
**Drivers**: `github.com/mark3labs/mcp-go`  
**Highlights**: Single binary, zero extra deps; `POLARIS_KB_ALLOWED_DIR` env var for path sandboxing

---

## Installation

### Step 1: Install binaries (computer_use + knowledge_base)

```bash
curl -fsSL https://raw.githubusercontent.com/polarisagi/polarisagi-plugins-official/main/install.sh | bash
```

Or download manually from [GitHub Releases](https://github.com/polarisagi/polarisagi-plugins-official/releases).  
Available platforms: `linux/amd64`, `linux/arm64`, `darwin/amd64`, `darwin/arm64`, `windows/amd64`.

### Step 2: Configure your agent

#### Claude Code / Claude Desktop

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "polarisagi-computer-use": {
      "command": "polarisagi-computer-mcp"
    },
    "polarisagi-browser-use": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--stdio"]
    },
    "polarisagi-knowledge-base": {
      "command": "polarisagi-knowledge-base",
      "env": { "POLARIS_KB_ALLOWED_DIR": "/your/allowed/dir" }
    }
  }
}
```

#### OpenAI Codex (plugin marketplace)

```bash
codex plugin marketplace add polarisagi/polarisagi-plugins-official --sparse .agents/plugins
```

Then browse and install from the **Polaris Official Plugins** marketplace in the Codex App.

#### Polaris AI Agent (automatic)

Polaris `pkg/extensions/marketplace/` auto-discovers and installs plugins from this repo. Learn more at [polarisagi.online](https://polarisagi.online/).

---

## Repository Structure

```
plugins/
  computer_use/
    .codex-plugin/plugin.json   # Codex plugin manifest
    .mcp.json                    # MCP server config (command: polarisagi-computer-mcp)
    src/main.rs                  # Rust MCP server
    Cargo.toml
  browser_use/
    .codex-plugin/plugin.json
    .mcp.json                    # MCP server config (command: npx @playwright/mcp)
  knowledge_base/
    .codex-plugin/plugin.json
    .mcp.json                    # MCP server config (command: polarisagi-knowledge-base)
    main.go                      # Go MCP server
    go.mod

.agents/plugins/
  marketplace.json               # Codex repo-level marketplace catalog

install.sh                       # Install script (downloads binaries from GitHub Releases)
```

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

## Support & Sponsorship

If this project helps you, consider sponsoring the author to support independent development! ☕️

## About Polaris

**Polaris** is an open-source self-hosted AI Agent project.

- **Official Website**: [polarisagi.online](https://polarisagi.online/)
- **GitHub**: [github.com/polarisagi/polaris-harness](https://github.com/polarisagi/polarisagi-harness)
- **Contact**: polarisagi.online@gmail.com

## Author

**mrlaoliai** — Independent AI Developer

Find me on:
- **Xiaohongshu (小红书)**: mrlaoliai
- **Douyin (抖音)**: mrlaoliai
- **TikTok**: mrlaoliai
- **X (Twitter)**: mrlaoliai

Contact: polarisagi.online@gmail.com
