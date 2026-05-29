# Polaris Plugins Official

🌎 [English](README.md) | 🇨🇳 [中文](README_zh.md)

[![Website](https://img.shields.io/badge/官网-polarisagi.online-brightgreen.svg)](https://polarisagi.online/)
[![MCP](https://img.shields.io/badge/Anthropic-MCP-blue.svg)](https://modelcontextprotocol.io)
[![Codex Plugin](https://img.shields.io/badge/OpenAI-Codex_Plugin-black.svg)](https://developers.openai.com/codex/plugins)

**Polaris Plugins Official** 是 [Polaris AI Agent](https://github.com/polarisagi/polarisagi-harness) 的官方扩展库，同时完全兼容以下行业标准：

- **Anthropic MCP**（Model Context Protocol）—— stdio JSON-RPC 2.0，协议版本 `2024-11-05`
- **OpenAI Codex Plugin**（`.codex-plugin/plugin.json` + `.mcp.json`）—— 当前现行标准

> **注**：旧版 `ai-plugin.json`（ChatGPT Plugin Store 格式）已于 2024 年 3 月废弃，本项目不再使用。

---

## 插件列表

### 1. [Computer Use (Rust)](plugins/computer_use)

**能力**：截图、鼠标移动/点击/拖拽、键盘输入  
**底层驱动**：`enigo` + `xcap`  
**特点**：原生编译，极低延迟，跨平台（macOS / Windows / Linux）

### 2. [Browser Use](plugins/browser_use)

**能力**：导航网页、点击元素、填写表单、截图  
**底层驱动**：[Playwright MCP](https://github.com/microsoft/playwright-mcp)（微软官方）  
**特点**：无需安装二进制，`npx` 自动下载；需要 Node.js

### 3. [Knowledge Base (Go)](plugins/knowledge_base)

**能力**：扫描本地文件系统、读取文档内容，用于 RAG 检索增强生成  
**底层驱动**：`github.com/mark3labs/mcp-go`  
**特点**：单体二进制，零额外依赖；支持 `POLARIS_KB_ALLOWED_DIR` 路径白名单

---

## 安装方式

### 第一步：安装二进制（computer_use + knowledge_base）

```bash
curl -fsSL https://raw.githubusercontent.com/polarisagi/polarisagi-plugins-official/main/install.sh | bash
```

或从 [GitHub Releases](https://github.com/polarisagi/polarisagi-plugins-official/releases) 手动下载。  
支持平台：`linux/amd64`、`linux/arm64`、`darwin/amd64`、`darwin/arm64`、`windows/amd64`。

### 第二步：配置你的 Agent

#### Claude Code / Claude Desktop

在 `~/.claude.json` 中添加：

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

#### OpenAI Codex（Plugin 市场安装）

```bash
codex plugin marketplace add polarisagi/polarisagi-plugins-official --sparse .agents/plugins
```

然后在 Codex App 中从 **Polaris Official Plugins** 市场浏览并安装。

#### Polaris AI Agent（自动）

Polaris 的 `pkg/extensions/marketplace/` 模块会自动发现并安装本仓库的插件，无需手动配置。了解更多请访问 [polarisagi.online](https://polarisagi.online/)。

---

## 项目结构

```
plugins/
  computer_use/
    .codex-plugin/plugin.json   # Codex 插件清单
    .mcp.json                    # MCP 配置（command: polarisagi-computer-mcp）
    src/main.rs                  # Rust MCP 服务器实现
    Cargo.toml
  browser_use/
    .codex-plugin/plugin.json
    .mcp.json                    # MCP 配置（command: npx @playwright/mcp）
  knowledge_base/
    .codex-plugin/plugin.json
    .mcp.json                    # MCP 配置（command: polarisagi-knowledge-base）
    main.go                      # Go MCP 服务器实现
    go.mod

.agents/plugins/
  marketplace.json               # Codex repo 级市场目录

install.sh                       # 安装脚本（从 GitHub Releases 下载二进制）
```

## 开源协议

本项目采用 **MIT License** 协议开源 — 详见 [LICENSE](LICENSE) 文件。

## 赞助与支持

如果您觉得这个项目对您有帮助，欢迎赞助作者，支持个人独立开发者的持续创作！☕️

## 关于 Polaris

**Polaris** 是一个开源自托管 AI Agent 项目。

- **官方网站**：[polarisagi.online](https://polarisagi.online/)
- **GitHub**：[github.com/polarisagi/polaris-harness](https://github.com/polarisagi/polarisagi-harness)
- **联系邮箱**：polarisagi.online@gmail.com

## 作者

**mrlaoliai** — 独立 AI 开发者

关注我：
- **小红书**：mrlaoliai
- **抖音**：mrlaoliai
- **TikTok**：mrlaoliai
- **X (Twitter)**：mrlaoliai

联系邮箱：polarisagi.online@gmail.com
