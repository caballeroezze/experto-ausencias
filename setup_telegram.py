#!/usr/bin/env python3
"""
Configurador automático para conexión a Telegram
Prueba diferentes métodos hasta encontrar uno que funcione
"""

import asyncio
import subprocess
import time
import requests
import logging
from src.config import settings

try:
    from aiogram import Bot
except ImportError:
    print("❌ aiogram no instalado")
    exit(1)

logging.basicConfig(level=logging.INFO)

async def test_telegram_connection():
    """Prueba la conexión básica a Telegram"""
    print("🔍 Probando conexión a Telegram...")
    
    if not settings.TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN no configurado en .env")
        return False
    
    try:
        bot = Bot(token=settings.TELEGRAM_TOKEN)
        me = await bot.get_me()
        await bot.session.close()
        print(f"✅ Conexión exitosa: @{me.username}")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def check_ngrok():
    """Verifica si ngrok está disponible y configurado"""
    try:
        # Verificar si ngrok está instalado
        subprocess.run(["ngrok", "version"], 
                      capture_output=True, check=True, timeout=5)
        print("✅ ngrok encontrado")
        
        # Verificar si hay túneles activos
        try:
            resp = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
            tunnels = resp.json().get("tunnels", [])
            if tunnels:
                for tunnel in tunnels:
                    print(f"🔗 Túnel activo: {tunnel['public_url']}")
                return True
            else:
                print("⚠️  ngrok instalado pero sin túneles activos")
                return False
        except:
            print("⚠️  ngrok instalado pero API no disponible")
            return False
            
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ ngrok no encontrado")
        return False

def install_ngrok_instructions():
    """Muestra instrucciones para instalar ngrok"""
    print("\n📥 CÓMO INSTALAR NGROK:")
    print("1. Ve a https://ngrok.com/download")
    print("2. Descarga ngrok para Windows")
    print("3. Descomprime y coloca ngrok.exe en tu PATH")
    print("4. Ejecuta: ngrok authtoken TU_TOKEN (regístrate gratis)")
    print("5. Ejecuta: ngrok http 8080")

def show_alternatives():
    """Muestra alternativas de conectividad"""
    print("\n🔄 ALTERNATIVAS DE CONECTIVIDAD:")
    print("\n1️⃣  CAMBIAR DE RED (MÁS FÁCIL):")
    print("   • Hotspot móvil de tu celular")
    print("   • Wifi diferente (casa, otro edificio)")
    print("   • Datos móviles 4G/5G")
    
    print("\n2️⃣  WEBHOOK CON NGROK:")
    print("   • Instala ngrok (gratis)")
    print("   • python bot_webhook.py")
    
    print("\n3️⃣  SERVIDOR EXTERNO:")
    print("   • Heroku, Railway, Render (gratis)")
    print("   • Sube tu código y ejecuta ahí")
    
    print("\n4️⃣  VPN/PROXY:")
    print("   • VPN gratuita (ProtonVPN, Windscribe)")
    print("   • Cambiar DNS (8.8.8.8, 1.1.1.1)")

async def main():
    print("🔧 CONFIGURADOR DE TELEGRAM")
    print("=" * 40)
    
    # Paso 1: Probar conexión directa
    if await test_telegram_connection():
        print("\n🎉 ¡Conexión directa funciona!")
        print("Ejecuta: python -m src.app")
        return
    
    print("\n⚠️  Conexión directa falló")
    
    # Paso 2: Verificar ngrok
    if check_ngrok():
        print("\n🔗 ngrok disponible - puedes usar webhook")
        print("Ejecuta: python bot_webhook.py")
    else:
        install_ngrok_instructions()
    
    # Paso 3: Mostrar alternativas
    show_alternatives()
    
    print("\n💡 RECOMENDACIÓN PARA PRESENTACIÓN:")
    print("   🔥 USA HOTSPOT MÓVIL (más rápido y seguro)")

if __name__ == "__main__":
    asyncio.run(main())
