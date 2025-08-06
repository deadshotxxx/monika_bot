from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from monika_bot.services.quiz_service import get_quiz_question, validate_quiz_answer
import logging

logger = logging.getLogger(__name__)
router = Router()

class QuizStates(StatesGroup):
    WAITING_ANSWER = State()

@router.callback_query(F.data == "quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = str(callback.from_user.id)
    question = await get_quiz_question(user_id, callback.message.bot)
    await state.update_data(question=question)
    keyboard = [
        [{"text": opt, "callback_data": f"quiz_{opt}"} for opt in question["options"][:2]],
        [{"text": opt, "callback_data": f"quiz_{opt}"} for opt in question["options"][2:]]
    ]
    await callback.message.reply_text(
        question["question"],
        reply_markup={"inline_keyboard": keyboard}
    )
    await state.set_state(QuizStates.WAITING_ANSWER)

@router.callback_query(F.data.startswith("quiz_"))
async def handle_quiz_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = str(callback.from_user.id)
    user_answer = callback.data.replace("quiz_", "")
    data = await state.get_data()
    question = data["question"]
    correct, feedback = validate_quiz_answer(user_id, question, user_answer)
    score = read_memory("quiz").get(user_id, {}).get("score", 0)
    await callback.message.reply_text(
        f"{feedback}\nТвой счёт: {score}. Хочешь ещё вопрос?",
        reply_markup={"inline_keyboard": [[{"text": "Ещё!", "callback_data": "quiz"}]]}
    )
    await state.clear()