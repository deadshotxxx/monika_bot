import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)
DB_FILE = Path("monika_bot/monika_user_data.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            reminder_text TEXT,
            remind_time TEXT
        )''')
        conn.commit()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        conn.close()

def save_reminder(user_id: str, reminder_text: str, remind_time: datetime):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO reminders (user_id, reminder_text, remind_time) VALUES (?, ?, ?)",
                  (user_id, reminder_text, remind_time.isoformat()))
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving reminder: {e}")
    finally:
        conn.close()

def load_reminders(user_id: str) -> list:
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT reminder_text, remind_time FROM reminders WHERE user_id = ?", (user_id,))
        reminders = [(row[0], datetime.fromisoformat(row[1])) for row in c.fetchall()]
        return reminders
    except Exception as e:
        logger.error(f"Error loading reminders: {e}")
        return []
    finally:
        conn.close()

def delete_reminder(user_id: str, reminder_text: str, remind_time: datetime):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM reminders WHERE user_id = ? AND reminder_text = ? AND remind_time = ?",
                  (user_id, reminder_text, remind_time.isoformat()))
        conn.commit()
    except Exception as e:
        logger.error(f"Error deleting reminder: {e}")
    finally:
        conn.close()