# Polaris Plugins Official

🌎 [English](README.md) | 🇨🇳 [中文](README_zh.md)

[![MCP](https://img.shields.io/badge/Anthropic-MCP-blue.svg)](https://modelcontextprotocol.io)
[![Codex Plugin](https://img.shields.io/badge/OpenAI-Codex_Plugin-black.svg)](https://developers.openai.com/codex/plugins)

**Polaris Plugins Official** 是 [Polaris AI Agent](https://github.com/polarisagi/polaris-harness) 的官方扩展库，同时完全兼容以下行业标准：

- **Anthropic MCP**（Model Context Protocol）—— stdio JSON-RPC 2.0，协议版本 `2024-11-05`
- **OpenAI Codex Plugin**（`.codex-plugin/plugin.json` + `.mcp.json`）—— 当前现行标准

> **注**：旧版 `ai-plugin.json`（ChatGPT Plugin Store 格式）已于 2024 年 3 月废弃，本项目不再使用。

---

## 插件列表

### 1. [Computer Use (Rust)](plugins/computer_use)

**能力**：截图、鼠标移动/点击/拖拽、键盘输入  
**底层驱动**：`enigo` + `xcap`  
**特点**：原生编译，极低延迟，跨平台（macOS / Windows / Linux）

构建：
```bash
cd plugins/computer_use
cargo build --release
```

### 2. [Browser Use (Python)](plugins/browser_use)

**能力**：导航网页、点击元素、填写表单、截图  
**底层驱动**：[browser-use](https://github.com/browser-use/browser-use) + Playwright  
**特点**：专为 LLM 打造的抗干扰浏览引擎

安装依赖：
```bash
cd plugins/browser_use
pip install -r requirements.txt
playwright install chromium
```

### 3. [Knowledge Base (Go)](plugins/knowledge_base)

**能力**：扫描本地文件系统、读取文档内容，用于 RAG 检索增强生成  
**底层驱动**：`github.com/mark3labs/mcp-go`  
**特点**：单体文件，零额外依赖；支持 `POLARIS_KB_ALLOWED_DIR` 路径白名单

构建：
```bash
cd plugins/knowledge_base
go build -o knowledge_base .
```

---

## 安装方式

### 方式一：Claude Code / Claude Desktop（MCP 直连）

在 `~/.claude.json` 中添加：

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

### 方式二：OpenAI Codex（Plugin 市场安装）

在 Codex CLI 中添加本仓库作为插件市场：

```bash
codex plugin marketplace add polarisagi/polarisagi-plugins-official --sparse .agents/plugins
```

然后在 Codex App 中从 **Polaris Official Plugins** 市场浏览并安装。

### 方式三：Polaris AI Agent（自动）

Polaris 的 `pkg/extensions/marketplace/` 模块会自动发现并安装本仓库的插件，无需手动配置。

---

## 项目结构

```
plugins/
  computer_use/
    .codex-plugin/plugin.json   # Codex 插件清单
    .mcp.json                    # MCP 服务器配置
    src/main.rs                  # Rust MCP 服务器实现
    Cargo.toml
  browser_use/
    .codex-plugin/plugin.json
    .mcp.json
    server.py                    # Python MCP 服务器实现
    requirements.txt
  knowledge_base/
    .codex-plugin/plugin.json
    .mcp.json
    main.go                      # Go MCP 服务器实现
    go.mod

.agents/plugins/
  marketplace.json               # Codex repo 级市场目录
```

## 开源协议

本项目采用 **GNU Affero General Public License v3.0 (AGPLv3)** 协议开源 — 详见 [LICENSE](LICENSE) 文件。

### 商业授权 (Dual License)

如果您希望在闭源商业产品中使用、集成或分发本项目的代码，您需要购买商业授权。请联系 `polarisagi.online@gmail.com` 获取商业授权许可。

## 赞助与支持

如果您觉得这个项目对您有帮助，欢迎赞助作者，支持个人独立开发者的持续创作！☕️

## 作者

- **polarisagi** · polarisagi.online@gmail.com
