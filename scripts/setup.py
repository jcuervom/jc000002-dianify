#!/usr/bin/env python3
"""
Script de configuración inicial para el proyecto DIAN Appointment Checker
"""

import os
import sys
import subprocess
from pathlib import Path

def print_step(step, message):
    print(f"\n{'='*50}")
    print(f"PASO {step}: {message}")
    print('='*50)

def run_command(command, description):
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def main():
    print("🤖 DIAN Appointment Checker - Setup Script")
    print("==========================================")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print_step(1, "Verificando Python")
    python_version = sys.version_info
    print(f"📍 Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    print_step(2, "Creando entorno virtual")
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creación del entorno virtual"):
            return False
    else:
        print("✅ Entorno virtual ya existe")
    
    print_step(3, "Instalando dependencias")
    pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Actualización de pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Instalación de dependencias"):
        return False
    
    print_step(4, "Instalando browsers de Playwright")
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python"
    
    if not run_command(f"{python_cmd} -m playwright install chromium", "Instalación de Chromium"):
        return False
    
    print_step(5, "Configurando archivo .env")
    if not Path(".env").exists():
        if Path(".env.example").exists():
            print("🔧 Copiando .env.example a .env...")
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales de Telegram")
        else:
            print("❌ No se encontró .env.example")
            return False
    else:
        print("✅ Archivo .env ya existe")
    
    print_step(6, "Ejecutando test básico")
    if not run_command(f"{python_cmd} tests/test_scraper.py", "Test del scraper"):
        print("⚠️  Test falló, pero esto es normal si no tienes configurado Telegram")
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETADO EXITOSAMENTE!")
    print("="*60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Edita el archivo .env con tus credenciales de Telegram")
    print("2. Ejecuta: python main.py")
    print("3. Para Heroku: ./scripts/deploy.sh tu-app-name")
    print("\n📚 DOCUMENTACIÓN:")
    print("- README.md para instrucciones completas")
    print("- tests/ para debugging")
    print("- docs/ para documentación adicional")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)