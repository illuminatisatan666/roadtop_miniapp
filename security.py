# security.py
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your_very_strong_32_char_secret_key_here")

def generate_token(telegram_id: int, username: str) -> str:
    data = f"{telegram_id}:{username or 'anon'}:{SECRET_KEY}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]