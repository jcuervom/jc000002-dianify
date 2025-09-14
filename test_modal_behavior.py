#!/usr/bin/env python3

import re
import os
import glob
import sys
import asyncio

# Agregar el directorio padre al path para importar src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from src.config import HEADLESS

async def test_modal_behavior():
    """Test que simula el comportamiento del modal de error y reinicio de formulario"""
    async with async_playwright() as p:
        print("🔍 Running locally - using default Playwright browser")
        
        browser_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
        
        browser = await p.chromium.launch(
            headless=False,  # Mostrar navegador para ver el comportamiento
            slow_mo=1000,    # Ralentizar para ver cada acción
            args=browser_args
        )
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(60000)

        async def complete_form_and_get_calendar():
            """Función auxiliar para completar el formulario y obtener el calendario"""
            print("🔍 Navigating to DIAN website...")
            await page.goto("https://agendamiento.dian.gov.co/", wait_until="networkidle")
            
            print("🔍 Filling form...")
            await page.locator("#control_209").click()
            await page.locator("div").filter(has_text=re.compile(r"^PersonaNatural$")).first.click()
            await page.locator("div").filter(has_text=re.compile(r"^Videoatención$")).first.click()
            await page.locator(".contentImgCategoria > .img-fluid").first.click()
            await page.get_by_role("combobox").select_option("332")
            await page.locator("#control_205").click()
            await page.locator("#control_194").get_by_role("img").click()

            print("🔍 Waiting for calendar...")
            await page.wait_for_selector(".k-calendar", timeout=45000)
            return await page.query_selector(".k-calendar")

        try:
            # Completar formulario inicial
            calendario = await complete_form_and_get_calendar()
            
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

                # Intentar agendar con cada día disponible
                if dias:
                    print(f"🔍 Intentando agendar cita. Días disponibles: {dias}")
                    
                    for i, dia in enumerate(dias):
                        try:
                            print(f"🔍 Intentando día {dia} (intento {i+1}/{len(dias)})...")
                            
                            # Para el primer intento, usar el calendario ya cargado
                            # Para intentos posteriores, recompletar todo el formulario
                            if i > 0:
                                print("🔄 Recompletando formulario completo para el siguiente día...")
                                try:
                                    calendario = await complete_form_and_get_calendar()
                                    if not calendario:
                                        print("❌ No se pudo recompletar el formulario")
                                        continue
                                    
                                    # Re-obtener todos los días disponibles
                                    dias_celdas_actual = await calendario.query_selector_all("td:not(.k-state-disabled) a.k-link")
                                    
                                    # Buscar el día específico que queremos intentar
                                    celda_objetivo = None
                                    for celda in dias_celdas_actual:
                                        texto_celda = await celda.inner_text()
                                        if texto_celda.strip() == dia:
                                            celda_objetivo = celda
                                            break
                                    
                                    if not celda_objetivo:
                                        print(f"⚠️ El día {dia} ya no está disponible después de recompletar")
                                        continue
                                        
                                except Exception as e:
                                    print(f"❌ Error al recompletar formulario: {e}")
                                    continue
                            else:
                                # Primera vez, usar los días ya obtenidos del calendario inicial
                                celda_objetivo = dias_celdas[i]
                            
                            # Hacer click en el día
                            await celda_objetivo.click()
                            print(f"🔍 Click realizado en día {dia}, esperando respuesta...")
                            
                            # Esperar para ver si aparece modal de error
                            await page.wait_for_timeout(3000)
                            
                            modal = await page.query_selector("div[nombrepantalla='ModalError']")
                            if modal:
                                print(f"⚠️ Modal de error detectado para día {dia}")
                                print("📝 Texto del modal:")
                                modal_text = await modal.inner_text()
                                print(f"   {modal_text}")
                                
                                btn_cerrar = await modal.query_selector("#control_39")
                                if btn_cerrar:
                                    await btn_cerrar.click()
                                    print("🔄 Modal cerrado, esperando redirección...")
                                    await page.wait_for_timeout(3000)  # Esperar redirección
                                    
                                    # Verificar URL después del cierre del modal
                                    current_url = page.url
                                    print(f"🔍 URL después de cerrar modal: {current_url}")
                                
                                # El siguiente ciclo recompletará todo el formulario
                                continue
                            else:
                                # ¡Éxito! Se pudo agendar
                                dia_agendado = dia
                                print(f"✅ ¡Cita agendada exitosamente para el día {dia_agendado}!")
                                break
                                
                        except Exception as e:
                            print(f"❌ Error al intentar día {dia}: {e}")
                            # En caso de error, también intentar con el siguiente día
                            continue
                    
                    # Si se intentaron todos los días y ninguno funcionó
                    if not dia_agendado and dias:
                        print("⚠️ Se intentaron todos los días disponibles pero ninguno permitió agendar")
                        error_modal = True
                else:
                    print("ℹ️ No hay días disponibles en el calendario")
            else:
                print("❌ No se pudo encontrar el calendario")

            # Pausar antes de cerrar para ver el resultado final
            print("⏸️ Test completado. Presiona Enter para cerrar el navegador...")
            # input()  # Comentado para que no espere input en modo automatizado
            
            await browser.close()
            
            resultado = {
                "error": error_modal, 
                "dias": dias, 
                "dia_agendado": dia_agendado
            }
            print(f"🎯 Resultado final: {resultado}")
            return resultado
            
        except Exception as e:
            await browser.close()
            raise Exception(f"Error de navegación: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_modal_behavior())