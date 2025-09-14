# Tests

Esta carpeta contiene todos los tests y herramientas de debug para el proyecto DIAN Appointment Scraper.

## 📁 Estructura de Tests

### Tests Principales
- **`test_scraper.py`** - Test básico del scraper principal
- **`test_debug_scraper.py`** - Test con logs detallados para debug
- **`test_scraper_directo.py`** - Test directo del scraper mejorado

### Tests de Comportamiento Específico
- **`test_control_209.py`** - Test específico para verificar clicks en #control_209
- **`test_modal_behavior.py`** - Test para verificar manejo de modales (con navegador visible)
- **`test_real_modal.py`** - Test que intenta provocar modales reales de error

### Herramientas
- **`test_explanation.py`** - Explicación del comportamiento implementado
- **`debug_heroku.py`** - Herramientas de debug para Heroku

## 🚀 Cómo Ejecutar los Tests

### Test Principal (recomendado)
```bash
python tests/test_scraper_directo.py
```

### Test con Debug Detallado
```bash
python tests/test_debug_scraper.py
```

### Test Visual (abre navegador)
```bash
python tests/test_modal_behavior.py
```

### Test de Verificación del Click #control_209
```bash
python tests/test_control_209.py
```

### Ver Explicación del Comportamiento
```bash
python tests/test_explanation.py
```

## 📋 Descripción de Funcionalidades Probadas

### ✅ Funcionalidad Principal
- Navegación a sitio DIAN
- Completado de formulario
- Detección de días disponibles
- Manejo de modales de error
- Reintento con días siguientes

### ✅ Casos de Error Manejados
- Modal de error en reserva de cita
- Redirección después de cerrar modal
- Recompletado de formulario desde el inicio
- Agotamiento de días disponibles

### ✅ Optimizaciones para Heroku
- Configuración de navegador optimizada
- Timeouts ajustados
- Manejo de memoria eficiente
- Detección automática de entorno

## 🎯 Tests por Funcionalidad

| Test | Propósito | Navegador Visible | Duración |
|------|-----------|-------------------|----------|
| `test_scraper_directo.py` | Test completo del flujo principal | No | ~2-3 min |
| `test_debug_scraper.py` | Debug con logs detallados | No | ~2-3 min |
| `test_modal_behavior.py` | Verificación visual de modales | Sí | ~3-5 min |
| `test_control_209.py` | Verificación específica de clicks | Sí | ~2-3 min |
| `test_explanation.py` | Mostrar documentación | N/A | Instantáneo |

## 📝 Notas Importantes

- Los tests que requieren navegador visible (`headless=False`) necesitan que tengas una sesión gráfica activa
- En Heroku, todos los tests corren en modo headless automáticamente
- Los tests pueden fallar si no hay días disponibles reales en el sitio DIAN
- Los modales de error son esperados y son parte del flujo normal de testing