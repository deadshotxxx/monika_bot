from aiogram import Router, Bot
from monika_bot.services.memory import read_memory
from monika_bot.services.ai_service import ask_ai
import logging
import asyncio
import random
from datetime import datetime

logger = logging.getLogger(__name__)
router = Router()

async def send_auto_messages(bot: Bot):
    while True:
        try:
            users = read_memory("global")
            for user_id, global_memory in users.items():
                if not global_memory.get("auto_messages_enabled", True):
                    continue
                mood_data = read_memory("mood").get(user_id, [])
                learning_data = read_memory("learning").get(user_id, [])
                name = global_memory.get("name", "Друг")
                
                if learning_data and random.random() < 0.4:
                    topic = random.choice([t["topic"] for t in learning_data])
                    message = f"Привет, {name}! Как успехи с {topic}? 😊"
                elif mood_data and random.random() < 0.6:
                    last_mood = mood_data[-1]["mood"]
                    message = f"Привет, {name}! Ты недавно чувствовала себя {last_mood}. Как дела сейчас? 😊"
                else:
                    message = f"Привет, {name}! Как дела? 😊 Расскажи, что нового!"
                
                await bot.send_message(chat_id=user_id, text=message)
            await asyncio.sleep(random.randint(7200, 14400))
        except Exception as e:
            logger.error(f"Ошибка автосообщений: {e}")
            await asyncio.sleep(60)