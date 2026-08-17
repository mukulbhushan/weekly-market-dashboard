import asyncio
from playwright.async_api import async_playwright
import os

async def generate_pdf_test():
    async with async_playwright() as p:
        print("Rendering HTML Dashboard into PDF...")
        browser = await p.chromium.launch(channel="msedge", headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        html_path = os.path.abspath("weekly-market-dashboard.html")
        await page.goto(f"file:///{html_path}", wait_until="networkidle")

        pdf_path = "Weekly_Market_Dashboard_2026_08_14.pdf"
        await page.pdf(
            path=pdf_path,
            format="A3",
            landscape=True,
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
        )
        await browser.close()
        print(f"Generated PDF: '{pdf_path}', Size: {os.path.getsize(pdf_path)} bytes")

if __name__ == '__main__':
    asyncio.run(generate_pdf_test())
