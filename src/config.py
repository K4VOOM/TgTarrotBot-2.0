import os
from pathlib import Path
from dotenv import load_dotenv

# Завантажити .env з кореня проекту
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Bot instance (встановлюється в main.py)
BOT = None

# Admin ID
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Gemini keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
