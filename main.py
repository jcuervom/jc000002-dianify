#!/usr/bin/env python3


import asyncio
from scraper import get_available_dates
from notifier import send_message


import asyncio
import time


async def run_periodically():
    while True:
        try:
            resultado = await get_available_dates()
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
            print(f"Error en el proceso: {e}")
            await send_message(f"❌ Error en el bot de citas DIAN: {e}")
        await asyncio.sleep(300)  # Espera 5 minutos

if __name__ == "__main__":
    asyncio.run(run_periodically())
