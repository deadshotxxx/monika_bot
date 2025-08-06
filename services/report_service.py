import asyncio
from datetime import datetime
from aiogram import Bot
from monika_bot.services.memory import read_memory, update_memory
import logging

logger = logging.getLogger(__name__)
PARENT_TELEGRAM_ID = "YOUR_TELEGRAM_ID"  # Заменить на реальный ID

def log_potential_issue(user_id: str, issue: str):
    global_memory = read_memory("global").get(user_id, {})
    issues = global_memory.get("issues", [])
    issues.append({"date": datetime.now().isoformat(), "issue": issue})
    global_memory["issues"] = issues
    update_memory("global", {user_id: global_memory})

async def send_daily_report(bot: Bot):
    while True:
        now = datetime.now()
        if now.hour == 20 and now.minute == 0:
            try:
                users = read_memory("global")
                for user_id in users:
                    global_memory = users[user_id]
                    mood_data = read_memory("mood").get(user_id, [])
                    goals_data = read_memory("goals").get(user_id, [])
                    learning_data = read_memory("learning").get(user_id, [])
                    issues = global_memory.get("issues", [])

                    report = f"Отчёт по пользователю {user_id} ({global_memory.get('name', 'Друг')}):\n"
                    if mood_data:
                        report += f"- Последнее настроение: {mood_data[-1]['mood']} ({mood_data[-1]['date']})\n"
                    if goals_data:
                        report += f"- Цели: {', '.join(goals_data)}\n"
                    if learning_data:
                        report += f"- Темы учёбы: {', '.join([t['topic'] for t in learning_data])}\n"
                    if issues:
                        report += f"- Возможные проблемы: {', '.join([i['issue'] for i in issues[-3:]])}"

                    await bot.send_message(
                        chat_id=PARENT_TELEGRAM_ID,
                        text=report
                    )
            except Exception as e:
                logger.error(f"Ошибка отправки отчёта: {e}")
        await asyncio.sleep(60)

async def send_critical_report(bot: Bot, user_id: str, issue: str):
    try:
        name = read_memory("global").get(user_id, {}).get("name", "Друг")
        await bot.send_message(
            chat_id=PARENT_TELEGRAM_ID,
            text=f"Критическая ситуация: {name} (ID: {user_id}) сообщил(а): '{issue}'. Рекомендуется связаться."
        )
    except Exception as e:
        logger.error(f"Ошибка отправки критического отчёта: {e}")