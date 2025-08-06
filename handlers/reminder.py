from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from monika_bot.services.db_service import save_reminder, load_reminders, delete_reminder
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)
router = Router()

class ReminderStates(StatesGroup):
    WAITING_REMINDER = State()

@router.callback_query(F.data == "reminder")
async def reminder_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.reply_text("О чём напомнить и когда? (Например, 'Сделать уроки через 10 минут')")
    await state.set_state(ReminderStates.WAITING_REMINDER)

@router.message(ReminderStates.WAITING_REMINDER)
async def handle_reminder(message: Message, state: FSMContext):
    try:
        reminder_text, delay_part = message.text.rsplit(" через ", 1)
        minutes = int(delay_part.split()[0])
        reminder_time = datetime.now() + timedelta(minutes=minutes)
        save_reminder(str(message.from_user.id), reminder_text, reminder_time)
        await message.reply_text(f"Поняла! Напомню: '{reminder_text}' через {minutes} минут. 🔔")
    except Exception:
        await message.reply_text("Пожалуйста, напиши в формате: 'Сделать уроки через 10 минут'")
    await state.clear()

async def check_reminders(bot: Bot):
    while True:
        now = datetime.now()
        for user_id, reminders in [(u, load_reminders(u)) for u in read_memory("global")]:
            for reminder_text, remind_time in reminders:
                if now >= remind_time:
                    try:
                        await bot.send_message(
                            chat_id=int(user_id),
                            text=f"🔔 *Напоминание*: {reminder_text}"
                        )
                        delete_reminder(user_id, reminder_text, remind_time)
                    except Exception as e:
                        logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
        await asyncio.sleep(30)