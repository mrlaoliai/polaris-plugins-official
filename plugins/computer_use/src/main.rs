use anyhow::{Result, anyhow};
use base64::{Engine as _, engine::general_purpose::STANDARD};
use enigo::{Button, Coordinate, Direction, Enigo, Key, Keyboard, Mouse, Settings};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::io::{self, BufRead, Write};
use xcap::Monitor;

#[derive(Deserialize, Debug)]
struct RpcRequest {
    jsonrpc: String,
    id: Option<Value>,
    method: String,
    params: Option<Value>,
}

#[derive(Serialize)]
struct RpcResponse {
    jsonrpc: String,
    id: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<RpcError>,
}

#[derive(Serialize)]
struct RpcError {
    code: i32,
    message: String,
}

#[tokio::main]
async fn main() -> Result<()> {
    let mut enigo = Enigo::new(&Settings::default())
        .map_err(|e| anyhow!("Failed to initialize enigo: {}", e))?;

    let stdin = io::stdin();
    let mut stdout = io::stdout();

    for line_result in stdin.lock().lines() {
        let line = match line_result {
            Ok(l) => l,
            Err(_) => break, // EOF or error
        };

        if line.trim().is_empty() {
            continue;
        }

        let req: RpcRequest = match serde_json::from_str(&line) {
            Ok(r) => r,
            Err(e) => {
                send_error(None, -32700, format!("Parse error: {}", e), &mut stdout);
                continue;
            }
        };

        let id = req.id.clone();

        match req.method.as_str() {
            "initialize" => {
                send_result(
                    id,
                    json!({
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "polaris-computer-mcp",
                            "version": "0.1.0"
                        }
                    }),
                    &mut stdout,
                );
            }
            "tools/list" => {
                send_result(
                    id,
                    json!({
                        "tools": [{
                            "name": "computer_use_action",
                            "description": "Execute computer actions like clicking, typing, and taking screenshots.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "enum": ["screenshot", "left_click", "right_click", "double_click", "mouse_move", "left_click_drag", "type", "key"],
                                        "description": "left_click_drag: press at current position, move to coordinate, release."
                                    },
                                    "coordinate": {
                                        "type": "array",
                                        "items": { "type": "number" },
                                        "description": "[x, y] coordinates for mouse actions. For left_click_drag, this is the drag destination."
                                    },
                                    "text": {
                                        "type": "string",
                                        "description": "Text to type (action=type) or key name to press (action=key)."
                                    }
                                },
                                "required": ["action"]
                            }
                        }]
                    }),
                    &mut stdout,
                );
            }
            "tools/call" => {
                let params = req.params.unwrap_or_default();
                let name = params["name"].as_str().unwrap_or("");

                if name == "computer_use_action" {
                    let args = params["arguments"].clone();
                    match handle_computer_use(&mut enigo, args) {
                        Ok(content) => {
                            send_result(id, json!({ "content": content }), &mut stdout);
                        }
                        Err(e) => {
                            send_error(id, -32603, format!("Execution error: {}", e), &mut stdout);
                        }
                    }
                } else {
                    send_error(id, -32601, "Tool not found".to_string(), &mut stdout);
                }
            }
            _ => {
                // Ignore notifications (no id)
                if id.is_some() {
                    send_error(
                        id,
                        -32601,
                        format!("Method not found: {}", req.method),
                        &mut stdout,
                    );
                }
            }
        }
    }

    Ok(())
}

fn send_result(id: Option<Value>, result: Value, stdout: &mut io::Stdout) {
    if id.is_none() {
        return;
    }
    let resp = RpcResponse {
        jsonrpc: "2.0".to_string(),
        id,
        result: Some(result),
        error: None,
    };
    if let Ok(json_str) = serde_json::to_string(&resp) {
        println!("{}", json_str);
        let _ = stdout.flush();
    }
}

fn send_error(id: Option<Value>, code: i32, message: String, stdout: &mut io::Stdout) {
    let resp = RpcResponse {
        jsonrpc: "2.0".to_string(),
        id,
        result: None,
        error: Some(RpcError { code, message }),
    };
    if let Ok(json_str) = serde_json::to_string(&resp) {
        println!("{}", json_str);
        let _ = stdout.flush();
    }
}

