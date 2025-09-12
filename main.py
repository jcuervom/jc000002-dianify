#!/usr/bin/env python3


import asyncio
from scraper import get_available_dates
from notifier import send_message

async def run():
    try:
        dias = await get_available_dates()
        if dias:
            mensaje = f"✅ ¡Hay citas disponibles en DIAN! Días: {', '.join(dias)}"
            await send_message(mensaje)
            print(mensaje)
        else:
            print("No hay citas disponibles.")
    except Exception as e:
        print(f"Error en el proceso: {e}")
        await send_message(f"❌ Error en el bot de citas DIAN: {e}")

if __name__ == "__main__":
    asyncio.run(run())
