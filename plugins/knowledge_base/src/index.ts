#!/usr/bin/env node
import * as readline from 'readline';
import * as fs from 'fs/promises';
import * as path from 'path';

// Allowed directory validation
const allowedDir = process.env.POLARISAGI_KB_ALLOWED_DIR;

function isPathAllowed(targetPath: string): boolean {
    if (!allowedDir) {
        return true;
    }
    const absPath = path.resolve(targetPath);
    const rootPath = path.resolve(allowedDir);
    return absPath === rootPath || absPath.startsWith(rootPath + path.sep);
}

// MCP JSON-RPC setup
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

function sendResult(id: number | string, result: any) {
    const msg = {
        jsonrpc: "2.0",
        id,
        result
    };
    console.log(JSON.stringify(msg));
}

function sendError(id: number | string, code: number, message: string) {
    const msg = {
        jsonrpc: "2.0",
        id,
        error: { code, message }
    };
    console.log(JSON.stringify(msg));
}

rl.on('line', async (line) => {
    if (!line.trim()) return;
    try {
        const req = JSON.parse(line);
        if (req.jsonrpc !== "2.0" || !req.method || req.id === undefined) {
            return;
        }

        const id = req.id;

        if (req.method === "initialize") {
            sendResult(id, {
                protocolVersion: "2024-11-05",
                capabilities: { tools: {} },
                serverInfo: {
                    name: "polarisagi-knowledge-base-mcp",
                    version: "0.1.0"
                }
            });
        } else if (req.method === "tools/list") {
            sendResult(id, {
                tools: [
                    {
                        name: "list_files",
                        description: "List files in a given directory path",
                        inputSchema: {
                            type: "object",
                            properties: {
                                path: {
                                    type: "string",
                                    description: "The absolute path to the directory"
                                }
                            },
                            required: ["path"]
                        }
                    },
                    {
                        name: "read_content",
                        description: "Read the textual content of a specific file",
                        inputSchema: {
                            type: "object",
                            properties: {
                                path: {
                                    type: "string",
                                    description: "The absolute path to the file"
                                }
                            },
                            required: ["path"]
                        }
                    }
                ]
            });
        } else if (req.method === "tools/call") {
            const params = req.params || {};
            const args = params.arguments || {};

            if (params.name === "list_files") {
                const targetPath = args.path;
                if (typeof targetPath !== "string") {
                    sendResult(id, { isError: true, content: [{ type: "text", text: "path is required and must be a string" }] });
                    return;
                }
                if (!isPathAllowed(targetPath)) {
                    sendResult(id, { isError: true, content: [{ type: "text", text: "path is outside the allowed directory (POLARISAGI_KB_ALLOWED_DIR)" }] });
                    return;
                }

                try {
                    const entries = await fs.readdir(targetPath, { withFileTypes: true });
                    const fileNames = entries.map(e => e.isDirectory() ? `${e.name}/` : e.name);
                    const result = `Files in ${targetPath}:\n${fileNames.join('\n')}`;
                    sendResult(id, { content: [{ type: "text", text: result }] });
                } catch (err: any) {
                    sendResult(id, { isError: true, content: [{ type: "text", text: `failed to read dir: ${err.message}` }] });
                }

            } else if (params.name === "read_content") {
                const targetPath = args.path;
                if (typeof targetPath !== "string") {
                    sendResult(id, { isError: true, content: [{ type: "text", text: "path is required and must be a string" }] });
                    return;
                }
                if (!isPathAllowed(targetPath)) {
                    sendResult(id, { isError: true, content: [{ type: "text", text: "path is outside the allowed directory (POLARISAGI_KB_ALLOWED_DIR)" }] });
                    return;
                }

                try {
                    const data = await fs.readFile(targetPath, 'utf8');
                    sendResult(id, { content: [{ type: "text", text: data }] });
                } catch (err: any) {
                    sendResult(id, { isError: true, content: [{ type: "text", text: `failed to read file: ${err.message}` }] });
                }

            } else {
                sendError(id, -32601, `Tool not found: ${params.name}`);
            }
        } else {
            sendError(id, -32601, "Method not found");
        }
    } catch (e: any) {
        // ignore parse errors or malformed json
    }
});
