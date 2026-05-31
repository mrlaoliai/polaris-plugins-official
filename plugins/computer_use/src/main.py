#!/usr/bin/env python3
import sys
import json
import base64
import os
import subprocess
import platform
import mss
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

mouse = MouseController()
keyboard = KeyboardController()

def send_result(req_id, result):
    if req_id is None: return
    resp = {"jsonrpc": "2.0", "id": req_id, "result": result}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    if req_id is None: return
    resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()

def handle_open_app(args):
    app_name = args.get("app_name") or args.get("text")
    if not app_name:
        raise Exception("Missing app_name parameter")
        
    plat = platform.system()
    if plat == "Darwin":
        subprocess.run(["open", "-a", app_name], check=True)
    elif plat == "Windows":
        subprocess.run(["cmd", "/c", "start", "", app_name], shell=True)
    elif plat == "Linux":
        subprocess.Popen(["xdg-open", app_name])
    return [{"type": "text", "text": f"Successfully opened {app_name}"}]

def handle_get_ui_tree(args):
    plat = platform.system()
    if plat == "Darwin":
        jxa = """
        function run() {
            const se = Application('System Events');
            const procs = se.processes.whose({ frontmost: true })();
            if (procs.length === 0) return JSON.stringify([]);
            const win = procs[0].windows()[0];
            let elements = [];
            function traverse(uiElem, depth) {
                if (depth > 6) return;
                try {
                    const role = uiElem.role();
                    const name = uiElem.name();
                    const pos = uiElem.position();
                    const size = uiElem.size();
                    if (pos && size) {
                        if (name || role === 'AXButton' || role === 'AXTextField') {
                            elements.push({role: role, name: name || '', x: Math.round(pos[0] + size[0]/2), y: Math.round(pos[1] + size[1]/2)});
                        }
                    }
                    const children = uiElem.uiElements();
                    for (let i=0; i<children.length; i++) traverse(children[i], depth + 1);
                } catch (e) {}
            }
            if (win) traverse(win, 0);
            return JSON.stringify(elements);
        }
        """
        out = subprocess.check_output(["osascript", "-l", "JavaScript", "-e", jxa]).decode("utf-8")
        return [{"type": "text", "text": out.strip()}]
    elif plat == "Windows":
        try:
            from pywinauto import Desktop
            app = Desktop(backend="uia")
            win = app.windows(visible_only=True)[0]
            elements = []
            for ctrl in win.descendants():
                rect = ctrl.rectangle()
                elements.append({
                    "role": ctrl.friendly_class_name(),
                    "name": ctrl.window_text(),
                    "x": rect.mid_point().x,
                    "y": rect.mid_point().y
                })
            return [{"type": "text", "text": json.dumps(elements)}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps({"error": str(e)})}]
    elif plat == "Linux":
        try:
            import pyatspi
            desktop = pyatspi.Registry.getDesktop(0)
            active_win = None
            for app in desktop:
                for window in app:
                    if window.getState().contains(pyatspi.STATE_ACTIVE):
                        active_win = window
                        break
                if active_win: break
            
            if not active_win:
                return [{"type": "text", "text": "[]"}]
                
            elements = []
            def traverse(accessible, depth):
                if not accessible or depth > 6: return
                try:
                    role = accessible.getRoleName()
                    name = accessible.name if accessible.name else ""
                    extents = accessible.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                    if extents.width > 0 and extents.height > 0:
                        elements.append({
                            "role": role,
                            "name": name,
                            "x": extents.x + extents.width // 2,
                            "y": extents.y + extents.height // 2
                        })
                except Exception:
                    pass
                for child in accessible:
                    traverse(child, depth + 1)
                    
            traverse(active_win, 0)
            return [{"type": "text", "text": json.dumps(elements)}]
        except ImportError:
            return [{"type": "text", "text": json.dumps([{"role": "error", "name": "Please install python3-pyatspi (e.g. sudo apt install python3-pyatspi) to enable Linux UI tree.", "x":0, "y":0}])}]
        except Exception as e:
            return [{"type": "text", "text": json.dumps([{"role": "error", "name": str(e), "x":0, "y":0}])}]
    
