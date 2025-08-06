from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from monika_bot.services.memory import read_memory, update_memory
from monika_bot.services.ai_service import ask_ai
import logging

logger = logging.getLogger(__name__)
router = Router()

class StudyStates(StatesGroup):
    WAITING_TOPIC = State()
    WAITING_TEST_ANSWER = State()

@router.callback_query(F.data == "study")
async def study_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.reply_text(
        "Какую тему хочешь изучить или проверить знания? 📚 Например, 'Математика' или 'Наука'."
    )
    await state.set_state(StudyStates.WAITING_TOPIC)

@router.message(StudyStates.WAITING_TOPIC)
async def handle_study_topic(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    topic = message.text.strip()
    learning_data = read_memory("learning").get(user_id, [])
    learning_data.append({"topic": topic, "tests": []})
    update_memory("learning", {user_id: learning_data})
    
    tests = next((t["tests"] for t in learning_data if t["topic"] == topic), [])
    if tests:
        test = tests[0]
        await state.update_data(test=test)
        keyboard = [
            [{"text": opt, "callback_data": f"test_{opt}"} for opt in test["options"][:2]],
            [{"text": opt, "callback_data": f"test_{opt}"} for opt in test["options"][2:]]
        ]
        await message.reply_text(
            test["question"],
            reply_markup={"inline_keyboard": keyboard}
        )
        await state.set_state(StudyStates.WAITING_TEST_ANSWER)
    else:
        response = await ask_ai(user_id, f"Объясни тему: {topic}", "study", message.bot)
        await message.reply_text(response)

@router.callback_query(F.data.startswith("test_"))
async def handle_test_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = str(callback.from_user.id)
    user_answer = callback.data.replace("test_", "")
    data = await state.get_data()
    test = data["test"]
    
    correct = user_answer.lower() == test["answer"].lower()
    response = (
        f"{'Молодец, правильно! 🎉' if correct else f'Не совсем, правильный ответ: {test['answer']}.'} "
        f"Вот почему: {test['explanation']}"
    )
    if correct:
        global_memory = read_memory("global").get(user_id, {})
        points = global_memory.get("points", 0) + 1
        global_memory["points"] = points
        update_memory("global", {user_id: global_memory})
    await callback.message.reply_text(
        response,
        reply_markup={"inline_keyboard": [[{"text": "Ещё тест!", "callback_data": "study"}]]}
    )
    await state.clear()