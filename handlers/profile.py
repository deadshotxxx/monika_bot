from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from monika_bot.services.memory import read_memory, update_memory
import logging

logger = logging.getLogger(__name__)
router = Router()

class ProfileSettingsStates(StatesGroup):
    WAITING_SETTINGS = State()

@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    global_memory = read_memory("global").get(user_id, {})
    mood_data = read_memory("mood").get(user_id, [])
    goals_data = read_memory("goals").get(user_id, [])
    learning_data = read_memory("learning").get(user_id, [])

    profile_text = f"🌟 *Твой профиль, {global_memory.get('name', 'Друг')}* 🌟\n\n"
    if global_memory.get("interests"):
        profile_text += f"🌈 *Интересы*: {', '.join(global_memory['interests'][-5:])}\n"
    if goals_data:
        profile_text += f"🎯 *Цели*: {', '.join(goals_data)}\n"
    if mood_data:
        profile_text += f"😊 *Недавние настроения*: {', '.join([f'{m['date']} — {m['mood']}' for m in mood_data[-3:]])}\n"
    profile_text += f"⚙️ *Настройки*: Ежедневные цитаты {'включены' if global_memory.get('daily_quotes', True) else 'выключены'}\n"
    profile_text += f"Автосообщения {'включены' if global_memory.get('auto_messages_enabled', True) else 'выключены'}\n"
    profile_text += f"🎖 *Баллы*: {global_memory.get('points', 0)}"

    await callback.message.reply_text(profile_text, reply_markup={
        "inline_keyboard": [[{"text": "Настройки", "callback_data": "profile_settings"},
                             {"text": "Вкл/Выкл автосообщения", "callback_data": "toggle_auto_messages"}]]
    })

@router.callback_query(F.data == "toggle_auto_messages")
async def toggle_auto_messages(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    global_memory = read_memory("global").get(user_id, {})
    current = global_memory.get("auto_messages_enabled", True)
    global_memory["auto_messages_enabled"] = not current
    update_memory("global", {user_id: global_memory})
    await callback.message.reply_text(
        f"Автосообщения {'включены' if not current else 'выключены'}!"
    )

@router.callback_query(F.data == "profile_settings")
async def profile_settings_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.reply_text(
        "Что хочешь изменить? Напиши, например: 'Имя: Анна', 'Интерес: Космос', 'Отключить цитаты'"
    )
    await state.set_state(ProfileSettingsStates.WAITING_SETTINGS)

@router.message(ProfileSettingsStates.WAITING_SETTINGS)
async def handle_profile_settings(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    global_memory = read_memory("global").get(user_id, {})
    
    if "Имя:" in text:
        global_memory["name"] = text.split("Имя:")[1].strip()
    elif "Интерес:" in text:
        global_memory.setdefault("interests", []).append(text.split("Интерес:")[1].strip())
    elif "Отключить цитаты" in text:
        global_memory["daily_quotes"] = False
    elif "Включить цитаты" in text:
        global_memory["daily_quotes"] = True
    update_memory("global", {user_id: global_memory})
    await message.reply_text("Настройки обновлены! Что ещё хочешь изменить?", reply_markup=get_main_keyboard())
    await state.clear()