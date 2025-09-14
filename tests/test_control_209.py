#!/usr/bin/env python3

import re
import os
import sys
import asyncio

# Agregar el directorio padre al path para importar src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright

async def test_control_209_click():
    """Test específico para verificar que #control_209 se clickea correctamente"""
    async with async_playwright() as p:
        print("🔍 Iniciando test específico para #control_209")
        
        browser = await p.chromium.launch(
            headless=False,  # Mostrar navegador
            slow_mo=2000     # Muy lento para ver cada acción claramente
        )
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        page.set_default_timeout(60000)

        async def complete_form_and_get_calendar_debug():
            """Versión debug de la función con logs detallados"""
            print("🔍 1. Navegando a DIAN website...")
            await page.goto("https://agendamiento.dian.gov.co/", wait_until="domcontentloaded")
            
            print("🔍 2. Esperando 2 segundos para carga completa...")
            await page.wait_for_timeout(2000)
            
            print("🔍 3. Buscando elemento #control_209...")
            try:
                await page.wait_for_selector("#control_209", timeout=10000)
                element = await page.query_selector("#control_209")
                if element:
                    print("✅ Elemento #control_209 encontrado")
                    is_visible = await element.is_visible()
                    is_enabled = await element.is_enabled()
                    print(f"   - Visible: {is_visible}")
                    print(f"   - Habilitado: {is_enabled}")
                else:
                    print("❌ Elemento #control_209 NO encontrado")
                    return None
            except Exception as e:
                print(f"❌ Error buscando #control_209: {e}")
                return None
            
            print("🔍 4. Haciendo click en #control_209...")
            try:
                await page.locator("#control_209").click()
                print("✅ Click en #control_209 realizado")
            except Exception as e:
                print(f"❌ Error haciendo click en #control_209: {e}")
                return None
            
            print("🔍 5. Continuando con el resto del formulario...")
            await page.wait_for_timeout(1000)
            await page.locator("div").filter(has_text=re.compile(r"^PersonaNatural$")).first.click()
            print("✅ PersonaNatural seleccionado")
            
            await page.wait_for_timeout(1000)
            await page.locator("div").filter(has_text=re.compile(r"^Videoatención$")).first.click()
            print("✅ Videoatención seleccionado")
            
            await page.wait_for_timeout(1000)
            await page.locator(".contentImgCategoria > .img-fluid").first.click()
            print("✅ Imagen clickeada")
            
            await page.wait_for_timeout(1000)
            await page.get_by_role("combobox").select_option("332")
            print("✅ Opción 332 seleccionada")
            
            await page.wait_for_timeout(1000)
            await page.locator("#control_205").click()
            print("✅ Control 205 clickeado")
            
            await page.wait_for_timeout(1000)
            await page.locator("#control_194").get_by_role("img").click()
            print("✅ Control 194 imagen clickeada")

            print("🔍 6. Esperando calendario...")
            try:
                await page.wait_for_selector(".k-calendar", timeout=45000)
                calendario = await page.query_selector(".k-calendar")
                if calendario:
                    print("✅ Calendario encontrado")
                    return calendario
                else:
                    print("❌ Calendario no encontrado")
                    return None
            except Exception as e:
                print(f"❌ Error esperando calendario: {e}")
                return None

        try:
            # Test 1: Completar formulario inicial
            print("\n" + "="*50)
            print("TEST 1: FORMULARIO INICIAL")
            print("="*50)
            calendario1 = await complete_form_and_get_calendar_debug()
            
            if calendario1:
                # Simular un click en un día para provocar un "error"
                print("\n🔍 Simulando click en primer día disponible...")
                dias_celdas = await calendario1.query_selector_all("td:not(.k-state-disabled) a.k-link")
                if dias_celdas:
                    await dias_celdas[0].click()
                    print("✅ Click en primer día realizado")
                    
                    # Esperar un momento y simular el comportamiento de cierre de modal
                    await page.wait_for_timeout(3000)
                    print("🔍 (Simulando que se cerró un modal y hubo redirección...)")
                    
                    # Test 2: Intentar recompletar formulario
                    print("\n" + "="*50)
                    print("TEST 2: RECOMPLETADO DE FORMULARIO")
                    print("="*50)
                    calendario2 = await complete_form_and_get_calendar_debug()
                    
                    if calendario2:
                        print("✅ ¡ÉXITO! El formulario se recompletó correctamente")
                    else:
                        print("❌ FALLO: No se pudo recompletar el formulario")
                else:
                    print("⚠️ No hay días disponibles para probar")
            else:
                print("❌ FALLO: No se pudo completar el formulario inicial")

            print("\n⏸️ Test completado. Presiona Enter para cerrar...")
            input()
            
        except Exception as e:
            print(f"❌ Error en test: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_control_209_click())