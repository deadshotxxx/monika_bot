import json
import os
import logging
from pathlib import Path
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

MEMORY_DIR = Path("monika_bot/memory")
MEMORY_FILES = {
    "mood": "mood.json",
    "goals": "goals.json",
    "homework": "homework.json",
    "learning": "learning.json",
    "quiz": "quiz.json",
    "game": "game.json",
    "global": "global_memory.json",
    "cache": "cache.json"
}

key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher = Fernet(key)

def ensure_memory_files():
    MEMORY_DIR.mkdir(exist_ok=True)
    for file in MEMORY_FILES.values():
        file_path = MEMORY_DIR / file
        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(cipher.encrypt(json.dumps({}).encode()))

def read_memory(section: str) -> dict:
    try:
        file_path = MEMORY_DIR / MEMORY_FILES[section]
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = cipher.decrypt(encrypted_data).decode()
        return json.loads(decrypted_data)
    except Exception as e:
        logger.error(f"Error reading {section} memory: {e}")
        return {}

def write_memory(section: str, data: dict) -> None:
    try:
        file_path = MEMORY_DIR / MEMORY_FILES[section]
        encrypted_data = cipher.encrypt(json.dumps(data, ensure_ascii=False).encode())
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
    except Exception as e:
        logger.error(f"Error writing {section} memory: {e}")

def update_memory(section: str, updates: dict) -> None:
    data = read_memory(section)
    data.update(updates)
    write_memory(section, data)