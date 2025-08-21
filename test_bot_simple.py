#!/usr/bin/env python3
"""
Script simple de prueba del bot de Telegram
Para probar la conectividad básica sin toda la lógica del DialogueManager
"""

import asyncio
import logging
from src.config import settings

try:
    from aiogram import Bot, Dispatcher
    from aiogram.types import Message
    from aiogram.filters import Command
except ImportError:
    print("aiogram no instalado")
    exit(1)

logging.basicConfig(level=logging.INFO)

async def main():
    if not settings.TELEGRAM_TOKEN:
        print("Falta TELEGRAM_TOKEN en .env")
        return
    
    bot = Bot(settings.TELEGRAM_TOKEN)
    dp = Dispatcher()
    
    @dp.message()
    async def any_message(msg: Message):
        print(f"📩 Mensaje recibido de {msg.chat.id}: {msg.text}")
        await msg.reply(f"Echo: {msg.text}")
    
    try:
        me = await bot.get_me()
        print(f"✅ Bot conectado: @{me.username}")
        print("🔄 Iniciando polling simple...")
        
        await dp.start_polling(bot, polling_timeout=10)
        
    except KeyboardInterrupt:
        print("🛑 Bot detenido")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
