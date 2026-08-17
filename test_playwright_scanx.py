import asyncio
from playwright.async_api import async_playwright
import json

async def test_playwright_scanx():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        requests_log = []
        
        # Intercept network requests to capture internal API calls
        def handle_request(request):
            url = request.url
            if 'api' in url or 'dhan' in url or 'scan' in url or 'json' in url or 'trade' in url:
                requests_log.append({
                    'url': url,
                    'method': request.method,
                    'resource_type': request.resource_type
                })

        page.on("request", handle_request)
        
        print("Navigating to https://scanx.trade/ ...")
        await page.goto("https://scanx.trade/", wait_until="networkidle", timeout=30000)
        
        title = await page.title()
        print("Page Title:", title)
        
        # Capture DOM text / elements
        body_text = await page.inner_text("body")
        print("Body text snippet (first 500 chars):\n", body_text[:500])
        
        print(f"\nCaptured {len(requests_log)} network requests during rendering:")
        for req in requests_log[:20]:
            print("  ", req['method'], req['url'])
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_playwright_scanx())
