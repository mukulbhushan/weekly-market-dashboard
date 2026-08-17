import asyncio
from playwright.async_api import async_playwright
import json

async def test_edge_scanx():
    async with async_playwright() as p:
        print("Launching Edge browser...")
        try:
            browser = await p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            print("Fallback to Chrome...")
            browser = await p.chromium.launch(channel="chrome", headless=True)
            
        page = await browser.new_page()
        
        requests_log = []
        responses_log = []
        
        def handle_response(response):
            url = response.url
            if 'dhan' in url or 'scan' in url or 'api' in url or 'screener' in url:
                responses_log.append({
                    'url': url,
                    'status': response.status
                })

        page.on("response", handle_response)
        
        print("Navigating to https://scanx.trade/ ...")
        await page.goto("https://scanx.trade/", wait_until="networkidle", timeout=30000)
        
        title = await page.title()
        print("Page Title:", title)
        
        # Scrape text content of the page
        content = await page.inner_text("body")
        print("\n=== SCANX PAGE BODY TEXT SNIPPET ===")
        print(content[:1000])
        
        print(f"\nCaptured {len(responses_log)} responses:")
        for r in responses_log[:25]:
            print(" ", r['status'], r['url'])
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_edge_scanx())
