from __future__ import annotations

import asyncio
from .config import settings
from .telegram.bot import start_bot


def main() -> None:
	print("Sistema Experto de Ausencias — iniciando bot...")
	if not settings.TELEGRAM_TOKEN:
		print("Falta TELEGRAM_TOKEN en .env. Configurá y reintentá.")
		return
	asyncio.run(start_bot(settings.TELEGRAM_TOKEN))


if __name__ == "__main__":
	main()
