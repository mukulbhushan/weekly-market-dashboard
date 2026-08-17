import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_scanx_pages():
    async with async_playwright() as p:
        print("Launching Edge for ScanX scraping...")
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()

        # 1. Scrape Homepage
        print("Scraping Home page: https://scanx.trade/ ...")
        await page.goto("https://scanx.trade/", wait_until="networkidle", timeout=30000)
        home_text = await page.inner_text("body")
        print("\n--- HOME DATA ---")
        print(home_text[:1200])

        # 2. Scrape Stock Screener Page
        print("\nScraping Screener page: https://scanx.trade/stock-screener ...")
        await page.goto("https://scanx.trade/stock-screener", wait_until="networkidle", timeout=30000)
        screener_text = await page.inner_text("body")
        print("\n--- SCREENER DATA ---")
        print(screener_text[:1200])

        # 3. Scrape Insights Page
        print("\nScraping Insight page: https://scanx.trade/insight ...")
        await page.goto("https://scanx.trade/insight", wait_until="networkidle", timeout=30000)
        insight_text = await page.inner_text("body")
        print("\n--- INSIGHT DATA ---")
        print(insight_text[:1200])

        await browser.close()

if __name__ == '__main__':
    asyncio.run(scrape_scanx_pages())
