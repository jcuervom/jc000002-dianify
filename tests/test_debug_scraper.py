#!/usr/bin/env python3

import re
import os
import glob
import sys

# Agregar el directorio padre al path para importar src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from src.notifier import send_message
from src.config import HEADLESS

async def get_available_dates_debug():
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
        
        # Configuración más permisiva para debug
        browser_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
        
        if os.getenv("DYNO"):  # Solo en Heroku usar configuración estricta
            browser_args.extend([
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
                "--max_old_space_size=460",
                "--single-process"
            ])
        
        browser = await p.chromium.launch(
            headless=True if os.getenv("DYNO") else False,  # Headless en Heroku, con head en local
            slow_mo=0,
            executable_path=chromium_path if chromium_path else None,
            args=browser_args
        )
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        
        page = await context.new_page()
        
        # Configurar timeouts
        timeout_val = 30000 if os.getenv("DYNO") else 60000
        page.set_default_timeout(timeout_val)
        page.set_default_navigation_timeout(timeout_val)
        
        # Solo bloquear recursos en Heroku
        if os.getenv("DYNO"):
            await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ttf}", lambda route: route.abort())

        try:
            print("🔍 Navigating to DIAN website...")
            wait_strategy = "domcontentloaded" if os.getenv("DYNO") else "networkidle"
            await page.goto("https://agendamiento.dian.gov.co/", wait_until=wait_strategy)
            
            print("🔍 Filling form...")
            await page.locator("#control_209").click()
            await page.locator("div").filter(has_text=re.compile(r"^PersonaNatural$")).first.click()
            await page.locator("div").filter(has_text=re.compile(r"^Videoatención$")).first.click()
            await page.locator(".contentImgCategoria > .img-fluid").first.click()
            await page.get_by_role("combobox").select_option("332")
            await page.locator("#control_205").click()
            await page.locator("#control_194").get_by_role("img").click()

            print("🔍 Waiting for calendar...")
            
            # Debug detallado del calendario
            try:
                print("🔍 Esperando que aparezca el calendario...")
                calendario = await page.wait_for_selector(".k-calendar", timeout=timeout_val)
                print("✅ Calendario encontrado!")
                
                # Verificar si el calendario tiene contenido
                calendar_html = await calendario.inner_html()
                print(f"🔍 Calendario HTML length: {len(calendar_html)}")
                
                # Buscar días disponibles
                print("🔍 Buscando días disponibles...")
                dias_celdas = await calendario.query_selector_all("td:not(.k-state-disabled) a.k-link")
                print(f"🔍 Días encontrados: {len(dias_celdas)}")
                
                dias = []
                for i, celda in enumerate(dias_celdas):
                    texto = await celda.inner_text()
                    if texto.strip():
                        dias.append(texto.strip())
                        print(f"🔍 Día {i+1}: {texto.strip()}")

                # Intentar hacer click en cada día disponible hasta encontrar uno que funcione
                dia_agendado = None
                error_modal = False
                
                if dias_celdas:
                    print(f"🔍 Intentando agendar cita. Días disponibles: {dias}")
                    
                    for i, celda in enumerate(dias_celdas):
                        dia_actual = dias[i] if i < len(dias) else f"día {i+1}"
                        try:
                            print(f"🔍 Intentando día {dia_actual}...")
                            
                            # Verificar que la página sigue accesible
                            try:
                                await page.wait_for_selector(".k-calendar", timeout=5000)
                            except:
                                print("⚠️ El calendario ya no está disponible, posible redirección")
                                break
                            
                            # Re-obtener los elementos del calendario por si la página cambió
                            calendario_actual = await page.query_selector(".k-calendar")
                            if not calendario_actual:
                                print("⚠️ No se puede encontrar el calendario actual")
                                break
                                
                            dias_celdas_actual = await calendario_actual.query_selector_all("td:not(.k-state-disabled) a.k-link")
                            if i >= len(dias_celdas_actual):
                                print(f"⚠️ El día {dia_actual} ya no está disponible")
                                continue
                            
                            celda_actual = dias_celdas_actual[i]
                            await celda_actual.click()
                            print(f"🔍 Click realizado en día {dia_actual}, esperando respuesta...")
                            
                            # Esperar un momento para ver si aparece modal de error
                            await page.wait_for_timeout(2000)
                            
                            modal = await page.query_selector("div[nombrepantalla='ModalError']")
                            if modal:
                                print(f"⚠️ Error al intentar agendar día {dia_actual}")
                                btn_cerrar = await modal.query_selector("#control_39")
                                if btn_cerrar:
                                    await btn_cerrar.click()
                                    await page.wait_for_timeout(1000)  # Esperar que se cierre el modal
                                # Continuar con el siguiente día
                                continue
                            else:
                                # ¡Éxito! Se pudo agendar
                                dia_agendado = dia_actual
                                print(f"✅ ¡Cita agendada exitosamente para el día {dia_agendado}!")
                                break
                        except Exception as click_error:
                            print(f"❌ Error al hacer click en día {dia_actual}: {click_error}")
                            # Si hay un error, intentar recargar el calendario
                            try:
                                await page.wait_for_timeout(2000)
                                await page.reload()
                                await page.wait_for_selector(".k-calendar", timeout=10000)
                                print("🔄 Página recargada, intentando continuar...")
                            except:
                                print("❌ No se pudo recargar la página")
                                break
                            continue
                    
                    # Si se intentaron todos los días y ninguno funcionó
                    if not dia_agendado and dias:
                        print("⚠️ Se intentaron todos los días disponibles pero ninguno permitió agendar")
                        error_modal = True

                await browser.close()
                
                resultado = {
                    "error": error_modal, 
                    "dias": dias, 
                    "dia_agendado": dia_agendado
                }
                print(f"🎯 Resultado final: {resultado}")
                return resultado
                
            except Exception as calendar_error:
                print(f"❌ Error esperando calendario: {calendar_error}")
                
                # Debug: verificar qué hay en la página
                page_content = await page.content()
                print(f"🔍 Página contiene 'calendar': {'calendar' in page_content.lower()}")
                print(f"🔍 Página contiene 'k-calendar': {'k-calendar' in page_content}")
                
                # Intentar selectores alternativos
                print("🔍 Intentando selectores alternativos...")
                selectors = [
                    ".k-calendar",
                    "[data-role='calendar']",
                    ".calendar",
                    "#calendar",
                    "[class*='calendar']"
                ]
                
                for selector in selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            print(f"✅ Encontrado elemento con selector: {selector}")
                        else:
                            print(f"❌ No encontrado: {selector}")
                    except:
                        print(f"❌ Error con selector: {selector}")
                
                await browser.close()
                raise calendar_error
            
        except Exception as e:
            await browser.close()
            raise Exception(f"Error de navegación: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(get_available_dates_debug())