#!/usr/bin/env python3

import asyncio
import time
import gc
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from src.scraper import get_available_dates
from src.notifier import send_message

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suprimir logs del servidor HTTP
        pass

def start_health_server():
    """Inicia un servidor HTTP simple para health checks"""
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🌐 Servidor de health check iniciado en puerto {port}")
    server.serve_forever()


async def run_periodically():
    consecutive_errors = 0
    max_consecutive_errors = 3
    
    while True:
        try:
            print(f"🔍 Iniciando verificación de citas... {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Añadir timeout para evitar que Heroku mate el proceso
            try:
                resultado = await asyncio.wait_for(get_available_dates(), timeout=180)  # 3 minutos máximo
            except asyncio.TimeoutError:
                print("⚠️ Timeout en la verificación de citas")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    wait_time = 600  # 10 minutos
                    print(f"⚠️ Demasiados timeouts. Esperando {wait_time//60} minutos...")
                    await asyncio.sleep(wait_time)
                    continue
                await asyncio.sleep(300)
                continue
            
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
        
        # Forzar garbage collection para liberar memoria en Heroku
        gc.collect()
        
        # Ajustar frecuencia según el entorno
        if os.getenv("DYNO"):  # En Heroku, verificar menos frecuentemente para ahorrar memoria
            wait_time = 600  # 10 minutos en Heroku
        else:
            wait_time = 300  # 5 minutos en desarrollo local
            
        print(f"⏰ Esperando {wait_time//60} minutos hasta la próxima verificación...")
        await asyncio.sleep(wait_time)

if __name__ == "__main__":
    # Iniciar servidor HTTP en un hilo separado para Heroku
    if os.getenv("DYNO"):  # Solo en Heroku
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()
        time.sleep(2)  # Dar tiempo al servidor para iniciar
    
    print("🚀 Iniciando bot de verificación de citas DIAN...")
    asyncio.run(run_periodically())
