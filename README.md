# 🤖 DIAN Appointment Checker

Un bot automatizado para verificar la disponibilidad de citas en el sistema de agendamiento de la DIAN (Dirección de Impuestos y Aduanas Nacionales de Colombia).

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.40+-green.svg)](https://playwright.dev/)
[![Heroku](https://img.shields.io/badge/deploy-heroku-purple.svg)](https://heroku.com/)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Deployment en Heroku](#-deployment-en-heroku)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## ✨ Características

- 🔍 **Monitoreo Automático**: Verifica disponibilidad de citas cada 10 minutos
- 📱 **Notificaciones Telegram**: Alerta instantánea cuando hay citas disponibles
- 🌐 **Web Scraping Inteligente**: Utiliza Playwright para navegación robusta
- ☁️ **Deploy en Heroku**: Configurado para ejecutarse 24/7 en la nube
- 🛡️ **Manejo de Errores**: Sistema robusto de reintentos y recuperación
- 🚀 **Optimizado para Memoria**: Configuración específica para entornos limitados
- 📊 **Logging Detallado**: Monitoreo completo del proceso

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    main.py      │    │   src/scraper   │    │ src/notifier    │
│                 │───▶│                 │───▶│                 │
│ - Scheduler     │    │ - Web Scraping  │    │ - Telegram Bot  │
│ - Health Check  │    │ - Form Filling  │    │ - Messages      │
│ - Error Handler │    │ - Data Extract  │    │ - Alerts        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   src/config    │
│                 │
│ - Environment   │
│ - Settings      │
│ - Constants     │
└─────────────────┘
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- Una cuenta de Telegram y bot token
- Cuenta de Heroku (para deployment)

### Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/jcuervom/jc000002-dianify.git
   cd citasDian
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\\Scripts\\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar browsers de Playwright**
   ```bash
   python -m playwright install chromium
   ```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# Application Settings
HEADLESS=true
NODE_ENV=production
```

### Configuración de Telegram

1. **Crear un bot de Telegram**:
   - Envía `/newbot` a [@BotFather](https://t.me/botfather)
   - Sigue las instrucciones para crear tu bot
   - Guarda el token que te proporciona

2. **Obtener tu Chat ID**:
   - Envía un mensaje a tu bot
   - Visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Busca el `chat.id` en la respuesta

## 🎯 Uso

### Ejecución Local

```bash
# Ejecutar el bot principal
python main.py

# Ejecutar tests
python tests/test_scraper.py

# Debugging detallado
python tests/test_debug_scraper.py
```

### Comandos Útiles

```bash
# Verificar configuración
python -c "from src.config import *; print('Config OK')"

# Test de notificaciones
python -c "from src.notifier import send_message; import asyncio; asyncio.run(send_message('Test!'))"

# Verificar browsers instalados
python -m playwright install --help
```

## ☁️ Deployment en Heroku

### 1. Preparación

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login a Heroku
heroku login

# Crear app
heroku create tu-app-name
```

### 2. Configurar Buildpacks

⚠️ **IMPORTANTE**: El orden de los buildpacks es crucial.

```bash
# 1. Python buildpack (debe ir primero)
heroku buildpacks:add heroku/python

# 2. Playwright Python browsers buildpack (segundo)
heroku buildpacks:add https://github.com/jcuervom/heroku-playwright-python-browsers.git

# 3. Playwright community buildpack (tercero)
heroku buildpacks:add https://github.com/playwright-community/heroku-playwright-buildpack.git
```

### 3. Variables de Entorno

```bash
heroku config:set TELEGRAM_BOT_TOKEN=tu_token_aqui
heroku config:set TELEGRAM_CHAT_ID=tu_chat_id_aqui
heroku config:set PLAYWRIGHT_BUILDPACK_BROWSERS=chromium
heroku config:set HEADLESS=true
```

### 4. Deploy

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 5. Monitoreo

```bash
# Ver logs en tiempo real
heroku logs --tail

# Ver status de la app
heroku ps

# Restart si es necesario
heroku restart
```

## 📁 Estructura del Proyecto

```
citasDian/
├── 📄 main.py                 # Aplicación principal
├── 📁 src/                    # Código fuente
│   ├── 📄 __init__.py         # Inicialización del paquete
│   ├── 🕷️ scraper.py          # Web scraping con Playwright
│   ├── 📱 notifier.py         # Notificaciones de Telegram
│   └── ⚙️ config.py           # Configuración y variables
├── 📁 tests/                  # Tests y debugging
│   ├── 📄 __init__.py
│   ├── 🧪 test_scraper.py     # Test básico del scraper
│   └── 🔍 test_debug_scraper.py # Test con debugging detallado
├── 📁 docs/                   # Documentación
├── 📁 scripts/                # Scripts de utilidad
├── 📄 requirements.txt        # Dependencias de Python
├── 📄 Procfile               # Configuración de Heroku
├── 📄 .env.example           # Ejemplo de variables de entorno
├── 📄 .gitignore             # Archivos ignorados por Git
└── 📄 README.md              # Este archivo
```

## 🧪 Testing

### Tests Locales

```bash
# Test básico
python tests/test_scraper.py

# Test con debugging detallado
python tests/test_debug_scraper.py
```

### Tests de Producción

```bash
# Verificar health check
curl https://tu-app.herokuapp.com/health

# Verificar logs
heroku logs --tail
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error: "Executable doesn't exist"

**Síntoma**: El bot no puede encontrar el browser de Chromium.

**Solución**:
```bash
# Verificar buildpacks
heroku buildpacks

# Reinstalar si es necesario
heroku config:set PLAYWRIGHT_BUILDPACK_BROWSERS=chromium
```

#### 2. Timeout en Heroku

**Síntoma**: El proceso se termina con SIGKILL.

**Solución**: El código ya está optimizado para memoria limitada. Si persiste:
```bash
# Verificar memoria disponible
heroku ps:type web=hobby  # 512MB
heroku ps:type web=standard-1x  # 512MB
heroku ps:type web=standard-2x  # 1GB
```

#### 3. Bot no recibe notificaciones

**Síntoma**: El scraper funciona pero no llegan mensajes.

**Solución**:
```bash
# Verificar configuración
heroku config:get TELEGRAM_BOT_TOKEN
heroku config:get TELEGRAM_CHAT_ID

# Test manual
python -c "from src.notifier import send_message; import asyncio; asyncio.run(send_message('Test'))"
```

#### 4. Calendario no carga

**Síntoma**: Se queda en "Waiting for calendar...".

**Posibles causas**:
- Sitio web de la DIAN está lento
- Timeout muy corto
- Recursos bloqueados necesarios

**Solución**: El código incluye timeouts adaptativos y múltiples reintentos.

### Logs de Debug

Para habilitar logging detallado:

```bash
# En desarrollo local
export DEBUG=true
python main.py

# En Heroku
heroku config:set DEBUG=true
```

### Comandos de Diagnóstico

```bash
# Verificar health de la app
curl https://tu-app.herokuapp.com/health

# Verificar estado de dynos
heroku ps

# Reiniciar la app
heroku restart

# Ver métricas
heroku metrics

# Acceder al dyno
heroku run bash
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📊 Monitoring y Métricas

### Métricas Importantes

- **Uptime**: Tiempo que la app ha estado funcionando
- **Frequency**: Cada cuánto verifica citas (10 min en Heroku, 5 min local)
- **Success Rate**: Porcentaje de verificaciones exitosas
- **Response Time**: Tiempo que toma cada verificación

### Alertas

El bot enviará notificaciones por:
- ✅ Citas disponibles encontradas
- ❌ Errores consecutivos (cada 3 errores)
- ⚠️ Reinicio después de múltiples fallos

## 🔒 Seguridad

- 🔐 **Tokens**: Nunca commitees tokens en el código
- 🌐 **HTTPS**: Todas las comunicaciones son seguras
- 🛡️ **Rate Limiting**: Respeta los límites del sitio de la DIAN
- 🔒 **Env Variables**: Configuración sensible en variables de entorno

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**jcuervom** - [GitHub](https://github.com/jcuervom)

## 🙏 Agradecimientos

- [Playwright](https://playwright.dev/) - Framework de automatización web
- [python-telegram-bot](https://python-telegram-bot.org/) - API de Telegram para Python
- [Heroku](https://heroku.com/) - Plataforma de deployment
- Comunidad de buildpacks de Playwright para Heroku

---

**⚠️ Disclaimer**: Este bot es para uso educativo y personal. Respeta los términos de uso del sitio web de la DIAN y no hagas un uso abusivo del sistema.

**📞 Soporte**: Si tienes problemas, abre un [issue](https://github.com/jcuervom/jc000002-dianify/issues) en GitHub.
