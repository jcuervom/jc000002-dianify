import re
import os
import glob
from playwright.async_api import async_playwright
from notifier import send_message
from config import HEADLESS

async def get_available_dates():
    async with async_playwright() as p:
        # Try to find the Chrome executable path for Heroku
        chromium_path = None
        
        # On Heroku, check for the buildpack-installed browsers
        if os.getenv("DYNO"):  # We're on Heroku
            # The playwright-community buildpack sets PLAYWRIGHT_BROWSERS_PATH
            browsers_path = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
            if browsers_path:
                print(f"🔍 Found PLAYWRIGHT_BROWSERS_PATH: {browsers_path}")
                # Look for chromium executable
                import glob
                chromium_pattern = os.path.join(browsers_path, "chromium-*/chrome-linux/chrome")
                matches = glob.glob(chromium_pattern)
                if matches:
                    chromium_path = matches[0]
                    print(f"🔍 Found Chromium at: {chromium_path}")
            
            # Fallback: try other common Heroku paths
            if not chromium_path:
                fallback_patterns = [
                    "/app/.cache/ms-playwright/chromium-*/chrome-linux/chrome",
                    "/tmp/playwright_browsers/chromium-*/chrome-linux/chrome"
                ]
                
                for pattern in fallback_patterns:
                    matches = glob.glob(pattern)
                    if matches:
                        chromium_path = matches[0]
                        print(f"🔍 Found Chromium via fallback: {chromium_path}")
                        break
        else:
            # Local development - let Playwright handle it automatically
            print("🔍 Running locally - using default Playwright browser")
        
        # Debug: print the path being used
        print(f"🔍 Using Chromium path: {chromium_path}")
        
        # Configuración robusta para Heroku
        browser_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-field-trial-config",
            "--disable-back-forward-cache",
            "--disable-ipc-flooding-protection",
            "--single-process"
        ]
        
        browser = await p.chromium.launch(
            headless=HEADLESS, 
            slow_mo=100,
            executable_path=chromium_path if chromium_path else None,
            args=browser_args
        )
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # Configurar timeouts más largos
        page.set_default_timeout(60000)  # 60 segundos
        page.set_default_navigation_timeout(60000)

        try:
            await page.goto("https://agendamiento.dian.gov.co/", wait_until="networkidle")
            await page.locator("#control_209").click()
            await page.locator("div").filter(has_text=re.compile(r"^PersonaNatural$")).first.click()
            await page.locator("div").filter(has_text=re.compile(r"^Videoatención$")).first.click()
            await page.locator(".contentImgCategoria > .img-fluid").first.click()
            await page.get_by_role("combobox").select_option("332")
            await page.locator("#control_205").click()
            await page.locator("#control_194").get_by_role("img").click()

            await page.wait_for_selector(".k-calendar", timeout=30000)
            calendario = await page.query_selector(".k-calendar")
            dias = []
            dia_agendado = None
            error_modal = False
            
            if calendario:
                dias_celdas = await calendario.query_selector_all("td:not(.k-state-disabled) a.k-link")
                for celda in dias_celdas:
                    texto = await celda.inner_text()
                    if texto.strip():
                        dias.append(texto.strip())

                # Intentar seleccionar cada día disponible
                for celda in dias_celdas:
                    try:
                        await celda.click()
                        # Esperar a ver si aparece el modal de error
                        modal = await page.query_selector("div[nombrepantalla='ModalError']")
                        if modal:
                            error_modal = True
                            btn_cerrar = await modal.query_selector("#control_39")
                            if btn_cerrar:
                                await btn_cerrar.click()
                            break
                        else:
                            dia_agendado = await celda.inner_text()
                            break
                    except Exception:
                        continue

            await browser.close()
            if error_modal:
                return {"error": True, "dias": dias, "dia_agendado": None}
            return {"error": False, "dias": dias, "dia_agendado": dia_agendado}
            
        except Exception as e:
            await browser.close()
            raise Exception(f"Error de navegación: {str(e)}")
