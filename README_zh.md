# Polaris Plugins Official

🌎 [English](README.md) | 🇨🇳 [中文](README_zh.md)

[![OpenAI Plugin](https://img.shields.io/badge/OpenAI-Plugin-brightgreen.svg)](https://platform.openai.com/docs/plugins/introduction)
[![MCP](https://img.shields.io/badge/Anthropic-MCP-blue.svg)](https://modelcontextprotocol.io)

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

## 项目说明
本项目是一个开源的扩展框架，旨在为各种 AI Agent 提供标准化的能力支持。通过这些插件，AI 系统能够更自然地与本地硬件、网络资源和文件系统进行交互。我们开发并维护此项目，以降低 AI Agent 的集成门槛。

## 作者
- **作者 ID**: mrlaoliai
- **邮箱**: mrlaoliai@gmail.com

## 开源协议
本项目采用 MIT 开源协议 - 详情请查看 [LICENSE](LICENSE) 文件。
