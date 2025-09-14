#!/usr/bin/env python3

import sys
import os
import asyncio

# Agregar el directorio padre al path para importar src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import get_available_dates

async def main():
    print("🚀 Iniciando test del scraper principal...")
    try:
        resultado = await get_available_dates()
        print(f"✅ Resultado obtenido: {resultado}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())