from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from monika_bot.services.memory import read_memory, update_memory
import logging

logger = logging.getLogger(__name__)
router = Router()

def get_main_keyboard():
    keyboard = [
        [{"text": "😊 Попросить совет", "callback_data": "advice"},
         {"text": "🚪 Поделиться настроением", "callback_data": "mood"}],
        [{"text": "⌚ Установить напоминание", "callback_data": "reminder"},
         {"text": "🎮 Сыграть в викторину", "callback_data": "quiz"}],
        [{"text": "📖 Помощь с учёбой", "callback_data": "study"},
         {"text": "🎯 Поставить цель", "callback_data": "goal"}],
        [{"text": "📊 Мой профиль", "callback_data": "profile"},
         {"text": "⚙️ Настройки профиля", "callback_data": "profile_settings"}],
        [{"text": "🕵️‍♀️ Играть в Мафию", "callback_data": "mafia"}]
    ]
    return {"inline_keyboard": keyboard}

@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    global_memory = read_memory("global").get(user_id, {})
    if not global_memory:
        global_memory = {
            "name": message.from_user.first_name,
            "tone": "мягкое и дружелюбное",
            "interests": [],
            "auto_messages_enabled": True,
            "daily_quotes": True,
            "points": 0,
            "timezone": "Europe/Moscow"  # По умолчанию, можно изменить
        }
        update_memory("global", {user_id: global_memory})

    welcome_message = (
        f"🌟 Привет, {global_memory['name']}! Я Моника, твой заботливый ИИ-друг.\n"
        "Я помогу с советами, поддержу, напомню о делах и даже поиграю с тобой!\n"
        "Что хочешь сделать сегодня?"
    )
    await message.reply_text(welcome_message, reply_markup=get_main_keyboard())