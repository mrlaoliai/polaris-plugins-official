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
      let endpointUrl = `http://127.0.0.1:${port}`;
      for (const portFile of portFiles) {
        if (fs.existsSync(portFile)) {
          const content = fs.readFileSync(portFile, 'utf8');
          const lines = content.split('\n');
          if (lines.length > 0) {
            const parsedPort = parseInt(lines[0].trim(), 10);
            if (!isNaN(parsedPort)) {
              port = parsedPort;
              endpointUrl = `http://127.0.0.1:${port}`;
              if (lines.length > 1 && lines[1].trim().startsWith('/devtools/')) {
                endpointUrl = `ws://127.0.0.1:${port}${lines[1].trim()}`;
              }
              break;
            }
          }
        }
      }

      // 连接现有的 Chrome 或 Edge
      browser = await chromium.connectOverCDP(endpointUrl);
      const contexts = browser.contexts();
      const context = contexts.length > 0 ? contexts[0] : await browser.newContext();
      
      // 监听新标签页的开启，并自动切换控制权
      context.on('page', newPage => {
        console.log("New tab opened, switching to it.");
        page = newPage;
      });

      // 总是打开新标签页，避免覆盖用户当前正在浏览的页面
      page = await context.newPage();
    } catch (e) {
      console.log("Failed to connect via CDP, launching a new browser instance...", e.message);
      // Fallback to launching a new visible browser instead of throwing an error
      browser = await chromium.launch({ headless: false });
      const contexts = browser.contexts();
      const context = contexts.length > 0 ? contexts[0] : await browser.newContext();
      
      context.on('page', newPage => {
        console.log("New tab opened, switching to it.");
        page = newPage;
      });

      page = await context.newPage();
    }
  }
  return page;
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "navigate",
        description: "Navigate to a URL and wait for it to load. The URL must be a full, valid URL starting with http:// or https://",
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
        description: "Get a simplified interactive DOM tree. Returns ONLY interactive elements (links, buttons, inputs) with a unique 'polaris-id'. Use this ONLY when you need to find an element to click or fill. To read the main text content of the page, use get_page_content instead.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "action_by_id",
        description: "Perform an action on an element using its 'polaris-id' obtained from get_interactive_dom. 'fill' clears the input first. 'fill_and_enter' is highly recommended for search boxes to automatically submit.",
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "number", description: "The polaris-id of the element" },
            action: { type: "string", enum: ["click", "fill", "fill_and_enter", "hover"] },
            text: { type: "string", description: "Text to fill (if action is fill or fill_and_enter)" },
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
      {
        name: "go_back",
        description: "Go back to the previous page in the browser history.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "close_tab",
        description: "Close the current active tab and switch to the previous one. Use this when you are done reading a link that opened in a new tab.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "get_page_content",
        description: "Get the visible text content of the current page. Use this to read articles, search results, or extract information.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "get_current_state",
        description: "Get the current URL and page title to know exactly which page you are currently on.",
        inputSchema: {
          type: "object",
          properties: {},
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

    if (name === "get_page_content") {
      const text = await p.evaluate(() => document.body.innerText || "");
      return {
        content: [{ type: "text", text: text.substring(0, 40000) }], // limit to 40k chars to prevent context overflow
      };
    }

    if (name === "get_current_state") {
      const url = p.url();
      const title = await p.title();
      return {
        content: [{ type: "text", text: `URL: ${url}\nTitle: ${title}` }],
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
      } else if (args.action === "fill_and_enter") {
        await locator.fill(args.text || "", { force: true });
        await locator.press("Enter");
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

    if (name === "go_back") {
      await p.goBack({ waitUntil: "domcontentloaded" }).catch(() => {});
      await p.waitForLoadState("networkidle").catch(() => {});
      return {
        content: [{ type: "text", text: "Navigated back." }],
      };
    }

    if (name === "close_tab") {
      await p.close();
      const pages = p.context().pages();
      if (pages.length > 0) {
        page = pages[pages.length - 1]; // Switch to the last available tab
        return {
          content: [{ type: "text", text: "Tab closed. Switched to previous tab." }],
        };
      } else {
        page = await p.context().newPage();
        return {
          content: [{ type: "text", text: "Tab closed. Opened a new empty tab as no other tabs were left." }],
        };
      }
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
