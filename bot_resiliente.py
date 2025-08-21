#!/usr/bin/env python3
"""
Bot resiliente para redes problemáticas
Incluye reintentos automáticos y configuración robusta
"""

import asyncio
import logging
from src.config import settings
from src.dialogue.manager import DialogueManager

try:
    from aiogram import Bot, Dispatcher
    from aiogram.types import Message
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram import BaseMiddleware
    from aiogram.types import TelegramObject
except ImportError:
    print("❌ aiogram no instalado")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

dm = DialogueManager()

class RetryMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error en handler: {e}")
            if isinstance(event, Message):
                try:
                    await event.reply("❌ Error temporal, intentá de nuevo")
                except:
                    pass

async def safe_start_bot():
    if not settings.TELEGRAM_TOKEN:
        print("❌ Falta TELEGRAM_TOKEN en .env")
        return False
    
    # Configuración más robusta
    bot = Bot(
        token=settings.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    dp.message.middleware(RetryMiddleware())
    
    @dp.message()
    async def handle_any_message(msg: Message):
        user_id = msg.from_user.id if msg.from_user else msg.chat.id
        logger.info(f"📩 Mensaje de {user_id}: {msg.text}")
        
        try:
            if not msg.text:
                await msg.reply("📎 Documento recibido (procesamiento pendiente)")
                return
            
            # Respuestas hardcodeadas para emergencia
            if msg.text.lower() in ['/start', 'start', 'hola']:
                await msg.reply(
                    "🤖 <b>Sistema de Ausencias Laborales</b>\n\n"
                    "✅ Motor experto funcionando\n"
                    "📝 Envía: <code>legajo: L1000</code>\n"
                    "🔍 O consulta: <code>/help</code>"
                )
                return
            
            if msg.text.lower() in ['/help', 'help', 'ayuda']:
                await msg.reply(
                    "📋 <b>Comandos disponibles:</b>\n\n"
                    "• <code>legajo: L1000</code>\n"
                    "• <code>motivo: enfermedad</code>\n" 
                    "• <code>fecha_inicio: hoy</code>\n"
                    "• <code>duracion_estimdays: 3</code>\n"
                    "• <code>consultar estado</code>"
                )
                return
            
            # Procesamiento con DialogueManager
            session_id = str(user_id)
            result = dm.process_message(session_id, msg.text)
            
            reply_text = result.get("reply_text", "✅ Procesado correctamente")
            
            # Agregar info adicional si existe
            if result.get("ask"):
                reply_text += f"\n\n❓ Necesito: {', '.join(result['ask'])}"
            
            await msg.reply(reply_text)
            logger.info(f"📤 Respuesta enviada a {user_id}")
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            await msg.reply(f"⚠️ Error: {str(e)[:100]}...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Intento {attempt + 1}/{max_retries}")
            
            # Verificar bot
            me = await bot.get_me()
            logger.info(f"✅ Bot conectado: @{me.username}")
            
            # Configuración especial para redes problemáticas
            await dp.start_polling(
                bot,
                polling_timeout=20,  # Timeout más corto
                request_timeout=15,  # Request timeout
                allowed_updates=["message"],  # Solo mensajes
                drop_pending_updates=True,  # Descartar mensajes pendientes
                handle_signals=False
            )
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot detenido por usuario")
            return True
        except Exception as e:
            logger.error(f"❌ Error en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Backoff exponencial
                logger.info(f"⏳ Esperando {wait_time}s antes del siguiente intento...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("❌ Todos los intentos fallaron")
                return False
        finally:
            await bot.session.close()

def main():
    print("🚀 Bot Resiliente - Sistema de Ausencias")
    print("=" * 40)
    
    # Verificar componentes
    try:
        print("🔧 Verificando componentes...")
        test_dm = DialogueManager()
        print("✅ DialogueManager: OK")
        
        if not settings.TELEGRAM_TOKEN:
            print("❌ TELEGRAM_TOKEN no configurado")
            print("\n💡 Para la demo sin Telegram, usa:")
            print("   python demo_local.py")
            return
        
        print("✅ Token configurado")
        print("\n🔄 Iniciando bot resiliente...")
        
        success = asyncio.run(safe_start_bot())
        if success:
            print("✅ Bot ejecutado exitosamente")
        else:
            print("❌ Bot falló después de todos los reintentos")
            
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        print("\n💡 Para la demo sin red, usa:")
        print("   python demo_local.py")

if __name__ == "__main__":
    main()
