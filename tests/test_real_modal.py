#!/usr/bin/env python3

import re
import os
import sys
import asyncio

# Agregar el directorio padre al path para importar src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright

async def test_real_modal_scenario():
    """Test que intenta provocar un modal real y verificar el comportamiento"""
    async with async_playwright() as p:
        print("🔍 Test de escenario real con modal")
        
        browser = await p.chromium.launch(
            headless=False,  # Mostrar navegador
            slow_mo=1500     # Ralentizar para ver cada acción
        )
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        page.set_default_timeout(60000)

        async def complete_form_and_get_calendar_debug():
            """Versión debug de la función"""
            print(f"🔍 URL actual: {page.url}")
            print("🔍 1. Navegando a DIAN website...")
            await page.goto("https://agendamiento.dian.gov.co/", wait_until="domcontentloaded")
            
            print("🔍 2. Esperando carga completa...")
            await page.wait_for_timeout(2000)
            
            print("🔍 3. Verificando y clickeando #control_209...")
            await page.wait_for_selector("#control_209", timeout=10000)
            await page.locator("#control_209").click()
            print("✅ #control_209 clickeado")
            
            await page.wait_for_timeout(1000)
            await page.locator("div").filter(has_text=re.compile(r"^PersonaNatural$")).first.click()
            print("✅ PersonaNatural")
            
            await page.wait_for_timeout(1000)
            await page.locator("div").filter(has_text=re.compile(r"^Videoatención$")).first.click()
            print("✅ Videoatención")
            
            await page.wait_for_timeout(1000)
            await page.locator(".contentImgCategoria > .img-fluid").first.click()
            print("✅ Imagen")
            
            await page.wait_for_timeout(1000)
            await page.get_by_role("combobox").select_option("332")
            print("✅ Opción 332")
            
            await page.wait_for_timeout(1000)
            await page.locator("#control_205").click()
            print("✅ Control 205")
            
            await page.wait_for_timeout(1000)
            await page.locator("#control_194").get_by_role("img").click()
            print("✅ Control 194")

            print("🔍 4. Esperando calendario...")
            await page.wait_for_selector(".k-calendar", timeout=45000)
            return await page.query_selector(".k-calendar")

        try:
            # Completar formulario inicial
            print("\n" + "="*60)
            print("COMPLETANDO FORMULARIO INICIAL")
            print("="*60)
            calendario = await complete_form_and_get_calendar_debug()
            
            if calendario:
                # Obtener días disponibles
                dias_celdas = await calendario.query_selector_all("td:not(.k-state-disabled) a.k-link")
                print(f"🔍 Días disponibles: {len(dias_celdas)}")
                
                if dias_celdas:
                    # Intentar varios días para ver si alguno genera modal
                    for i, celda in enumerate(dias_celdas[:3]):  # Solo probar primeros 3
                        texto = await celda.inner_text()
                        print(f"\n🔍 Intentando día {texto} (#{i+1})...")
                        
                        # Si no es el primer intento, recompletar formulario
                        if i > 0:
                            print("\n" + "="*60)
                            print(f"RECOMPLETANDO FORMULARIO PARA DÍA {texto}")
                            print("="*60)
                            
                            calendario_nuevo = await complete_form_and_get_calendar_debug()
                            if not calendario_nuevo:
                                print("❌ Fallo al recompletar formulario")
                                continue
                                
                            # Re-obtener los días
                            dias_celdas_nuevo = await calendario_nuevo.query_selector_all("td:not(.k-state-disabled) a.k-link")
                            
                            # Buscar el día específico
                            celda_objetivo = None
                            for celda_nueva in dias_celdas_nuevo:
                                texto_nuevo = await celda_nueva.inner_text()
                                if texto_nuevo.strip() == texto.strip():
                                    celda_objetivo = celda_nueva
                                    break
                            
                            if not celda_objetivo:
                                print(f"⚠️ Día {texto} ya no disponible")
                                continue
                        else:
                            celda_objetivo = celda
                        
                        # Hacer click en el día
                        await celda_objetivo.click()
                        print(f"✅ Click en día {texto} realizado")
                        
                        # Esperar posible modal
                        print("🔍 Esperando posible modal de error...")
                        await page.wait_for_timeout(4000)
                        
                        # Buscar modal
                        modal = await page.query_selector("div[nombrepantalla='ModalError']")
                        if modal:
                            print(f"⚠️ ¡MODAL DE ERROR DETECTADO para día {texto}!")
                            
                            # Mostrar contenido del modal
                            modal_text = await modal.inner_text()
                            print(f"📄 Contenido del modal: {modal_text[:200]}...")
                            
                            # Cerrar modal
                            btn_cerrar = await modal.query_selector("#control_39")
                            if btn_cerrar:
                                print("🔄 Cerrando modal...")
                                await btn_cerrar.click()
                                
                                # Esperar redirección
                                print("🔍 Esperando redirección...")
                                for wait_time in range(10):
                                    await page.wait_for_timeout(1000)
                                    try:
                                        control_209 = await page.query_selector("#control_209")
                                        if control_209:
                                            is_visible = await control_209.is_visible()
                                            if is_visible:
                                                print(f"✅ Redirección completada en {wait_time + 1} segundos")
                                                print(f"🔍 URL después de redirección: {page.url}")
                                                break
                                    except:
                                        pass
                                else:
                                    print("⚠️ Redirección no detectada después de 10 segundos")
                            
                            # Continuar con el siguiente día
                            continue
                        else:
                            print(f"✅ ¡Sin modal! Día {texto} parece exitoso")
                            break
                            
                    print("\n🏁 Test completado")
                else:
                    print("⚠️ No hay días disponibles")
            else:
                print("❌ No se pudo obtener calendario inicial")

            print("\n⏸️ Presiona Enter para cerrar...")
            input()
            
        except Exception as e:
            print(f"❌ Error en test: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_real_modal_scenario())