import logging
from monika_bot.services.memory import read_memory, update_memory
from openai import AsyncOpenAI
import os
from datetime import datetime

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def build_context_prompt(user_id: str, user_input: str, mode: str) -> str:
    global_memory = read_memory("global").get(user_id, {})
    mood_data = read_memory("mood").get(user_id, [])
    goals_data = read_memory("goals").get(user_id, [])
    learning_data = read_memory("learning").get(user_id, [])

    name = global_memory.get("name", "Друг")
    tone = global_memory.get("tone", "мягкое и дружелюбное")
    interests = global_memory.get("interests", [])

    context_lines = [
        f"Ты Моника, заботливый ИИ-наставник для 11-летней девочки по имени {name}.",
        f"Тон общения: {tone}.",
        f"Текущий режим: {mode}.",
        "Контекст о пользователе:"
    ]
    if mood_data:
        context_lines.append(f"- Недавнее настроение: {mood_data[-1]['mood'] if mood_data else 'неизвестно'}")
    if goals_data:
        context_lines.append(f"- Цели: {', '.join(goals_data)}")
    if interests:
        context_lines.append(f"- Интересы: {', '.join(interests)}")
    if learning_data:
        context_lines.append(f"- Темы обучения: {', '.join([t['topic'] for t in learning_data])}")
    context_lines.append(f"Пользователь написал: {user_input}")
    
    if mode == "advice":
        context_lines.append("Дай простой, добрый и поддерживающий совет, подходящий для 11-летней девочки.")
    elif mode == "mood":
        context_lines.append("Проанализируй настроение и предложи поддержку или мотивацию.")
    elif mode == "study":
        context_lines.append("Объясни тему просто, как для 11-летней девочки.")
    elif mode == "quiz":
        context_lines.append("Создай образовательный вопрос для викторины в формате: {'question': 'текст', 'options': ['a', 'b', 'c', 'd'], 'answer': 'правильный ответ'}.")
    elif mode == "goal":
        context_lines.append("Помоги сформулировать или поддержать цель.")
    elif mode == "mafia":
        context_lines.append("Создай короткое описание персонажа для игры 'Мафия', подходящее для 11-летней девочки.")
    
    return "\n".join(context_lines)

async def is_personal_topic(user_id: str, user_input: str, bot) -> tuple[bool, str]:
    prompt = (
        f"Ты заботливый ИИ-наставник для 11-летней девочки. Проанализируй текст: '{user_input}'. "
        "Является ли он личным или эмоционально тяжёлым, требующим обсуждения с родителями? "
        "Ответь в формате: 'да|нет|причина'. Например: 'да|Это эмоциональная тема, связанная с отношениями.'"
    )
    try:
        cache = read_memory("cache")
        if prompt in cache:
            response = cache[prompt]
        else:
            completion = await client.chat.completions.create(
                model="horizon-beta",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7,
                extra_headers={
                    "HTTP-Referer": "https://github.com/yourusername/yourrepo",
                    "X-Title": "Monika AI Assistant",
                }
            )
            response = completion.choices[0].message.content.strip()
            cache[prompt] = response
            update_memory("cache", cache)
        
        is_personal, reason = response.split("|", 1)
        if is_personal.lower() == "да" and "критическая" in reason.lower():
            from monika_bot.services.report_service import send_critical_report
            await send_critical_report(bot, user_id, user_input)
        return is_personal.lower() == "да", reason
    except Exception as e:
        logger.error(f"Ошибка Horizon Beta при анализе личных тем: {e}")
        return False, "Не удалось проанализировать запрос"

async def ask_ai(user_id: str, user_input: str, mode: str, bot) -> str:
    from monika_bot.services.report_service import log_potential_issue
    is_personal, reason = await is_personal_topic(user_id, user_input, bot)
    if is_personal:
        log_potential_issue(user_id, user_input)
        return (
            f"Я тебя понимаю, {read_memory('global').get(user_id, {}).get('name', 'Друг')} 😊 "
            f"Это звучит как что-то важное. Лучше обсудить это с родителями, они смогут помочь. "
            f"Хочешь, я помогу придумать, как им рассказать?"
        )

    prompt = build_context_prompt(user_id, user_input, mode)
    cache = read_memory("cache")
    if prompt in cache:
        return cache[prompt]
    
    try:
        completion = await client.chat.completions.create(
            model="horizon-beta",
            messages=[
                {"role": "system", "content": "Ты Моника, заботливая и эмпатичная ИИ-подруга для 11-летней девочки, отвечаешь на русском языке с теплотой и поддержкой."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "https://github.com/yourusername/yourrepo",
                "X-Title": "Monika AI Assistant",
            }
        )
        response = completion.choices[0].message.content.strip()
        cache[prompt] = response
        update_memory("cache", cache)
        return response
    except Exception as e:
        logger.error(f"Ошибка Horizon Beta: {e}")
        return "Ой, что-то пошло не так! Попробуй ещё раз."