import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import os from "os";

let browser = null;
let page = null;

const server = new Server(
  {
    name: "polarisagi-browser-use",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

async function ensurePage() {
  if (!page || page.isClosed()) {
    try {
      // 尝试多平台多浏览器的动态调试端口获取
      const localAppData = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local');
      const portFiles = [
        path.join(os.homedir(), 'Library/Application Support/Google/Chrome/DevToolsActivePort'), // Mac Chrome
        path.join(os.homedir(), 'Library/Application Support/Microsoft Edge/DevToolsActivePort'), // Mac Edge
        path.join(localAppData, 'Google', 'Chrome', 'User Data', 'DevToolsActivePort'), // Win Chrome
        path.join(localAppData, 'Microsoft', 'Edge', 'User Data', 'DevToolsActivePort'), // Win Edge
      ];

      let port = 9222;
      for (const portFile of portFiles) {
        if (fs.existsSync(portFile)) {
          const content = fs.readFileSync(portFile, 'utf8');
          const lines = content.split('\n');
          if (lines.length > 0) {
            const parsedPort = parseInt(lines[0].trim(), 10);
            if (!isNaN(parsedPort)) {
              port = parsedPort;
              break;
            }
          }
        }
      }

      // 连接现有的 Chrome 或 Edge
      browser = await chromium.connectOverCDP(`http://127.0.0.1:${port}`);
      const contexts = browser.contexts();
      const context = contexts.length > 0 ? contexts[0] : await browser.newContext();
      const pages = context.pages();
      page = pages.length > 0 ? pages[0] : await context.newPage();
    } catch (e) {
      // 提供 Chrome 和 Edge 双平台的 UX 提示
      throw new Error(
        "Remote Debugging Required (需要开启远程调试)\n\n" +
        "To use browser tools, you need to enable remote debugging / 为了使用智能体的浏览器控制功能，您需要手动开启远程调试:\n\n" +
        "For Google Chrome (谷歌浏览器):\n" +
        "Navigate to chrome://inspect/#remote-debugging and enable 'Allow remote debugging for this browser instance'.\n" +
        "(请在地址栏输入 chrome://inspect/#remote-debugging ，然后勾选 'Allow remote debugging for this browser instance' 选项)\n\n" +
        "For Microsoft Edge (微软 Edge 浏览器):\n" +
        "Navigate to edge://inspect/#remote-debugging and enable 'Allow remote debugging for this browser instance'.\n" +
        "(请在地址栏输入 edge://inspect/#remote-debugging ，然后勾选 'Allow remote debugging for this browser instance' 选项)"
      );
    }
  }
  return page;
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "navigate",
        description: "Navigate to a URL and wait for it to load.",
        inputSchema: {
          type: "object",
          properties: {
            url: { type: "string" },
          },
          required: ["url"],
        },
      },
      {
        name: "get_interactive_dom",
        description: "Get a simplified interactive DOM tree (Accessibility Tree). Returns interactive elements with a unique 'polaris-id'. Use this to see what you can interact with instead of taking screenshots.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "action_by_id",
        description: "Perform an action (click, fill, hover) on an element using its 'polaris-id' obtained from get_interactive_dom.",
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "number", description: "The polaris-id of the element" },
            action: { type: "string", enum: ["click", "fill", "hover"] },
            text: { type: "string", description: "Text to fill (if action is fill)" },
          },
          required: ["id", "action"],
        },
      },
      {
        name: "scroll_page",
        description: "Scroll the page up or down by one viewport height.",
        inputSchema: {
          type: "object",
          properties: {
            direction: { type: "string", enum: ["down", "up"] },
          },
          required: ["direction"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const p = await ensurePage();

  try {
    if (name === "navigate") {
      await p.goto(args.url, { waitUntil: "domcontentloaded" });
      await p.waitForLoadState("networkidle").catch(() => {});
      return {
        content: [{ type: "text", text: `Navigated to ${args.url}` }],
      };
    }

    if (name === "get_interactive_dom") {
      // Inject JS to mark and extract interactive elements, supporting Shadow DOM and Out-of-Viewport
      const domTree = await p.evaluate(() => {
        let counter = 1;
        const result = [];
        const interactiveSelectors = 'a, button, input, select, textarea, [role="button"], [role="link"], [tabindex]:not([tabindex="-1"])';
        
        function processNode(node) {
          if (!node || !node.querySelectorAll) return;
          
          const elements = node.querySelectorAll(interactiveSelectors);
          elements.forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
              return;
            }

            const rect = el.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) return; // skip completely invisible

            // Check if in viewport
            const inViewport = rect.top >= 0 && rect.left >= 0 && 
                               rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && 
                               rect.right <= (window.innerWidth || document.documentElement.clientWidth);

            el.setAttribute('polaris-id', counter);
            
            let text = el.innerText || el.getAttribute('aria-label') || el.getAttribute('placeholder') || el.value || '';
            text = text.trim().substring(0, 50); // limit length
            
            if (!text && el.tagName === 'INPUT') {
              text = '[Input Field]';
            }

            if (text || el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') {
              result.push({
                id: counter,
                tag: el.tagName.toLowerCase(),
                role: el.getAttribute('role') || undefined,
                text: text,
                inViewport: inViewport
              });
            }
            counter++;
          });

          // Check shadow roots
          const allElements = node.querySelectorAll('*');
          allElements.forEach(el => {
            if (el.shadowRoot) {
              processNode(el.shadowRoot);
            }
          });
        }
        
        processNode(document);
        return result;
      });

      const formatted = domTree.map(e => `[ID: ${e.id}] <${e.tag}${e.role ? ` role="${e.role}"` : ''}> ${e.text} ${e.inViewport ? '' : '(Out of Viewport)'}`).join('\n');
      
      return {
        content: [{ type: "text", text: formatted || "No interactive elements found." }],
      };
    }

    if (name === "action_by_id") {
      const locator = p.locator(`[polaris-id="${args.id}"]`).first();
      
      // Ensure element is visible
      await locator.scrollIntoViewIfNeeded().catch(() => {});

      if (args.action === "click") {
        await locator.click({ force: true });
      } else if (args.action === "fill") {
        await locator.fill(args.text || "", { force: true });
      } else if (args.action === "hover") {
        await locator.hover({ force: true });
      }
      
      // Wait for potential network/DOM updates
      await p.waitForLoadState("networkidle").catch(() => {});
      await p.waitForTimeout(500);
      
      return {
        content: [{ type: "text", text: `Action ${args.action} performed successfully on element ID ${args.id}.` }],
      };
    }

    if (name === "scroll_page") {
      const direction = args.direction === "up" ? -1 : 1;
      await p.evaluate((dir) => {
        window.scrollBy(0, window.innerHeight * dir);
      }, direction);
      await p.waitForTimeout(500);
      return {
        content: [{ type: "text", text: `Scrolled ${args.direction}.` }],
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
server.connect(transport).catch(console.error);

process.on('SIGINT', async () => {
  if (browser) await browser.close();
  process.exit(0);
});
