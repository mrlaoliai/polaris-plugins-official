# Polaris Plugins Official

🌎 [English](README.md) | 🇨🇳 [中文](README_zh.md)

[![OpenAI Plugin](https://img.shields.io/badge/OpenAI-Plugin-brightgreen.svg)](https://platform.openai.com/docs/plugins/introduction)
[![MCP](https://img.shields.io/badge/Anthropic-MCP-blue.svg)](https://modelcontextprotocol.io)

**Polaris Plugins Official** is the official extension repository for the [Polaris AI Agent System](https://github.com/mrlaoliai/polaris-harness).
This project provides a suite of plug-and-play AI extensions fully compliant with two major industry standards:
- **OpenAI Plugin Standard** (`ai-plugin.json` + OpenAPI Schema)
- **Anthropic MCP (Model Context Protocol) Standard**

Our goal is to effortlessly grant your AI Agent (such as Polaris, Claude Desktop, Cursor, etc.) the powerful abilities to control computers, operate browsers, and read knowledge bases.

### Plugin Directory

1. **[Computer Use (Rust)](plugins/computer_use)**
   - **Capabilities**: Mouse movement, clicks, keyboard typing, and taking screenshots.
   - **Driver**: `enigo` and `xcap`
   - **Highlights**: Natively compiled, ultra-low latency, cross-platform.

2. **[Browser Use (Python)](plugins/browser_use)**
   - **Capabilities**: Navigate web pages, click elements, fill forms, and extract DOM trees.
   - **Driver**: [browser-use](https://github.com/browser-use/browser-use) with `Playwright`
   - **Highlights**: Built specifically for Large Language Models to interact with the web reliably.

3. **[Knowledge Base (Go)](plugins/knowledge_base)**
   - **Capabilities**: Scan local file systems and read document contents for LLM RAG (Retrieval-Augmented Generation).
   - **Driver**: `github.com/mark3labs/mcp-go`
   - **Highlights**: Single binary distribution, no external dependencies.

### Quick Start
See the specific build and run instructions within each plugin's directory.

## About the Project
This project is an open-source extension framework designed to provide various standard capabilities for AI Agents. Through these plugins, AI systems can interact with local hardware, web resources, and file systems. It is developed and maintained to lower the barrier for AI Agent integrations.

## Author
- **ID**: mrlaoliai
- **Email**: mrlaoliai@gmail.com

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
