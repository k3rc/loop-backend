import hashlib

# Секретный ключ, должен совпадать с тем, что используется в Telegram WebApp
BOT_TOKEN = "7812495971:AAFNTowxTUrHda4Nsih8DzIzEQjVS8sWxIk"  # Заменить на твой токен

# Простейшая проверка токена Telegram (в будущем можно заменить на JWT или OAuth)
def verify_token(token: str) -> int:
    """
    Простая проверка токена Telegram. Здесь он должен быть в формате 'uid:sha256(uid + secret)'.
    Возвращает user_id, если токен корректный. Иначе — None.
    """
    try:
        uid_part, hash_part = token.split(":")
        uid = int(uid_part)
        secret = BOT_TOKEN.encode()
        expected_hash = hashlib.sha256(f"{uid}{secret.decode()}".encode()).hexdigest()
        if expected_hash == hash_part:
            return uid
    except Exception:
        return None
