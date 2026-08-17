import asyncio
from playwright.async_api import async_playwright
import json
import re

async def scrape_scanx_full():
    async with async_playwright() as p:
        print("Launching Edge to scrape ScanX...")
        browser = await p.chromium.launch(channel="msedge", headless=True)
        page = await browser.new_page()

        # 1. Scrape Header Tickers off https://scanx.trade/
        print("Scraping Tickers from https://scanx.trade/ ...")
        await page.goto("https://scanx.trade/", wait_until="networkidle", timeout=30000)
        
        # Scrape index tickers
        ticker_data = []
        body_text = await page.inner_text("body")
        lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        
        target_indices = ['NIFTY 50', 'BANK NIFTY', 'FIN NIFTY', 'SENSEX', 'MIDCPNIFTY']
        for i, line in enumerate(lines):
            for t_idx in target_indices:
                if line.upper() == t_idx and i + 3 < len(lines):
                    close_val = lines[i+1]
                    pts_val = lines[i+2]
                    pct_val = lines[i+3]
                    ticker_data.append({
                        'name': t_idx,
                        'close': close_val,
                        'pts': pts_val,
                        'pct': pct_val
                    })
                    print(f"Scraped ScanX Ticker: {t_idx} -> Close: {close_val}, Pts: {pts_val}, Pct: {pct_val}")

        # 2. Scrape News off ScanX homepage
        news_items = []
        print("\nExtracting ScanX Latest Market News...")
        if 'Latest Market News' in body_text:
            idx_news = lines.index('Latest Market News') if 'Latest Market News' in lines else 0
            sub_lines = lines[idx_news:idx_news+30]
            for j in range(len(sub_lines)-2):
                if 'ago' in sub_lines[j] or 'just now' in sub_lines[j]:
                    title = sub_lines[j-1] if j > 0 else 'Corporate Update'
                    summary = sub_lines[j+1]
                    news_items.append({'title': title, 'time': sub_lines[j], 'summary': summary})

        print(f"Scraped {len(news_items)} news items from ScanX:")
        for n in news_items[:3]:
            print("  ", n['title'], "|", n['time'])

        await browser.close()
        return ticker_data, news_items

if __name__ == '__main__':
    asyncio.run(scrape_scanx_full())
