import os
import asyncio
import time
from collections import deque

from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не знайдено! Перевір .env файл")

client = genai.Client(api_key=GEMINI_API_KEY)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

RPM_LIMIT = int(os.getenv("GEMINI_RPM_LIMIT", "15"))


class RateLimiter:

    def __init__(self, rpm_limit: int):
        self.rpm_limit = rpm_limit
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            while True:
                now = time.monotonic()

                while self._timestamps and now - self._timestamps[0] >= 60:
                    self._timestamps.popleft()

                if len(self._timestamps) < self.rpm_limit:
                    self._timestamps.append(now)
                    return

                wait_time = 60 - (now - self._timestamps[0]) + 0.05
                await asyncio.sleep(wait_time)


_rate_limiter = RateLimiter(RPM_LIMIT)


async def generate_text(prompt: str, model_name: str | None = None) -> str:

    await _rate_limiter.acquire()

    response = await asyncio.to_thread(
        client.models.generate_content,
        model=model_name or DEFAULT_MODEL,
        contents=prompt,
    )
    return response.text.strip()