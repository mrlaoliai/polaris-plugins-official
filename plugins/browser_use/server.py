import asyncio
import base64
import sys
import json
from mcp.server.fastmcp import FastMCP
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig

# Create FastMCP server
mcp = FastMCP("browser-use-mcp", version="0.1.0")

# Global browser instance
_browser = None
_context = None

async def get_browser_context():
    global _browser, _context
    if _browser is None:
        _browser = Browser(config=BrowserConfig(headless=True))
        _context = await _browser.new_context(config=BrowserContextConfig())
    return _context

@mcp.tool()
async def browser_use_action(action: str, url: str = None, selector: str = None, text: str = None) -> dict:
    """
    Execute browser actions like navigating, clicking, typing, and taking screenshots.
    
    Args:
        action: The action to perform (navigate, click, type, screenshot)
        url: URL to navigate to (if action=navigate)
        selector: CSS/XPath selector (if action=click or type)
        text: Text to type (if action=type)
    """
    context = await get_browser_context()
    page = await context.get_current_page()
    
    try:
        if action == "navigate":
            if not url:
                return {"error": "Missing 'url' parameter for navigate action"}
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            return {"content": [{"type": "text", "text": f"Successfully navigated to {url}"}]}
            
        elif action == "click":
            if not selector:
                return {"error": "Missing 'selector' parameter for click action"}
            await page.click(selector)
            return {"content": [{"type": "text", "text": "Click successful"}]}
            
        elif action == "type":
            if not selector or not text:
                return {"error": "Missing 'selector' or 'text' for type action"}
            await page.fill(selector, text)
            return {"content": [{"type": "text", "text": "Type successful"}]}
            
        elif action == "screenshot":
            screenshot_bytes = await page.screenshot(full_page=False)
            b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")
            return {
                "content": [{
                    "type": "image",
                    "data": b64_img,
                    "mimeType": "image/png"
                }]
            }
            
        else:
            return {"error": f"Unknown action: {action}"}
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()
