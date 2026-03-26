import asyncio
import sys
from typing import Optional
from playwright.async_api import async_playwright


async def _render_pdf(html: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="networkidle")
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                scale=1.05,
                margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"},
            )
            return pdf_bytes
        finally:
            await browser.close()


def _run_pdf_sync(html: str) -> bytes:
    if sys.platform.startswith("win"):
        policy = asyncio.WindowsProactorEventLoopPolicy()
        loop = policy.new_event_loop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_render_pdf(html))
    finally:
        loop.close()


async def html_to_pdf(html: str, base_url: Optional[str] = None) -> bytes:
    return await asyncio.to_thread(_run_pdf_sync, html)
