#!/usr/bin/env python3

import asyncio
from scraper import get_available_dates

async def test_scraper():
    print("🧪 Iniciando prueba del scraper en local...")
    try:
        resultado = await get_available_dates()
        print(f"✅ Resultado: {resultado}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())