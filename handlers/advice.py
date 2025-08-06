from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from monika_bot.services.ai_service import ask_ai
import logging

logger = logging.getLogger(__name__)
router = Router()

class AdviceStates(StatesGroup):
    WAITING_ADVICE = State()

@router.callback_query(F.data == "advice")
async def advice_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.reply_text("Что у тебя на душе? Спроси меня, и я дам совет! 😊")
    await state.set_state(AdviceStates.WAITING_ADVICE)

@router.message(AdviceStates.WAITING_ADVICE)
async def handle_advice(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    response = await ask_ai(user_id, message.text, "advice", message.bot)
    await message.reply_text(response)
    update_memory("global", {user_id: read_memory("global").get(user_id, {}).update({"interests": [message.text.lower()]})})
    await state.clear()