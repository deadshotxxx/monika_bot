from aiogram import Router, F
from aiogram.types import Message
from monika_bot.services.memory import read_memory
import logging

logger = logging.getLogger(__name__)
router = Router()
PARENT_TELEGRAM_ID = "YOUR_TELEGRAM_ID"

@router.message(F.text.startswith("/parent_report"), F.from_user.id == int(PARENT_TELEGRAM_ID))
async def parent_report(message: Message):
    user_id = str(message.text.split()[1]) if len(message.text.split()) > 1 else None
    if not user_id:
        await message.reply_text("Укажите ID пользователя, например: /parent_report 12345")
        return
    
    global_memory = read_memory("global").get(user_id, {})
    mood_data = read_memory("mood").get(user_id, [])
    goals_data = read_memory("goals").get(user_id, [])
    learning_data = read_memory("learning").get(user_id, [])
    
    report = f"Отчёт по пользователю {user_id} ({global_memory.get('name', 'Друг')}):\n"
    if mood_data:
        report += f"- Последнее настроение: {mood_data[-1]['mood']} ({mood_data[-1]['date']})\n"
    if goals_data:
        report += f"- Цели: {', '.join(goals_data)}\n"
    if learning_data:
        report += f"- Темы учёбы: {', '.join([t['topic'] for t in learning_data])}\n"
    await message.reply_text(report)