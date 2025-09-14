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
            # En producción, mostrar menos debug info para acelerar startup
            print(f"🔍 CHROMIUM_EXECUTABLE_PATH: {repr(os.getenv('CHROMIUM_EXECUTABLE_PATH'))}")
            
            # Special case: if the logs show the path but Python doesn't see it, try direct path
            chromium_path = None
            buildpack_path = "/app/browsers/chromium-1091/chrome-linux/chrome"
            if os.path.exists(buildpack_path):
                print(f"🔍 Found Chromium at expected buildpack location: {buildpack_path}")
                chromium_path = buildpack_path
            
            # If not found by direct path, try environment variables
            if not chromium_path:
                # The heroku-playwright-python-browsers buildpack sets CHROMIUM_EXECUTABLE_PATH
                chromium_path = os.getenv("CHROMIUM_EXECUTABLE_PATH")
                # Filter out invalid values like "0" or empty strings
                if chromium_path and chromium_path != "0" and chromium_path.strip():
                    print(f"🔍 Using CHROMIUM_EXECUTABLE_PATH: {chromium_path}")
                    # Verify the path exists
                    if not os.path.exists(chromium_path):
                        print(f"⚠️ Chromium executable not found at: {chromium_path}")
                        chromium_path = None
                else:
                    chromium_path = None
            
            # Quick fallback if still not found
            if not chromium_path:
                print("🔍 Searching for Chromium in fallback locations...")
                fallback_patterns = [
                    "/app/browsers/chromium-*/chrome-linux/chrome",
                    "/app/.cache/ms-playwright/chromium-*/chrome-linux/chrome"
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
        
        # Configuración optimizada para Heroku (menos memoria)
        browser_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor,AudioServiceOutOfProcess",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-default-apps",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-translate",
            "--hide-scrollbars",
            "--metrics-recording-only",
            "--mute-audio",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
            "--disable-ipc-flooding-protection",
            "--memory-pressure-off",
            "--max_old_space_size=460",  # Limit memory usage
            "--single-process"  # Use single process to save memory
        ]
        
        browser = await p.chromium.launch(
            headless=True,  # Force headless on Heroku to save memory
            slow_mo=0,  # Remove slow_mo to speed up
            executable_path=chromium_path if chromium_path else None,
            args=browser_args
        )
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Disable images and CSS to save memory and speed up loading
            ignore_https_errors=True
        )
        
        page = await context.new_page()
        
        # Configurar timeouts más cortos para evitar que Heroku mate el proceso
        page.set_default_timeout(30000)  # 30 segundos
        page.set_default_navigation_timeout(30000)
        
        # Bloquear recursos innecesarios para ahorrar memoria y tiempo
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ttf}", lambda route: route.abort())

        try:
            print("🔍 Navigating to DIAN website...")
            await page.goto("https://agendamiento.dian.gov.co/", wait_until="domcontentloaded")  # Cambiar a domcontentloaded para ser más rápido
            
            print("🔍 Filling form...")
            await page.locator("#control_209").click()
            await page.locator("div").filter(has_text=re.compile(r"^PersonaNatural$")).first.click()
            await page.locator("div").filter(has_text=re.compile(r"^Videoatención$")).first.click()
            await page.locator(".contentImgCategoria > .img-fluid").first.click()
            await page.get_by_role("combobox").select_option("332")
            await page.locator("#control_205").click()
            await page.locator("#control_194").get_by_role("img").click()

            print("🔍 Waiting for calendar...")
            await page.wait_for_selector(".k-calendar", timeout=45000)  # Aumentar a 45 segundos
            calendario = await page.query_selector(".k-calendar")
            dias = []
            dia_agendado = None
            error_modal = False
            
            if calendario:
                print("✅ Calendario encontrado, buscando días disponibles...")
                dias_celdas = await calendario.query_selector_all("td:not(.k-state-disabled) a.k-link")
                print(f"🔍 Días disponibles encontrados: {len(dias_celdas)}")
                
                for celda in dias_celdas:
                    texto = await celda.inner_text()
                    if texto.strip():
                        dias.append(texto.strip())

                # Intentar seleccionar cada día disponible
                if dias_celdas:
                    print(f"🔍 Intentando hacer click en el primer día: {dias[0] if dias else 'Sin días'}")
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
                else:
                    print("ℹ️ No hay días disponibles en el calendario")
            else:
                print("❌ No se pudo encontrar el calendario")

            await browser.close()
            if error_modal:
                return {"error": True, "dias": dias, "dia_agendado": None}
            return {"error": False, "dias": dias, "dia_agendado": dia_agendado}
            
        except Exception as e:
            await browser.close()
            raise Exception(f"Error de navegación: {str(e)}")
