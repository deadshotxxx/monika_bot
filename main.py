import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from monika_bot.handlers import (
    start, advice, mood, reminder, quiz, study, goal, profile, daily_quote, mafia, auto_message, parent
)
from monika_bot.services.db_service import init_db
from monika_bot.services.report_service import send_daily_report
from monika_bot.handlers.auto_message import send_auto_messages
from monika_bot.logging_config import setup_logging

async def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Monika Bot")

    init_db()
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        start.router, advice.router, mood.router, reminder.router, quiz.router,
        study.router, goal.router, profile.router, daily_quote.router, mafia.router,
        auto_message.router, parent.router
    )

    asyncio.create_task(send_auto_messages(bot))
    asyncio.create_task(send_daily_report(bot))
    asyncio.create_task(reminder.check_reminders(bot))
    asyncio.create_task(daily_quote.send_daily_quote(bot))

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Polling error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())