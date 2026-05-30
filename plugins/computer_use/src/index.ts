#!/usr/bin/env node
import * as readline from 'readline';
import { mouse, keyboard, Key, Point, Button, clipboard } from '@nut-tree-fork/nut-js';
import { execFile } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as os from 'os';
import * as path from 'path';

const execFileAsync = promisify(execFile);

async function captureScreen(): Promise<string> {
    const tmpPath = path.join(os.tmpdir(), `screenshot-${Date.now()}.png`);
    try {
        if (process.platform === 'darwin') {
            await execFileAsync('screencapture', ['-x', tmpPath]);
        } else if (process.platform === 'win32') {
            const psScript = `
            Add-Type -AssemblyName System.Windows.Forms;
            Add-Type -AssemblyName System.Drawing;
            $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen;
            $Width = $Screen.Width; $Height = $Screen.Height;
            $Left = $Screen.Left; $Top = $Screen.Top;
            $bitmap = New-Object System.Drawing.Bitmap $Width, $Height;
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap);
            $graphic.CopyFromScreen($Left, $Top, 0, 0, $bitmap.Size);
            $bitmap.Save('${tmpPath}');
            `;
            await execFileAsync('powershell', ['-Command', psScript]);
        } else {
            try {
                // Try scrot first
                await execFileAsync('scrot', [tmpPath]);
            } catch (err) {
                // Fallback to ImageMagick (import)
                await execFileAsync('import', ['-window', 'root', tmpPath]);
            }
        }
        const buffer = await fs.readFile(tmpPath);
        return buffer.toString('base64');
    } finally {
        try {
            await fs.unlink(tmpPath);
        } catch (e) {
            // ignore
        }
    }
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

function sendResult(id: any, result: any) {
    if (id === undefined || id === null) return;
    const resp = {
        jsonrpc: "2.0",
        id,
        result
    };
    console.log(JSON.stringify(resp));
}

function sendError(id: any, code: number, message: string) {
    const resp = {
        jsonrpc: "2.0",
        id,
        error: { code, message }
    };
    console.log(JSON.stringify(resp));
}

rl.on('line', async (line) => {
    if (!line.trim()) return;

    let req: any;
    try {
        req = JSON.parse(line);
    } catch (e) {
        sendError(null, -32700, "Parse error: " + e);
        return;
    }

    const id = req.id;

    try {
        if (req.method === "initialize") {
            sendResult(id, {
                protocolVersion: "2024-11-05",
                capabilities: { tools: {}, prompts: {} },
                serverInfo: {
                    name: "polarisagi-computer-mcp",
                    version: "0.1.0"
                }
            });
        } else if (req.method === "prompts/list") {
            sendResult(id, {
                prompts: [{
                    name: "computer_use_guidelines",
                    description: "Standard system guidelines for AI agents using the computer plugin.",
                    arguments: []
                }]
            });
        } else if (req.method === "prompts/get") {
            const promptName = req.params?.name;
            if (promptName === "computer_use_guidelines") {
                sendResult(id, {
                    description: "System Prompt for Computer Use",
                    messages: [
                        {
                            role: "user",
                            content: {
                                type: "text",
                                text: "You have permission to operate a real computer. Please strictly follow these visual recognition and operation guidelines:\n\n1. Visual Feedback Loop: Before executing any click (`left_click`) or input (`type`/`paste`), you MUST call `screenshot` to get the current screen state. Analyze the screenshot carefully to find the absolute coordinates `[x, y]` of the target UI element before clicking.\n\n2. Handling UI States: UI elements may have loading animations or network delays. After interacting with an element (e.g. clicking 'search'), do not assume the action completed instantly. You MUST call `screenshot` again to verify the new UI state (like checking if a dropdown menu appeared) before proceeding.\n\n3. Text Input Rules: When inputting Chinese characters or long text, you MUST prioritize the `paste` action. This bypasses input method editor (IME) interference and prevents text truncation. Only use `type` or `key` for pure English characters or shortcuts.\n\n4. Error Recovery: If the screenshot does not match your expectations (e.g. click failed or text was typed in the wrong place), analyze the screen, use `mouse_move` to move the focus away, or send `key: escape` to cancel the current state, and retry."
                            }
                        }
                    ]
                });
            } else {
                sendError(id, -32602, "Prompt not found");
            }
        } else if (req.method === "tools/list") {
            sendResult(id, {
                tools: [{
                    name: "computer",
                    description: "Execute computer actions like clicking, typing, and taking screenshots.",
                    inputSchema: {
                        type: "object",
                        properties: {
                            action: {
                                type: "string",
                                enum: ["screenshot", "left_click", "right_click", "middle_click", "double_click", "mouse_move", "left_click_drag", "cursor_position", "type", "key", "paste"],
                                description: "The action to perform. left_click_drag: press at current position, move to coordinate, release. paste: copy text to clipboard and simulate Cmd+V/Ctrl+V."
                            },
                            coordinate: {
                                type: "array",
                                items: { type: "number" },
                                description: "[x, y] coordinates for mouse actions. For left_click_drag, this is the drag destination."
                            },
                            text: {
                                type: "string",
                                description: "Text to type (action=type) or key name to press (action=key)."
                            }
                        },
                        required: ["action"]
                    }
                }]
            });
        } else if (req.method === "tools/call") {
            const params = req.params || {};
            if (params.name === "computer") {
                const args = params.arguments || {};
                const content = await handleComputerUse(args);
                sendResult(id, { content });
            } else {
                sendError(id, -32601, "Tool not found");
            }
        } else {
            if (id !== undefined) {
                sendError(id, -32601, "Method not found: " + req.method);
            }
        }
    } catch (e: any) {
        if (id !== undefined) {
            sendError(id, -32603, "Execution error: " + e.message);
        }
    }
});

async function handleComputerUse(args: any) {
    const action = args.action;
    if (!action) throw new Error("Missing action parameter");

    let x = 0, y = 0;
    if (Array.isArray(args.coordinate) && args.coordinate.length >= 2) {
        x = Math.round(Number(args.coordinate[0]) || 0);
        y = Math.round(Number(args.coordinate[1]) || 0);
    }

    switch (action) {
        case "screenshot":
            const b64 = await captureScreen();
            return [{
                type: "image",
                data: b64,
                mimeType: "image/png"
            }];
        
        case "mouse_move":
            await mouse.setPosition(new Point(x, y));
            return [{ type: "text", text: "success" }];
            
        case "left_click":
            await mouse.setPosition(new Point(x, y));
            await mouse.leftClick();
            return [{ type: "text", text: "success" }];
            
        case "right_click":
            await mouse.setPosition(new Point(x, y));
            await mouse.rightClick();
            return [{ type: "text", text: "success" }];
            
        case "middle_click":
            await mouse.setPosition(new Point(x, y));
            await mouse.pressButton(Button.MIDDLE);
            await mouse.releaseButton(Button.MIDDLE);
            return [{ type: "text", text: "success" }];
            
        case "double_click":
            await mouse.setPosition(new Point(x, y));
            await mouse.doubleClick(Button.LEFT);
            return [{ type: "text", text: "success" }];
            
        case "left_click_drag":
            await mouse.pressButton(Button.LEFT);
            await mouse.setPosition(new Point(x, y));
            await mouse.releaseButton(Button.LEFT);
            return [{ type: "text", text: "success" }];
            
        case "cursor_position":
            const pos = await mouse.getPosition();
            return [{ type: "text", text: `X: ${pos.x}, Y: ${pos.y}` }];
            
        case "type":
            if (!args.text) throw new Error("Missing text parameter");
            await keyboard.type(args.text);
            return [{ type: "text", text: "success" }];
            
        case "paste":
            if (!args.text) throw new Error("Missing text parameter");
            await clipboard.setContent(args.text);
            // wait a tiny bit to ensure clipboard is synced
            await new Promise(r => setTimeout(r, 200));
            if (process.platform === 'darwin') {
                await keyboard.pressKey(Key.LeftSuper, Key.V);
                await keyboard.releaseKey(Key.LeftSuper, Key.V);
            } else {
                await keyboard.pressKey(Key.LeftControl, Key.V);
                await keyboard.releaseKey(Key.LeftControl, Key.V);
            }
            return [{ type: "text", text: "success" }];
            
        case "key":
            if (!args.text) throw new Error("Missing text parameter");
            const keyText = args.text.toLowerCase();
            const keyMap: Record<string, Key> = {
                "return": Key.Enter, "enter": Key.Enter,
                "escape": Key.Escape, "esc": Key.Escape,
                "tab": Key.Tab, "space": Key.Space,
                "backspace": Key.Backspace, "delete": Key.Delete, "del": Key.Delete,
                "up": Key.Up, "down": Key.Down, "left": Key.Left, "right": Key.Right,
                "home": Key.Home, "end": Key.End,
                "pageup": Key.PageUp, "page_up": Key.PageUp,
                "pagedown": Key.PageDown, "page_down": Key.PageDown,
                "ctrl": Key.LeftControl, "control": Key.LeftControl,
                "alt": Key.LeftAlt, "shift": Key.LeftShift,
                "meta": Key.LeftSuper, "command": Key.LeftSuper, "win": Key.LeftSuper
            };
            
            let nutKey = keyMap[keyText];
            if (!nutKey && keyText.length === 1) {
                await keyboard.type(keyText);
                return [{ type: "text", text: "success" }];
            } else if (!nutKey) {
                throw new Error(`Unsupported key: ${args.text}`);
            }
            
            await keyboard.pressKey(nutKey);
            await keyboard.releaseKey(nutKey);
            return [{ type: "text", text: "success" }];
            
        default:
            throw new Error(`Action '${action}' is not fully implemented yet`);
    }
}