def handle_click_element_by_name(args):
    elem_name = args.get("element_name") or args.get("text")
    if not elem_name: raise Exception("Missing element_name")
    
    plat = platform.system()
    if plat == "Darwin":
        safe_name = elem_name.replace('"', '\\"')
        jxa = f"""
        function run() {{
            const se = Application('System Events');
            const procs = se.processes.whose({{ frontmost: true }})();
            if (procs.length === 0) return "Not found";
            const win = procs[0].windows()[0];
            let foundPos = null;
            function traverse(uiElem, depth) {{
                if (foundPos || depth > 6) return;
                try {{
                    const name = uiElem.name();
                    if (name && name.indexOf("{safe_name}") !== -1) {{
                        const pos = uiElem.position();
                        const size = uiElem.size();
                        if (pos && size) foundPos = {{x: Math.round(pos[0] + size[0]/2), y: Math.round(pos[1] + size[1]/2)}};
                    }}
                    const children = uiElem.uiElements();
                    for (let i=0; i<children.length; i++) traverse(children[i], depth + 1);
                }} catch (e) {{}}
            }}
            if (win) traverse(win, 0);
            if (foundPos) return foundPos.x + "," + foundPos.y;
            return "Not found";
        }}
        """
        out = subprocess.check_output(["osascript", "-l", "JavaScript", "-e", jxa]).decode("utf-8").strip()
        if out == "Not found": raise Exception("Element not found")
        x, y = map(int, out.split(","))
        mouse.position = (x, y)
        mouse.click(Button.left)
        return [{"type": "text", "text": f"Clicked '{elem_name}' at {x}, {y}"}]
    elif plat == "Windows":
        try:
            from pywinauto import Desktop
            app = Desktop(backend="uia")
            win = app.windows(visible_only=True)[0]
            for ctrl in win.descendants():
                if elem_name in ctrl.window_text():
                    rect = ctrl.rectangle()
                    x, y = rect.mid_point().x, rect.mid_point().y
                    mouse.position = (x, y)
                    mouse.click(Button.left)
                    return [{"type": "text", "text": f"Clicked '{elem_name}'"}]
            raise Exception("Element not found")
        except Exception as e:
            raise Exception(str(e))
    elif plat == "Linux":
        try:
            import pyatspi
            desktop = pyatspi.Registry.getDesktop(0)
            active_win = None
            for app in desktop:
                for window in app:
                    if window.getState().contains(pyatspi.STATE_ACTIVE):
                        active_win = window
                        break
                if active_win: break
                
            if not active_win:
                raise Exception("No active window found")
                
            found_pos = None
            def traverse(accessible, depth):
                nonlocal found_pos
                if found_pos or not accessible or depth > 6: return
                try:
                    name = accessible.name if accessible.name else ""
                    if elem_name in name:
                        extents = accessible.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                        if extents.width > 0 and extents.height > 0:
                            found_pos = (extents.x + extents.width // 2, extents.y + extents.height // 2)
                except Exception:
                    pass
                for child in accessible:
                    traverse(child, depth + 1)
                    
            traverse(active_win, 0)
            if not found_pos:
                raise Exception("Element not found")
                
            mouse.position = found_pos
            mouse.click(Button.left)
            return [{"type": "text", "text": f"Clicked '{elem_name}' at {found_pos[0]}, {found_pos[1]}"}]
            
        except ImportError:
            raise Exception("Please install python3-pyatspi (e.g. sudo apt install python3-pyatspi) to enable Linux UI tree support.")

def handle_computer(args):
    action = args.get("action")
    if action == "open_app": return handle_open_app(args)
    if action == "get_ui_tree": return handle_get_ui_tree(args)
    if action == "click_element_by_name": return handle_click_element_by_name(args)
        
    x, y = 0, 0
    if args.get("coordinate") and len(args["coordinate"]) >= 2:
        x, y = int(args["coordinate"][0]), int(args["coordinate"][1])
        
    if action == "screenshot":
        with mss.mss() as sct:
            filename = sct.shot(output="screenshot.png")
            with open(filename, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            os.remove(filename)
            return [{"type": "image", "data": b64, "mimeType": "image/png"}]
    elif action == "mouse_move": 
        mouse.position = (x, y)
    elif action == "left_click": 
        mouse.position = (x, y)
        mouse.click(Button.left)
    elif action == "right_click": 
        mouse.position = (x, y)
        mouse.click(Button.right)
    elif action == "double_click": 
        mouse.position = (x, y)
        mouse.click(Button.left, 2)
    elif action == "type": 
        keyboard.type(args.get("text", ""))
    elif action == "key": 
        key_str = args.get("text", "").lower()
        key_map = {
            "enter": Key.enter, "return": Key.enter,
            "esc": Key.esc, "escape": Key.esc,
            "tab": Key.tab, "space": Key.space,
            "backspace": Key.backspace, "delete": Key.delete, "del": Key.delete,
            "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
            "home": Key.home, "end": Key.end,
            "pageup": Key.page_up, "pagedown": Key.page_down,
            "ctrl": Key.ctrl, "alt": Key.alt, "shift": Key.shift, "cmd": Key.cmd, "win": Key.cmd
        }
        target_key = key_map.get(key_str)
        if target_key:
            keyboard.tap(target_key)
        elif len(key_str) == 1:
            keyboard.tap(key_str)
        else:
            raise Exception(f"Unsupported key: {key_str}")
    else: 
        raise Exception(f"Action {action} not implemented")
        
    return [{"type": "text", "text": "success"}]

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: req = json.loads(line)
        except:
            send_error(None, -32700, "Parse error")
            continue
            
        req_id = req.get("id")
        method = req.get("method")
        
        try:
            if method == "initialize":
                send_result(req_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "polarisagi-computer-mcp", "version": "0.3.0"}
                })
            elif method == "tools/list":
                send_result(req_id, {
                    "tools": [{
                        "name": "computer",
                        "description": "Cross-platform computer automation.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["screenshot", "left_click", "right_click", "double_click", "mouse_move", "type", "key", "open_app", "get_ui_tree", "click_element_by_name"],
                                    "description": "The action to perform. open_app: natively launch/focus an app. get_ui_tree: get semantic UI elements of the active window. click_element_by_name: precise click by element name."
                                },
                                "coordinate": {
                                    "type": "array", 
                                    "items": {"type": "number"},
                                    "description": "[x, y] absolute coordinates for legacy mouse actions."
                                },
                                "text": {
                                    "type": "string",
                                    "description": "Text to type (action=type) or key string (action=key, e.g. 'enter', 'esc', 'ctrl')."
                                },
                                "app_name": {
                                    "type": "string",
                                    "description": "Name of the application to open (for open_app)."
                                },
                                "element_name": {
                                    "type": "string",
                                    "description": "Name or substring of the UI element to click (for click_element_by_name)."
                                }
                            },
                            "required": ["action"]
                        }
                    }]
                })
            elif method == "tools/call":
                params = req.get("params", {})
                if params.get("name") == "computer":
                    result = handle_computer(params.get("arguments", {}))
                    send_result(req_id, {"content": result})
                else:
                    send_error(req_id, -32601, "Tool not found")
            else:
                send_error(req_id, -32601, "Method not found")
        except Exception as e:
            send_error(req_id, -32603, str(e))

if __name__ == "__main__":
    main()
