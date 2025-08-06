from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from monika_bot.services.memory import read_memory, update_memory
from monika_bot.services.ai_service import ask_ai
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = Router()

class MoodStates(StatesGroup):
    WAITING_MOOD = State()

@router.callback_query(F.data == "mood")
async def mood_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.reply_text("Какое у тебя сегодня настроение? (Например, 'весёлое', 'грустное' или опиши своими словами!)")
    await state.set_state(MoodStates.WAITING_MOOD)

@router.message(MoodStates.WAITING_MOOD)
async def handle_mood(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    mood = message.text.strip()
    update_memory("mood", {user_id: read_memory("mood").get(user_id, []) + [{"mood": mood, "date": datetime.now().isoformat()}]})
    
    is_personal, reason = await ask_ai(user_id, mood, "mood", message.bot)
    if is_personal:
        await message.reply_text(is_personal)
    elif "груст" in mood.lower():
        prompt = f"Создай короткую вдохновляющую цитату для 11-летней девочки, которая грустит."
        completion = await client.chat.completions.create(
            model="horizon-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        quote = completion.choices[0].message.content.strip()
        await message.reply_text(f"Не грусти, всё будет хорошо! 😊 Вот тебе цитата: {quote}")
    else:
        await message.reply_text("Спасибо, что поделилась! 😊 Хочешь рассказать подробнее?")
    await state.clear()