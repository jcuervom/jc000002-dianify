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
