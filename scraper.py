import re
from playwright.async_api import async_playwright
from notifier import send_message
from config import HEADLESS

async def get_available_dates():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS, slow_mo=150)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://agendamiento.dian.gov.co/")
        await page.locator("#control_209").click()
        await page.locator("div").filter(has_text=re.compile(r"^PersonaNatural$")).first.click()
        await page.locator("div").filter(has_text=re.compile(r"^Videoatención$")).first.click()
        await page.locator(".contentImgCategoria > .img-fluid").first.click()
        await page.get_by_role("combobox").select_option("332")
        await page.locator("#control_205").click()
        await page.locator("#control_194").get_by_role("img").click()

        await page.wait_for_selector(".k-calendar")
        calendario = await page.query_selector(".k-calendar")
        dias = []
        if calendario:
            dias_celdas = await calendario.query_selector_all("td:not(.k-state-disabled) a.k-link")
            for celda in dias_celdas:
                texto = await celda.inner_text()
                if texto.strip():
                    dias.append(texto.strip())
        await browser.close()
        return dias
