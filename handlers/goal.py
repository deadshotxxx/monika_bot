from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from monika_bot.services.memory import read_memory, update_memory
from monika_bot.services.ai_service import ask_ai
import logging

logger = logging.getLogger(__name__)
router = Router()

class GoalStates(StatesGroup):
    WAITING_GOAL = State()

@router.callback_query(F.data == "goal")
async def goal_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.reply_text("Какую цель хочешь поставить или отследить? (Например, 'Подготовиться к тесту по математике')")
    await state.set_state(GoalStates.WAITING_GOAL)

@router.message(GoalStates.WAITING_GOAL)
async def handle_goal(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    goal = message.text.strip()
    update_memory("goals", {user_id: read_memory("goals").get(user_id, []) + [goal]})
    response = await ask_ai(user_id, f"Я поставил(а) новую цель: {goal}", "goal", message.bot)
    await message.reply_text(response)
    await state.clear()