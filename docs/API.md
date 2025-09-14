# API Documentation

## Core Modules

### `src/scraper.py`

#### `get_available_dates()`

Función principal que realiza el web scraping del sitio de agendamiento de la DIAN.

**Returns:**
```python
{
    "error": bool,          # True si hubo un modal de error
    "dias": list[str],      # Lista de días disponibles
    "dia_agendado": str     # Día que se logró agendar (si aplica)
}
```

**Flujo:**
1. Detecta si está en Heroku o local
2. Configura browser con parámetros optimizados
3. Navega a https://agendamiento.dian.gov.co/
4. Completa formulario automáticamente
5. Extrae días disponibles del calendario
6. Intenta agendar primer día disponible

### `src/notifier.py`

#### `send_message(message: str)`

Envía notificación por Telegram.

**Parameters:**
- `message` (str): Mensaje a enviar

**Returns:**
- `bool`: True si se envió exitosamente

### `src/config.py`

Variables de configuración cargadas desde el entorno.

**Variables:**
- `TELEGRAM_BOT_TOKEN`: Token del bot de Telegram
- `TELEGRAM_CHAT_ID`: ID del chat donde enviar notificaciones
- `HEADLESS`: Ejecutar browser en modo headless

## Error Handling

El sistema maneja varios tipos de errores:

### TimeoutError
- **Causa**: El sitio web tarda más de lo esperado
- **Acción**: Reintento automático con backoff exponencial

### Browser Errors
- **Causa**: Fallo en Playwright/Chromium
- **Acción**: Reinicio del browser y reintento

### Network Errors
- **Causa**: Problemas de conexión
- **Acción**: Espera y reintento con timeout incrementado

### Telegram Errors
- **Causa**: Fallo en API de Telegram
- **Acción**: Log del error, continúa monitoreo

## Performance Optimizations

### Memory Usage
- Browser en modo single-process
- Bloqueo de recursos no esenciales (imágenes, CSS)
- Garbage collection después de cada ciclo

### Speed Optimizations
- domcontentloaded en lugar de networkidle
- Timeouts optimizados para Heroku
- Cache de selectores frecuentes

### Heroku Specific
- Health check endpoint en puerto dinámico
- Timeouts adaptativos según recursos disponibles
- Logging optimizado para agregación