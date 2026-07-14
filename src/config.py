import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

BOT = None

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

BOT_TOKEN = os.getenv("BOT_TOKEN")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
