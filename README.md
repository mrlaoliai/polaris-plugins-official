# Polaris Plugins Official

[![OpenAI Plugin](https://img.shields.io/badge/OpenAI-Plugin-brightgreen.svg)](https://platform.openai.com/docs/plugins/introduction)
[![MCP](https://img.shields.io/badge/Anthropic-MCP-blue.svg)](https://modelcontextprotocol.io)

*English documentation follows below.*

## 🇨🇳 中文介绍

**Polaris Plugins Official** 是 [Polaris AI Agent 系统](https://github.com/mrlaoliai/polaris-harness) 的官方扩展库。
本项目提供了一系列即插即用的 AI 扩展，全面兼容两大行业标准：
- **OpenAI Plugin 标准** (`ai-plugin.json` + OpenAPI Schema)
- **Anthropic MCP (Model Context Protocol) 标准**

我们的目标是让您的 AI Agent（如 Polaris, Claude Desktop, Cursor 等）轻松获得操作电脑、控制浏览器、读取知识库的强大能力。

### 插件列表

1. **[Computer Use (Rust)](plugins/computer_use)**
   - **能力**: 控制鼠标移动、点击、键盘输入、截图。
   - **底层驱动**: `enigo` 和 `xcap`
   - **特点**: 原生编译，极低延迟，跨平台。

2. **[Browser Use (Python)](plugins/browser_use)**
   - **能力**: 导航网页、点击页面元素、输入表单数据、抓取网页 DOM 树结构。
   - **底层驱动**: [browser-use](https://github.com/browser-use/browser-use) 结合 `Playwright`
   - **特点**: 专为大语言模型打造的抗干扰浏览引擎。

3. **[Knowledge Base (Go)](plugins/knowledge_base)**
   - **能力**: 扫描本地机器文件系统，读取文档内容，供大模型用于 RAG (检索增强生成)。
   - **底层驱动**: `github.com/mark3labs/mcp-go`
   - **特点**: 单体文件分发，无额外环境依赖。

### 快速开始
详见每个插件目录下的具体构建与运行说明。

---

## 🇺🇸 English

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
