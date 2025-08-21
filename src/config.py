from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
	TELEGRAM_TOKEN: str | None = os.getenv("TELEGRAM_TOKEN")
	DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ausencias.db")
	LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
	DEMO_EXPORT: bool = os.getenv("DEMO_EXPORT", "false").lower() in ("1", "true", "yes")


settings = Settings()
