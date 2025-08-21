from __future__ import annotations

import logging
from typing import Optional

try:
	from aiogram import Bot, Dispatcher, F
	from aiogram.filters import Command
	from aiogram.types import Message
	exists_aiogram = True
except Exception:  # aiogram no instalado aún
	exists_aiogram = False
	Bot = Dispatcher = Message = object  # type: ignore

from ..dialogue.manager import DialogueManager
from ..session_store import set_legajo
from ..persistence.seed import ensure_schema
from ..persistence.dao import session_scope
from ..persistence.models import Employee
from ..config import settings

logging.basicConfig(level=logging.INFO)


_dm = DialogueManager()


async def start_bot(token: str) -> None:
	"""Inicia el bot de Telegram (aiogram 3.x)."""
	if not exists_aiogram:
		print("aiogram no está disponible. Instálalo con requirements.txt")
		return
	
	print(f"Inicializando DialogueManager...")
	try:
		_dm_test = DialogueManager()
		print("DialogueManager inicializado correctamente")
	except Exception as e:
		print(f"Error inicializando DialogueManager: {e}")
		return
	
	bot = Bot(token)
	dp = Dispatcher()
	print(f"Bot configurado, registrando handlers...")

	# Comando /id <legajo>
	@dp.message(Command("id"))
	async def handle_id(msg: Message) -> None:
		try:
			parts = (msg.text or "").split()
			if len(parts) < 2:
				await msg.reply("Usá: /id <legajo> (por ejemplo /id 1001)")
				return
			from ..utils.normalize import parse_legajo
			legajo_digits = parse_legajo(parts[1].strip()) or ""
			if not legajo_digits:
				await msg.reply("Formato inválido. Usá /id 1234 (4 dígitos)")
				return
			# Validar en BD mínima
			ensure_schema()
			with session_scope() as s:
				emp = s.query(Employee).filter(Employee.legajo == legajo_digits).first()
			if not emp:
				await msg.reply("No encontré ese legajo en el sistema. Revisá y volvé a intentar.")
				return
			set_legajo(str(msg.chat.id), legajo_digits)
			_dm.set_legajo_validado(str(msg.chat.id), legajo_digits)
			await msg.reply(f"Listo, legajo {legajo_digits} verificado ✅")
		except Exception as e:
			await msg.reply(f"No pude guardar el legajo: {e}")

	# Comando /export_csv (solo demo)
	@dp.message(Command("export_csv"))
	async def handle_export(msg: Message) -> None:
		try:
			if not settings.DEMO_EXPORT:
				await msg.reply("Comando no disponible en este entorno.")
				return
			ensure_schema()
			from ..persistence.export_powerbi import export_all_csv
			export_all_csv(out_dir="./exports")
			await msg.reply("Export listo en /exports (employees.csv, avisos.csv, certificados.csv, notificaciones.csv, auditoria.csv)")
		except Exception as e:
			await msg.reply(f"Error en export: {e}")

	# Handler simplificado para testing
	@dp.message()
	async def handle_message(msg: Message) -> None:
		print(f"📩 MENSAJE RECIBIDO de {msg.chat.id}: {msg.text}")
		logging.info(f"Mensaje recibido de {msg.chat.id}: {msg.text}")
		
		try:
			# Respuesta simple primero para confirmar que funciona
			if msg.text and msg.text.startswith('/start'):
				await msg.reply("🤖 Bot funcionando! Soy el sistema de ausencias.")
			elif msg.text and msg.text.startswith('/help'):
				await msg.reply("📋 Puedo ayudarte con avisos de ausencias. Enviá tu legajo y motivo.")
			elif msg.text:
				print(f"💬 Procesando con DialogueManager: {msg.text}")
				session_id = str(msg.chat.id)
				result = _dm.process_message(session_id, msg.text)
				print(f"📤 Respuesta del sistema: {result}")
				
				reply_text = result.get("reply_text", "Sistema procesado")
				await msg.reply(reply_text)
			else:
				await msg.reply("💾 Documento o tipo de mensaje no soportado aún")
				
		except Exception as e:
			print(f"❌ ERROR: {e}")
			logging.error(f"Error procesando mensaje: {e}", exc_info=True)
			await msg.reply(f"Error: {str(e)}")

	print(f"Handlers registrados, iniciando polling...")
	
	try:
		# Verificar que el bot funciona antes de polling
		me = await bot.get_me()
		print(f"Bot verificado: @{me.username} (ID: {me.id})")
		
		# Configuración más robusta para el polling
		await dp.start_polling(
			bot,
			polling_timeout=30,
			handle_signals=False,
			close_bot_session=True,
			allowed_updates=None  # Recibir todos los tipos de updates
		)
	except KeyboardInterrupt:
		print("Bot detenido por usuario")
	except Exception as e:
		print(f"Error durante polling: {e}")
		logging.error(f"Error durante polling: {e}", exc_info=True)
