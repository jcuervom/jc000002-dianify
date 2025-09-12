#!/usr/bin/env python3


import asyncio
from scraper import get_available_dates
from notifier import send_message


import asyncio
import time


async def run_periodically():
    consecutive_errors = 0
    max_consecutive_errors = 3
    
    while True:
        try:
            print(f"🔍 Iniciando verificación de citas... {time.strftime('%Y-%m-%d %H:%M:%S')}")
            resultado = await get_available_dates()
            
            # Reset error counter on success
            consecutive_errors = 0
            
            if resultado["error"]:
                print("No hay agendas disponibles.")
            elif resultado["dia_agendado"]:
                mensaje = f"✅ ¡Hay agenda disponible el día {resultado['dia_agendado']}!"
                await send_message(mensaje)
                print(mensaje)
            elif resultado["dias"]:
                mensaje = f"✅ ¡Hay citas disponibles en DIAN! Días: {', '.join(resultado['dias'])}"
                await send_message(mensaje)
                print(mensaje)
            else:
                print("No hay citas disponibles.")
                
        except Exception as e:
            consecutive_errors += 1
            error_msg = f"Error en el proceso: {e}"
            print(error_msg)
            
            # Solo enviar notificación si es el primer error o cada 3 errores consecutivos
            if consecutive_errors == 1 or consecutive_errors % 3 == 0:
                await send_message(f"❌ Error en el bot de citas DIAN (#{consecutive_errors}): {e}")
            
            # Si hay demasiados errores consecutivos, esperar más tiempo
            if consecutive_errors >= max_consecutive_errors:
                wait_time = min(1800, 300 * consecutive_errors)  # Max 30 min
                print(f"⚠️ Demasiados errores consecutivos. Esperando {wait_time//60} minutos...")
                await asyncio.sleep(wait_time)
                continue
        
        # Espera normal de 5 minutos
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(run_periodically())
