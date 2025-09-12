#!/usr/bin/env python3

import re
import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
import telegram

# Cargar variables del .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "false"

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise EnvironmentError("Faltan TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en el archivo .env")

bot = telegram.Bot(token=TELEGRAM_TOKEN)

async def run():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=HEADLESS, slow_mo=150)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://agendamiento.dian.gov.co/")

            # Flujo de navegación
            await page.locator("#control_209").click()
            await page.locator("div").filter(has_text=re.compile(r"^PersonaNatural$")).first.click()
            await page.locator("div").filter(has_text=re.compile(r"^Videoatención$")).first.click()
            await page.locator(".contentImgCategoria > .img-fluid").first.click()
            await page.get_by_role("combobox").select_option("332")
            await page.locator("#control_205").click()
            await page.locator("#control_194").get_by_role("img").click()

            # Esperar a que cargue el calendario (nuevo selector)
            await page.wait_for_selector(".k-calendar")
            calendario = await page.query_selector(".k-calendar")
            dias = []
            if calendario:
                # Extraer días disponibles: celdas <td> con enlaces <a> habilitados
                dias_celdas = await calendario.query_selector_all("td:not(.k-state-disabled) a.k-link")
                for celda in dias_celdas:
                    texto = await celda.inner_text()
                    if texto.strip():
                        dias.append(texto.strip())

            if dias:
                mensaje = f"✅ ¡Hay citas disponibles en DIAN! Días: {', '.join(dias)}"
                await bot.send_message(chat_id=CHAT_ID, text=mensaje)
                print(mensaje)
            else:
                print("No hay citas disponibles.")

            await browser.close()
    except Exception as e:
        print(f"Error en el proceso: {e}")
        await bot.send_message(chat_id=CHAT_ID, text=f"❌ Error en el bot de citas DIAN: {e}")

if __name__ == "__main__":
    asyncio.run(run())
