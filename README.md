# jc000002-dianify

**jc000002-dianify** es un bot automatizado que monitorea la página de agendamiento de citas de la DIAN (Colombia) y notifica por Telegram cuando hay citas disponibles.

## Características

- Scraping automatizado de la web de agendamiento de la DIAN usando Playwright.
- Notificaciones instantáneas vía Telegram cuando se detectan citas disponibles.
- Configuración sencilla mediante archivo `.env`.
- Ejecución periódica cada 5 minutos.

## Requisitos

- Python 3.8+
- Playwright
- python-telegram-bot
- python-dotenv

Instala las dependencias con:

```bash
pip install -r requirements.txt
python -m playwright install
```

## Configuración

Crea un archivo `.env` con tu token y chat ID de Telegram:

```
TELEGRAM_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id
```

## Uso

Ejecuta el bot con:

```bash
python main.py
```

El bot revisará periódicamente la página de la DIAN y enviará una notificación por Telegram si hay citas disponibles.

## Despliegue en Heroku

Este proyecto está configurado para desplegarse en Heroku usando los siguientes buildpacks:

1. `heroku-community/apt` - Para dependencias del sistema
2. `heroku/python` - Para Python
3. `https://github.com/playwright-community/heroku-playwright-buildpack.git` - Para Playwright

### Variables de entorno en Heroku

- `TELEGRAM_TOKEN`: Tu token de bot de Telegram
- `TELEGRAM_CHAT_ID`: Tu chat ID de Telegram
- `PLAYWRIGHT_BUILDPACK_BROWSERS=chromium`: Especifica qué navegador instalar

### Solución de problemas en Heroku

Si encuentras errores relacionados con Playwright en Heroku:

1. Verifica que uses el buildpack correcto: `https://github.com/playwright-community/heroku-playwright-buildpack.git`
2. Ejecuta el script de verificación: `python bin/verify_playwright.py`
3. Revisa los logs de construcción para asegurar que Chromium se instaló correctamente
