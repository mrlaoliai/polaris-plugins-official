---
name: system-info
description: Decision guide for using the system_info MCP plugin to gather environment context.
---

## 1. Architecture

The `system_info` tool serves as the primary environmental context provider for the AI agent. It allows the agent to safely detect system specs, platform, locale, and verify software installations without triggering massive, context-bloating file system scans.

| Tool | When to use | Operations |
|-------|-------------|------------|
| `get_system_context` | To understand the base environment | Returns OS, architecture, locale, timezone, and CPU cores. |
| `check_app_installed` | To verify software availability | Returns true/false and paths if the requested software is installed. |

---

## 2. Decision Tree

```
Agent needs to know about the environment?
  └─ Yes → Is it a general system property (OS, language, CPU)?
              └─ Yes → call `get_system_context`
              └─ No  → Is it about whether a specific app exists?
                          └─ Yes → call `check_app_installed` with app_name
```

---

## 3. Gathering System Context

Call `get_system_context` before running platform-specific terminal commands (like `apt-get` vs `brew`) or to decide whether to output English or Chinese based on the user's OS locale.

```jsonc
{
  "action": "get_system_context"
}
```

**Expected Result (Example)**:
```jsonc
{
  "os_name": "Darwin",
  "os_release": "25.5.0",
  "architecture": "arm64",
  "locale": "zh_CN.UTF-8",
  "timezone": "CST",
  "cpu_cores": 8,
  "disk_free_gb": 273.63
}
```

---

## 4. Checking Installed Apps

Instead of executing `find /` or scanning the entire disk, use `check_app_installed`.

```jsonc
{
  "action": "check_app_installed",
  "app_name": "WeChat"
}
```

This tool safely checks standard installation paths specific to the detected OS (`/Applications` on Mac, `C:\Program Files` on Windows) using case-insensitive substring matching.

**Expected Result**:
```jsonc
{
  "installed": true,
  "found_paths": [
    "/Applications/微信.app"
  ]
}
```

**Error Handling**: If `installed` is `false`, the agent should suggest alternative applications to the user or ask them to download the required software.
