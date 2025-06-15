import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения (.env)")

def verify_token(token: str) -> int:
    """
    Проверка токена Telegram вида 'uid:sha256(uid + BOT_TOKEN)'.
    Возвращает UID, если токен валиден, иначе выбрасывает исключение.
    """
    try:
        uid_part, hash_part = token.split(":")
        uid = int(uid_part)
        expected_hash = hashlib.sha256(f"{uid}{BOT_TOKEN}".encode()).hexdigest()
        if expected_hash != hash_part:
            raise ValueError("Неверный токен")
        return uid
    except Exception as e:
        raise ValueError("Невалидный токен") from e
