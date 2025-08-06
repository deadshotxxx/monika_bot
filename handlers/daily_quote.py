from aiogram import Router, Bot
from monika_bot.services.memory import read_memory
from monika_bot.services.ai_service import ask_ai
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)
router = Router()

async def send_daily_quote(bot: Bot):
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            try:
                users = read_memory("global")
                for user_id, global_memory in users.items():
                    if global_memory.get("daily_quotes", True):
                        quote = await ask_ai(user_id, "Дай вдохновляющую цитату на день.", "daily_quote", bot)
                        await bot.send_message(
                            chat_id=int(user_id),
                            text=f"🌞 Доброе утро, {global_memory.get('name', 'Друг')}! Вот твоя цитата на сегодня:\n\n_{quote}_"
                        )
            except Exception as e:
                logger.error(f"Ошибка отправки цитаты: {e}")
        await asyncio.sleep(60)