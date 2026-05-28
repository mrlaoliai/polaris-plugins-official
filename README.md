# Polaris Plugins Official

🌎 [English](README.md) | 🇨🇳 [中文](README_zh.md)

[![MCP](https://img.shields.io/badge/Anthropic-MCP-blue.svg)](https://modelcontextprotocol.io)
[![Codex Plugin](https://img.shields.io/badge/OpenAI-Codex_Plugin-black.svg)](https://developers.openai.com/codex/plugins)

**Polaris Plugins Official** is the official extension library for [Polaris AI Agent](https://github.com/polarisagi/polaris-harness), fully compatible with:

- **Anthropic MCP** (Model Context Protocol) — stdio JSON-RPC 2.0, protocol version `2024-11-05`
- **OpenAI Codex Plugin** (`.codex-plugin/plugin.json` + `.mcp.json`) — current standard

> **Note**: The legacy `ai-plugin.json` format (ChatGPT Plugin Store) was deprecated in March 2024 and is not used here.

---

## Plugins

### 1. [Computer Use (Rust)](plugins/computer_use)

**Capabilities**: Screenshot, mouse move/click/drag, keyboard input  
**Drivers**: `enigo` + `xcap`  
**Highlights**: Native compiled, ultra-low latency, cross-platform (macOS / Windows / Linux)

Build:
```bash
cd plugins/computer_use
cargo build --release
```

### 2. [Browser Use (Python)](plugins/browser_use)

**Capabilities**: Navigate URLs, click elements, fill forms, capture screenshots  
**Drivers**: [browser-use](https://github.com/browser-use/browser-use) + Playwright  
**Highlights**: LLM-native browser automation engine

Install deps:
```bash
cd plugins/browser_use
pip install -r requirements.txt
playwright install chromium
```

### 3. [Knowledge Base (Go)](plugins/knowledge_base)

**Capabilities**: List directory contents, read file content for RAG  
**Drivers**: `github.com/mark3labs/mcp-go`  
**Highlights**: Single binary, zero extra deps; `POLARIS_KB_ALLOWED_DIR` env var for path sandboxing

Build:
```bash
cd plugins/knowledge_base
go build -o knowledge_base .
```

---

## Installation

### Option 1: Claude Code / Claude Desktop (direct MCP)

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "polaris-computer-use": {
      "command": "/path/to/plugins/computer_use/target/release/polaris-computer-mcp"
    },
    "polaris-browser-use": {
      "command": "python3",
      "args": ["/path/to/plugins/browser_use/server.py"]
    },
    "polaris-knowledge-base": {
      "command": "/path/to/plugins/knowledge_base/knowledge_base",
      "env": { "POLARIS_KB_ALLOWED_DIR": "/your/allowed/dir" }
    }
  }
}
```

### Option 2: OpenAI Codex (plugin marketplace)

Add this repo as a Codex marketplace:

```bash
codex plugin marketplace add polarisagi/polarisagi-plugins-official --sparse .agents/plugins
```

Then browse and install from the **Polaris Official Plugins** marketplace in the Codex App.

### Option 3: Polaris AI Agent (automatic)

Polaris `pkg/extensions/marketplace/` auto-discovers and installs plugins from this repo.

---

## Repository Structure

```
plugins/
  computer_use/
    .codex-plugin/plugin.json   # Codex plugin manifest
    .mcp.json                    # MCP server config
    src/main.rs                  # Rust MCP server
    Cargo.toml
  browser_use/
    .codex-plugin/plugin.json
    .mcp.json
    server.py                    # Python MCP server
    requirements.txt
  knowledge_base/
    .codex-plugin/plugin.json
    .mcp.json
    main.go                      # Go MCP server
    go.mod

.agents/plugins/
  marketplace.json               # Codex repo-level marketplace catalog
```

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)** — see the [LICENSE](LICENSE) file for details.

### Commercial Licensing (Dual License)

For enterprises or individuals who wish to use, integrate, or distribute this project in closed-source commercial products, a commercial license is required. Please contact `polarisagi.online@gmail.com` to purchase a commercial license.

## Support & Sponsorship

If this project helps you, consider sponsoring the author to support independent development! ☕️

## Author

- **polarisagi** · polarisagi.online@gmail.com