fn handle_computer_use(enigo: &mut Enigo, args: Value) -> Result<Vec<Value>> {
    let action = args["action"]
        .as_str()
        .ok_or_else(|| anyhow!("Missing action parameter"))?;

    // Parse coordinates if available
    let mut x = 0;
    let mut y = 0;
    if let Some(coord) = args["coordinate"].as_array() {
        if coord.len() >= 2 {
            x = coord[0].as_i64().unwrap_or(0) as i32;
            y = coord[1].as_i64().unwrap_or(0) as i32;
        }
    }

    match action {
        "screenshot" => {
            let monitors = Monitor::all()?;
            // Get primary monitor (usually the first one)
            let monitor = monitors
                .first()
                .ok_or_else(|| anyhow!("No monitors found"))?;
            let image = monitor.capture_image()?;

            // Encode to base64 jpeg or png
            let mut cursor = std::io::Cursor::new(Vec::new());
            image.write_to(&mut cursor, image::ImageFormat::Png)?;
            let b64 = STANDARD.encode(cursor.into_inner());

            Ok(vec![json!({
                "type": "image",
                "data": b64,
                "mimeType": "image/png"
            })])
        }
        "mouse_move" => {
            enigo.move_mouse(x, y, Coordinate::Abs)?;
            Ok(vec![json!({"type": "text", "text": "success"})])
        }
        "left_click" => {
            enigo.move_mouse(x, y, Coordinate::Abs)?;
            enigo.button(Button::Left, Direction::Click)?;
            Ok(vec![json!({"type": "text", "text": "success"})])
        }
        "right_click" => {
            enigo.move_mouse(x, y, Coordinate::Abs)?;
            enigo.button(Button::Right, Direction::Click)?;
            Ok(vec![json!({"type": "text", "text": "success"})])
        }
        "double_click" => {
            enigo.move_mouse(x, y, Coordinate::Abs)?;
            enigo.button(Button::Left, Direction::Click)?;
            enigo.button(Button::Left, Direction::Click)?;
            Ok(vec![json!({"type": "text", "text": "success"})])
        }
        "left_click_drag" => {
            // coordinate 是拖拽终点，从当前鼠标位置按下后移动
            enigo.button(Button::Left, Direction::Press)?;
            enigo.move_mouse(x, y, Coordinate::Abs)?;
            enigo.button(Button::Left, Direction::Release)?;
            Ok(vec![json!({"type": "text", "text": "success"})])
        }
        "type" => {
            let text = args["text"]
                .as_str()
                .ok_or_else(|| anyhow!("Missing text parameter"))?;
            enigo.text(text)?;
            Ok(vec![json!({"type": "text", "text": "success"})])
        }
        "key" => {
            let text = args["text"]
                .as_str()
                .ok_or_else(|| anyhow!("Missing text parameter"))?;
            // Basic key mapping for common special keys
            let key = match text.to_lowercase().as_str() {
                "return" | "enter" => Key::Return,
                "escape" | "esc" => Key::Escape,
                "tab" => Key::Tab,
                "space" => Key::Space,
                "backspace" => Key::Backspace,
                "delete" | "del" => Key::Delete,
                "up" => Key::UpArrow,
                "down" => Key::DownArrow,
                "left" => Key::LeftArrow,
                "right" => Key::RightArrow,
                "home" => Key::Home,
                "end" => Key::End,
                "pageup" | "page_up" => Key::PageUp,
                "pagedown" | "page_down" => Key::PageDown,
                "ctrl" | "control" => Key::Control,
                "alt" => Key::Alt,
                "shift" => Key::Shift,
                "meta" | "command" | "win" => Key::Meta,
                _ => {
                    // Try to parse as single char if it's length 1
                    if text.chars().count() == 1 {
                        let c = text.chars().next().unwrap();
                        Key::Unicode(c) // Use Unicode or Layout depending on enigo version
                    } else {
                        return Err(anyhow!("Unsupported key: {}", text));
                    }
                }
            };
            enigo.key(key, Direction::Click)?;
            Ok(vec![json!({"type": "text", "text": "success"})])
        }
        _ => Err(anyhow!("Action '{}' is not fully implemented yet", action)),
    }
}
