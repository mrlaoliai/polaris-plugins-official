# PolarisAGI Knowledge Base MCP

[![npm version](https://img.shields.io/npm/v/polarisagi-knowledge-base.svg)](https://www.npmjs.com/package/polarisagi-knowledge-base)

An official Model Context Protocol (MCP) server plugin for [PolarisAGI](https://polarisagi.online/), enabling agents to securely read local files and directories.

## Features

- **List Files**: Explore directory structures.
- **Read Content**: Read the textual contents of local files for RAG or context injection.
- **Sandboxed**: Restricts file reading strictly to a permitted directory via environment variables.

## Architecture

This plugin is a zero-dependency, pure TypeScript implementation utilizing native Node.js `fs` APIs. 

## Usage with PolarisAGI

Configure your AI agent with the following MCP server setting, replacing `/your/allowed/dir` with the absolute path you wish to expose to the agent:

```json
{
  "mcpServers": {
    "polarisagi-knowledge-base": {
      "command": "npx",
      "args": ["-y", "polarisagi-knowledge-base@latest"],
      "env": {
        "POLARISAGI_KB_ALLOWED_DIR": "/your/allowed/dir"
      }
    }
  }
}
```

## Requirements
- Node.js v18 or newer.
