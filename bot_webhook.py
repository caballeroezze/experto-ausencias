#!/usr/bin/env python3
"""
Bot con WEBHOOK - Alternativa al polling para redes problemáticas
Usa ngrok para crear un túnel público
"""

import asyncio
import logging
from aiohttp import web
from aiohttp.web_request import Request
from src.config import settings
from src.dialogue.manager import DialogueManager

try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
except ImportError:
    print("❌ aiogram no instalado")
    exit(1)

# Configuración
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = None  # Se configurará dinámicamente
HOST = "127.0.0.1"
PORT = 8080

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dm = DialogueManager()

async def setup_webhook_bot():
    if not settings.TELEGRAM_TOKEN:
        print("❌ Falta TELEGRAM_TOKEN en .env")
        return None, None
    
    bot = Bot(token=settings.TELEGRAM_TOKEN)
    dp = Dispatcher()
    
    @dp.message()
    async def handle_message(msg: types.Message):
        user_id = msg.from_user.id if msg.from_user else msg.chat.id
        logger.info(f"📩 Mensaje webhook de {user_id}: {msg.text}")
        
        try:
            if not msg.text:
                await msg.reply("📎 Documento recibido")
                return
            
            if msg.text.lower() in ['/start', 'start', 'hola']:
                await msg.reply(
                    "🤖 <b>Sistema de Ausencias - Webhook</b>\n\n"
                    "✅ Conectado vía webhook\n"
                    "📝 Envía tu legajo para comenzar"
                )
                return
            
            if msg.text.lower() in ['/help', 'help']:
                await msg.reply("📋 Comandos: legajo, motivo, fecha_inicio, duracion_estimdays")
                return
            
            # Procesamiento normal
            session_id = str(user_id)
            result = dm.process_message(session_id, msg.text)
            
            reply = result.get("reply_text", "✅ Procesado")
            if result.get("ask"):
                reply += f"\n\n❓ Necesito: {', '.join(result['ask'])}"
            
            await msg.reply(reply)
            logger.info(f"📤 Respuesta webhook enviada")
            
        except Exception as e:
            logger.error(f"Error en webhook: {e}")
            await msg.reply(f"⚠️ Error: {str(e)}")
    
    return bot, dp

async def main():
    print("🔗 Sistema de Ausencias - Modo Webhook")
    print("=" * 50)
    
    # Detectar ngrok automáticamente
    try:
        import requests
        import json
        
        # Intentar obtener la URL de ngrok
        try:
            resp = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
            tunnels = resp.json().get("tunnels", [])
            
            for tunnel in tunnels:
                if tunnel.get("proto") == "https" and str(PORT) in tunnel.get("config", {}).get("addr", ""):
                    global WEBHOOK_URL
                    WEBHOOK_URL = tunnel["public_url"] + WEBHOOK_PATH
                    print(f"✅ Detectado ngrok: {WEBHOOK_URL}")
                    break
        except:
            pass
            
        if not WEBHOOK_URL:
            print("⚠️  ngrok no detectado. Ejecuta primero:")
            print(f"   ngrok http {PORT}")
            print("\nUsando webhook local (puede no funcionar)...")
            WEBHOOK_URL = f"http://{HOST}:{PORT}{WEBHOOK_PATH}"
        
    except ImportError:
        print("📦 requests no instalado, usando configuración manual")
        WEBHOOK_URL = f"http://{HOST}:{PORT}{WEBHOOK_PATH}"
    
    bot, dp = await setup_webhook_bot()
    if not bot:
        return
    
    try:
        # Configurar webhook
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(WEBHOOK_URL)
            print(f"🔗 Webhook configurado: {WEBHOOK_URL}")
        else:
            print(f"✅ Webhook ya configurado: {WEBHOOK_URL}")
        
        # Crear aplicación web
        app = web.Application()
        
        # Configurar el handler de webhook
        SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        ).register(app, path=WEBHOOK_PATH)
        
        # Endpoint de estado
        async def health(request: Request):
            return web.Response(text="🤖 Bot webhook activo!")
        
        app.router.add_get("/", health)
        
        print(f"🚀 Servidor iniciando en http://{HOST}:{PORT}")
        print("📱 Bot listo para recibir mensajes via webhook")
        print("🔄 Prueba enviando /start al bot")
        
        # Iniciar servidor
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, HOST, PORT)
        await site.start()
        
        # Mantener activo
        print("✅ Webhook activo - Presiona Ctrl+C para detener")
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo webhook...")
    except Exception as e:
        logger.error(f"Error webhook: {e}")
    finally:
        await bot.set_webhook("")  # Limpiar webhook
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
