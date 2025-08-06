import random
import logging
from monika_bot.services.memory import read_memory, update_memory
from monika_bot.services.ai_service import ask_ai

logger = logging.getLogger(__name__)

async def get_quiz_question(user_id: str, bot) -> dict:
    quiz_data = read_memory("quiz")
    learning_data = read_memory("learning").get(user_id, [])
    interests = read_memory("global").get(user_id, {}).get("interests", [])
    
    if learning_data and random.random() < 0.5:
        topic = random.choice([t["topic"] for t in learning_data])
        question = await ask_ai(user_id, f"Создай вопрос по теме '{topic}'", "quiz", bot)
        return eval(question)  # Предполагается, что Horizon Beta возвращает JSON-подобный формат
    elif interests:
        question = await ask_ai(user_id, f"Создай вопрос на основе интересов: {', '.join(interests)}", "quiz", bot)
        return eval(question)
    
    default_quiz = {
        "question": "Какая планета самая большая?",
        "options": ["Земля", "Юпитер", "Марс", "Сатурн"],
        "answer": "Юпитер"
    }
    return default_quiz

def validate_quiz_answer(user_id: str, question: dict, user_answer: str) -> tuple[bool, str]:
    correct = user_answer.lower() == question["answer"].lower()
    feedback = "Молодец, это правильный ответ! 🎉" if correct else f"Не совсем, правильный ответ: {question['answer']}. Попробуем ещё?"
    if correct:
        score = read_memory("quiz").get(user_id, {}).get("score", 0) + 1
        update_memory("quiz", {user_id: {"score": score}})
        global_memory = read_memory("global").get(user_id, {})
        points = global_memory.get("points", 0) + 1
        global_memory["points"] = points
        update_memory("global", {user_id: global_memory})
    return correct, feedback