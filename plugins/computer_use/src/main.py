#!/usr/bin/env python3
"""
PolarisAGI Computer Use MCP Server — Universal Desktop Automation
Supports: macOS, Windows, Linux

Architecture:
  utils.py          — shared keyboard / mouse / accessibility helpers
  adapters/base.py  — BaseAdapter: generic search-result selection
  adapters/chat/    — app-specific adapters (only when generic is not enough)
  adapters/registry — maps bundle IDs to adapter classes
  profiles/*.json   — per-app config (shortcuts, locale-aware labels, etc.)
  main.py           — MCP server + action handlers (zero app-specific logic)

Adding a new app: create profiles/<app>.json (+ an adapter only if needed).
main.py never changes for new app support.
"""
import sys
import json
import base64
import glob
import locale
import mss
import os
import platform
import subprocess
import time

import utils
from utils import mouse, Button
from adapters.registry import get_adapter

# ---------------------------------------------------------------------------
# Profile loader
# ---------------------------------------------------------------------------

_PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")


def _load_profiles() -> dict:
    profiles: dict = {}
    for path in sorted(glob.glob(os.path.join(_PROFILES_DIR, "*.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                p = json.load(f)
        except Exception:
            continue
        keys = set()
        for field in ("app_name", "open_name"):
            v = p.get(field, "")
            if v:
                keys.add(v.lower())
        for alias in p.get("aliases", []):
            if alias:
                keys.add(alias.lower())
        for k in keys:
            profiles[k] = p
    return profiles


APP_PROFILES: dict = _load_profiles()

# ---------------------------------------------------------------------------
# Locale detection + field resolver
# ---------------------------------------------------------------------------

SYSTEM_LOCALE: str = utils.detect_locale()


def _resolve(value, loc: str = None):
    """Resolve a profile field that may be a locale map {"zh": …, "en": …}."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        l = loc or SYSTEM_LOCALE
        return value.get(l) or value.get("en") or next(iter(value.values()), None)
    return str(value)


# ---------------------------------------------------------------------------
# Action handlers
# ---------------------------------------------------------------------------

def handle_open_app(args):
    app_name  = args.get("app_name", "")
    open_name = args.get("open_name", "") or app_name
    bundle_id = args.get("bundle_id", "")
    if not app_name and not open_name:
        raise Exception("Missing app_name")

    plat = platform.system()
    if plat == "Darwin":
        launched = False
        if bundle_id:
            r = subprocess.run(["open", "-b", bundle_id], capture_output=True)
            if r.returncode == 0:
                launched = True
        if not launched and open_name:
            r = subprocess.run(
                ["osascript", "-e", f'tell application "{open_name}" to activate'],
                capture_output=True,
            )
            if r.returncode == 0:
                launched = True
        if not launched:
            subprocess.run(["open", "-a", open_name], check=True)
        subprocess.run(
            ["osascript", "-e", f'tell application "{open_name or app_name}" to activate'],
            capture_output=True,
        )
    elif plat == "Windows":
        subprocess.run(["cmd", "/c", "start", "", open_name], shell=True)
    else:
        subprocess.Popen(["xdg-open", open_name])

    return [{"type": "text", "text": f"Opened {open_name or app_name}"}]


def handle_get_ui_tree(args):
    plat = platform.system()
    if plat == "Darwin":
        jxa = """
        function run() {
            const se = Application('System Events');
            const procs = se.processes.whose({ frontmost: true })();
            if (!procs.length) return JSON.stringify([]);
            const win = procs[0].windows()[0];
            let elements = [];
            function traverse(el, depth) {
                if (depth > 6) return;
                try {
                    const role = el.role(), name = el.name();
                    const pos = el.position(), sz = el.size();
                    if (pos && sz) {
                        if (name || role === 'AXButton' || role === 'AXTextField' || role === 'AXTextArea')
                            elements.push({role, name: name || '',
                                           x: Math.round(pos[0]+sz[0]/2),
                                           y: Math.round(pos[1]+sz[1]/2)});
                    }
                    const kids = el.uiElements();
                    for (let i = 0; i < kids.length; i++) traverse(kids[i], depth + 1);
                } catch(e) {}
            }
            if (win) traverse(win, 0);
            return JSON.stringify(elements);
        }
        """
        out = subprocess.check_output(
            ["osascript", "-l", "JavaScript", "-e", jxa], timeout=10
        ).decode()
        return [{"type": "text", "text": out.strip()}]

    elif plat == "Windows":
        try:
            from pywinauto import Desktop
            win = Desktop(backend="uia").windows(visible_only=True)[0]
            elements = [
                {"role": c.friendly_class_name(), "name": c.window_text(),
                 "x": c.rectangle().mid_point().x, "y": c.rectangle().mid_point().y}
                for c in win.descendants()
            ]
            return [{"type": "text", "text": json.dumps(elements)}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"error": str(e)})}]

    else:
        try:
            import pyatspi
            desktop = pyatspi.Registry.getDesktop(0)
            active_win = None
            for app in desktop:
                for window in app:
                    if window.getState().contains(pyatspi.STATE_ACTIVE):
                        active_win = window
                        break
                if active_win:
                    break
            if not active_win:
                return [{"type": "text", "text": "[]"}]
            elements = []
            def traverse(node, depth):
                if not node or depth > 6:
                    return
                try:
                    ext = node.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                    if ext.width > 0:
                        elements.append({"role": node.getRoleName(), "name": node.name or "",
                                         "x": ext.x + ext.width // 2, "y": ext.y + ext.height // 2})
                except Exception:
                    pass
                for child in node:
                    traverse(child, depth + 1)
            traverse(active_win, 0)
            return [{"type": "text", "text": json.dumps(elements)}]
        except ImportError:
            return [{"type": "text", "text": json.dumps([{"error": "install python3-pyatspi"}])}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps([{"error": str(e)}])}]


def handle_click_element_by_name(args):
    elem_name   = args.get("element_name") or args.get("text")
    match_index = int(args.get("index", 0))
    if not elem_name:
        raise Exception("Missing element_name")

    plat = platform.system()
    if plat == "Darwin":
        js_name = json.dumps(elem_name)
        js_idx  = int(match_index)
        jxa = f"""
        function run() {{
            const se = Application('System Events');
            const procs = se.processes.whose({{ frontmost: true }})();
            if (!procs.length) return "Not found";
            const win = procs[0].windows()[0];
            const needle = {js_name};
            let matches = [];
            function traverse(el, depth) {{
                if (depth > 6) return;
                try {{
                    const name = el.name();
                    if (name && name.indexOf(needle) !== -1) {{
                        const pos = el.position(), sz = el.size();
                        if (pos && sz) matches.push({{x: Math.round(pos[0]+sz[0]/2),
                                                       y: Math.round(pos[1]+sz[1]/2)}});
                    }}
                    const kids = el.uiElements();
                    for (let i = 0; i < kids.length; i++) traverse(kids[i], depth + 1);
                }} catch(e) {{}}
            }}
            if (win) traverse(win, 0);
            if (!matches.length) return "Not found";
            const idx = {js_idx} < 0 ? matches.length + {js_idx} : {js_idx};
            const m = matches[Math.min(Math.max(idx, 0), matches.length - 1)];
            return m.x + "," + m.y;
        }}
        """
        out = subprocess.check_output(
            ["osascript", "-l", "JavaScript", "-e", jxa], timeout=10
        ).decode().strip()

        if out == "Not found":
            # OCR fallback — finds text anywhere on screen
            swift_src = os.path.join(os.path.dirname(__file__), "find_text_on_screen.swift")
            swift_exe = os.path.join(os.path.dirname(__file__), "find_text_on_screen")
            if not os.path.exists(swift_exe):
                subprocess.run(["swiftc", swift_src, "-o", swift_exe], check=True)
            with mss.MSS() as sct:
                filename = sct.shot(output="ocr_temp.png")
            try:
                ocr_out = subprocess.check_output(
                    [swift_exe, filename, elem_name], timeout=15
                ).decode().strip()
            finally:
                if os.path.exists(filename):
                    os.remove(filename)
            if not ocr_out or "Failed" in ocr_out:
                raise Exception(f"Element '{elem_name}' not found (OCR failed)")
            lines = [l for l in ocr_out.split("\n") if "," in l]
            if not lines:
                raise Exception(f"Element '{elem_name}' not found on screen")
            idx = match_index if match_index >= 0 else max(0, len(lines) + match_index)
            x, y = map(float, lines[min(idx, len(lines) - 1)].split(","))
            x, y = int(x), int(y)
        else:
            x, y = map(int, out.split(","))

        utils.safe_click(x, y, "", "")   # no specific proc — best-effort
        return [{"type": "text", "text": f"Clicked '{elem_name}' at {x},{y}"}]

    elif plat == "Windows":
        from pywinauto import Desktop
        win = Desktop(backend="uia").windows(visible_only=True)[0]
        matches = [c for c in win.descendants() if elem_name in c.window_text()]
        if not matches:
            raise Exception(f"Element '{elem_name}' not found")
        idx = match_index if match_index >= 0 else max(0, len(matches) + match_index)
        ctrl = matches[min(idx, len(matches) - 1)]
        pt = ctrl.rectangle().mid_point()
        mouse.position = (pt.x, pt.y)
        mouse.click(Button.left)
        return [{"type": "text", "text": f"Clicked '{elem_name}'"}]

    else:
        import pyatspi
        desktop = pyatspi.Registry.getDesktop(0)
        active_win = None
        for a in desktop:
            for window in a:
                if window.getState().contains(pyatspi.STATE_ACTIVE):
                    active_win = window
                    break
            if active_win:
                break
        if not active_win:
            raise Exception("No active window")
        matches = []
        def _traverse(node, depth):
            if not node or depth > 6:
                return
            try:
                if elem_name in (node.name or ""):
                    ext = node.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                    if ext.width > 0:
                        matches.append((ext.x + ext.width // 2, ext.y + ext.height // 2))
            except Exception:
                pass
            for child in node:
                _traverse(child, depth + 1)
        _traverse(active_win, 0)
        if not matches:
            raise Exception(f"Element '{elem_name}' not found")
        idx = match_index if match_index >= 0 else max(0, len(matches) + match_index)
        pos = matches[min(idx, len(matches) - 1)]
        mouse.position = pos
        mouse.click(Button.left)
        return [{"type": "text", "text": f"Clicked '{elem_name}' at {pos}"}]


def handle_focus_input(args):
    """Find and click the primary text input field in the active window."""
    hint = args.get("hint", "AXTextArea")
    plat = platform.system()

    if plat == "Darwin":
        coords = utils.find_input_field(role_hint=hint)
        if coords:
            x, y = coords
            mouse.position = (x, y)
            mouse.click(Button.left)
            time.sleep(0.1)
            return [{"type": "text", "text": f"Focused input at {x},{y} (accessibility)"}]

        bounds = utils.get_frontmost_window_bounds()
        if bounds:
            x = bounds["x"] + bounds["w"] // 2
            y = bounds["y"] + int(bounds["h"] * 0.88)
            mouse.position = (x, y)
            mouse.click(Button.left)
            time.sleep(0.1)
            return [{"type": "text", "text": f"Focused input at {x},{y} (window fallback)"}]

    with mss.MSS() as sct:
        m = sct.monitors[1]
        x = m["left"] + m["width"] // 2
        y = m["top"] + int(m["height"] * 0.88)
    mouse.position = (x, y)
    mouse.click(Button.left)
    time.sleep(0.1)
    return [{"type": "text", "text": f"Focused input at {x},{y} (screen fallback)"}]


def handle_clear_and_type(args):
    """Clear the focused field then type (clipboard injection for CJK/emoji)."""
    text = args.get("text", "")
    utils.clear_field()
    time.sleep(0.1)
    utils.clipboard_type(text)
    return [{"type": "text", "text": f"Typed: {text[:60]}{'...' if len(text) > 60 else ''}"}]


def handle_send_message_to(args):
    """
    High-level chat op: open an app, find a contact/group, and send a message.

    Parameters
    ----------
    contact_name  Name of the contact or group chat.
    message       Message text.
    app           App alias (any alias from a profile in src/profiles/).
    wait_search   Seconds to wait for search results (default 1.5).
    wait_chat     Seconds to wait for chat to open (default 0.8).

    The search-result selection step is handled by the app's adapter
    (adapters/registry.py → adapters/<category>/<app>.py).
    main.py never contains app-specific selection logic.
    """
    contact_name = args.get("contact_name", "").strip()
    message      = args.get("message", "").strip()
    app_key = args.get("app", args.get("app_name", "")).strip().lower()
    if not app_key:
        # Default to the first known chat app if none provided
        chat_apps = [k for k, v in APP_PROFILES.items() if v.get("category") == "chat" and not k.isascii()]
        app_key = chat_apps[0] if chat_apps else "wechat"

    wait_search  = float(args.get("wait_search", 1.5))
    wait_chat    = float(args.get("wait_chat", 0.8))

    if not contact_name:
        raise Exception("send_message_to requires 'contact_name'")
    if not message:
        raise Exception("send_message_to requires 'message'")
    for field, val in (("contact_name", contact_name), ("message", message)):
        if any(ord(c) < 0x20 and c not in ("\t",) for c in val):
            raise Exception(f"'{field}' contains disallowed control characters")

    profile = APP_PROFILES.get(app_key)
    if not profile:
        known = sorted({k for k, v in APP_PROFILES.items() if v.get("category") == "chat"})
        raise Exception(
            f"Unknown app '{app_key}'. Known chat apps: {', '.join(known)}. "
            "Add a JSON file in src/profiles/ to support a new app."
        )

    plat          = platform.system()
    proc_name     = profile.get("process_name", profile.get("open_name", app_key))
    actual_app    = profile.get("app_name", app_key)
    open_name     = profile.get("open_name", actual_app)
    bundle_id     = profile.get("bundle_id", "")
    search_sc     = _resolve(profile.get("search_shortcut", "cmd+f"))
    send_sc       = _resolve(profile.get("send_shortcut", "enter"))
    input_hint    = _resolve(profile.get("input_role_hint", "AXTextArea"))
    search_sect   = _resolve(profile.get("search_result_section"))
    pre_reset     = bool(profile.get("pre_search_reset", False))

    steps: list = []
    def _log(msg): steps.append(msg)

    # ── 1. Activate app ───────────────────────────────────────────────────────
    _log(f"[1] Activating {actual_app}")
    handle_open_app({"app_name": actual_app, "open_name": open_name, "bundle_id": bundle_id})
    time.sleep(2.0)

    if plat == "Darwin":
        front = utils.get_frontmost_app_name()
        if proc_name.lower() not in (front or "").lower():
            _log(f"[1b] Retrying focus (frontmost='{front}')")
            subprocess.run(["osascript", "-e", f'tell application "{open_name}" to activate'])
            time.sleep(1.5)
            front = utils.get_frontmost_app_name()
        _log(f"[1] Frontmost: '{front}'")

    # Cache window info NOW — before any search UI appears.
    # Use Quartz (no subprocess, no focus change) to get both the window ID
    # and bounds.  Adapters use screencapture -l <id> later, which captures
    # the exact window pixels without touching System Events or stealing focus.
    if plat == "Darwin":
        _winfo = utils.get_window_id_for_process(proc_name)
        if _winfo and _winfo.get("w", 0) > 50:
            profile["_window_id"]     = _winfo["id"]
            profile["_window_bounds"] = {k: _winfo[k] for k in ("x", "y", "w", "h")}
            _log(f"[1] Window id={_winfo['id']} bounds=({_winfo['x']},{_winfo['y']},{_winfo['w']},{_winfo['h']})")

    # ── 2. Open search ────────────────────────────────────────────────────────
    # Initialize adapter early to delegate shortcuts
    adapter = get_adapter(profile)

    if pre_reset:
        _log("[2] Resetting state (Escape)")
        adapter.press_escape(proc_name, plat)
        time.sleep(0.3)

    _log(f"[2] Search shortcut: {search_sc}")
    adapter.press_search_shortcut(proc_name, plat, search_sc)
    time.sleep(0.8)

    # ── 3. Type contact name ──────────────────────────────────────────────────
    _log(f"[3] Searching for '{contact_name}'")
    utils.clear_field()
    time.sleep(0.15)
    utils.clipboard_type(contact_name)
    time.sleep(wait_search)

    # ── 4. Select search result — delegated entirely to the app's adapter ─────
    _log(f"[4] Selecting '{contact_name}'")
    adapter.select_search_result(
        contact_name=contact_name,
        section=search_sect,
        profile=profile,
        proc_name=proc_name,
        plat=plat,
        log=_log,
    )
    time.sleep(wait_chat + 0.5)

    # ── 5. Re-verify focus ────────────────────────────────────────────────────
    if plat == "Darwin":
        ok = utils.ensure_frontmost(proc_name, open_name, bundle_id)
        front = utils.get_frontmost_app_name()
        _log(f"[5] ensure_frontmost={'ok' if ok else 'FAILED'}, frontmost='{front}'")

    # ── 6. Focus message input ────────────────────────────────────────────────
    # Escape closes any residual search overlay; ensure_frontmost guarantees the
    # click that follows lands in the correct app window.
    adapter.press_escape(proc_name, plat)
    time.sleep(0.2)
    if plat == "Darwin":
        utils.ensure_frontmost(proc_name, open_name, bundle_id)
    _log(f"[6] Focusing input ({input_hint})")
    handle_focus_input({"hint": input_hint})
    time.sleep(0.3)

    # ── 7. Type message ───────────────────────────────────────────────────────
    preview = message[:60] + ("..." if len(message) > 60 else "")
    _log(f"[7] Typing: '{preview}'")
    utils.clear_field()
    time.sleep(0.15)
    utils.clipboard_type(message)
    time.sleep(0.2)

    # ── 8. Send ───────────────────────────────────────────────────────────────
    _log(f"[8] Sending via: {send_sc}")
    adapter.press_send_shortcut(proc_name, plat, send_sc)

    return [{"type": "text", "text": f"✅ Sent to '{contact_name}' via {actual_app}\n\n" + "\n".join(steps)}]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def handle_computer(args):
    action = args.get("action")

    if action == "open_app":            return handle_open_app(args)
    if action == "get_ui_tree":         return handle_get_ui_tree(args)
    if action == "click_element_by_name": return handle_click_element_by_name(args)
    if action == "focus_input":         return handle_focus_input(args)
    if action == "clear_and_type":      return handle_clear_and_type(args)
    if action == "send_message_to":     return handle_send_message_to(args)

    x, y = 0, 0
    if args.get("coordinate") and len(args["coordinate"]) >= 2:
        x, y = int(args["coordinate"][0]), int(args["coordinate"][1])

    if action == "screenshot":
        with mss.MSS() as sct:
            filename = sct.shot(output="screenshot.png")
            with open(filename, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            os.remove(filename)
            return [{"type": "image", "data": b64, "mimeType": "image/png"}]
    elif action == "mouse_move":   mouse.position = (x, y)
    elif action == "left_click":   mouse.position = (x, y); mouse.click(Button.left)
    elif action == "right_click":  mouse.position = (x, y); mouse.click(Button.right)
    elif action == "double_click": mouse.position = (x, y); mouse.click(Button.left, 2)
    elif action == "type":         utils.clipboard_type(args.get("text", ""))
    elif action == "key":          utils.press_shortcut(args.get("text", ""))
    else:
        raise Exception(f"Unknown action: '{action}'")

    return [{"type": "text", "text": "success"}]


# ---------------------------------------------------------------------------
# MCP JSON-RPC server
# ---------------------------------------------------------------------------

TOOL_SCHEMA = {
    "name": "computer",
    "description": (
        "Universal desktop automation. "
        "Use 'send_message_to' to send a message in any supported chat app with one call. "
        "Use low-level actions (screenshot, click, type, key, get_ui_tree) to interact with any app. "
        "Supported chat apps are defined by profiles in src/profiles/. "
        "App-specific behaviour lives in src/adapters/ — main.py never changes for new apps."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "screenshot", "left_click", "right_click", "double_click",
                    "mouse_move", "type", "key",
                    "open_app", "get_ui_tree", "click_element_by_name",
                    "focus_input", "clear_and_type", "send_message_to",
                ],
                "description": (
                    "Action:\n"
                    "• send_message_to — open a chat app, find contact/group, send message.\n"
                    "• open_app — launch or focus an application.\n"
                    "• get_ui_tree — accessibility elements of active window as JSON.\n"
                    "• click_element_by_name — click a UI element by name/label.\n"
                    "• focus_input — click the primary input field in the active window.\n"
                    "• clear_and_type — clear field and type text (CJK/emoji safe).\n"
                    "• type — type text at cursor.\n"
                    "• key — press a shortcut, e.g. 'enter', 'cmd+f', 'ctrl+a'.\n"
                    "• screenshot — capture full screen as base64 PNG.\n"
                    "• mouse_move / left_click / right_click / double_click — coordinate mouse."
                ),
            },
            "coordinate": {"type": "array", "items": {"type": "number"},
                           "description": "[x, y] screen coordinates for mouse actions."},
            "text":        {"type": "string", "description": "Text to type or key shortcut string."},
            "app_name":    {"type": "string", "description": "Application name for open_app."},
            "element_name":{"type": "string", "description": "Name substring of element to click."},
            "index":       {"type": "integer", "description": "Match index: 0=first, -1=last."},
            "hint":        {"type": "string", "description": "Accessibility role hint for focus_input."},
            "contact_name":{"type": "string", "description": "[send_message_to] Contact or group chat name."},
            "message":     {"type": "string", "description": "[send_message_to] Message to send."},
            "app":         {"type": "string",
                            "description": (
                                "[send_message_to] Target app alias from src/profiles/. "
                                "Examples: 'wechat', 'slack', 'lark', 'dingtalk', 'telegram'. "
                                "If omitted, defaults to the first available chat profile."
                            )},
            "wait_search": {"type": "number", "description": "[send_message_to] Wait for search results (default 1.5s)."},
            "wait_chat":   {"type": "number", "description": "[send_message_to] Wait for chat to open (default 0.8s)."},
        },
        "required": ["action"],
    },
}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            _send_error(None, -32700, "Parse error")
            continue

        req_id = req.get("id")
        method = req.get("method")

        try:
            if method == "initialize":
                _send_result(req_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "polarisagi-computer-mcp", "version": "1.0.0"},
                })
            elif method == "ping":
                _send_result(req_id, {})
            elif method == "tools/list":
                _send_result(req_id, {"tools": [TOOL_SCHEMA]})
            elif method == "tools/call":
                params = req.get("params", {})
                if params.get("name") == "computer":
                    result = handle_computer(params.get("arguments", {}))
                    _send_result(req_id, {"content": result})
                else:
                    _send_error(req_id, -32601, "Tool not found")
            else:
                # Silently ignore notifications (requests without an ID, like 'notifications/initialized')
                if req_id is not None:
                    _send_error(req_id, -32601, "Method not found")
        except Exception as e:
            _send_error(req_id, -32603, str(e))


def _send_result(req_id, result):
    if req_id is None:
        return
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()


def _send_error(req_id, code, message):
    if req_id is None:
        return
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
