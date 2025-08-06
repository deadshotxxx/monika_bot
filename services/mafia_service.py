import random
from monika_bot.services.memory import read_memory, update_memory
from monika_bot.services.ai_service import ask_ai
import logging

logger = logging.getLogger(__name__)

class MafiaGame:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.characters = ["Мирный житель 1", "Мирный житель 2", "Мафия", "Шериф", "Доктор"]
        self.alive = self.characters.copy()
        self.day = 1
        self.role = random.choice(["Шериф", "Доктор", "Мирный житель"])
        self.state = "day"
        self.saved_by_doctor = None
        self.descriptions = {}

    async def generate_description(self, character: str, bot) -> str:
        if character not in self.descriptions:
            desc = await ask_ai(self.user_id, f"Создай описание персонажа '{character}'", "mafia", bot)
            self.descriptions[character] = desc
        return self.descriptions[character]

    async def start_game(self, bot) -> str:
        descs = [f"{char}: {await self.generate_description(char, bot)}" for char in self.characters]
        return (
            f"Добро пожаловать в игру 'Мафия', {read_memory('global').get(self.user_id, {}).get('name', 'Друг')}!\n"
            f"Ты — {self.role}. В городе:\n{'\n'.join(descs)}\nНаступает день {self.day}. "
            f"Кого ты подозреваешь?"
        )

    async def night_phase(self, bot) -> str:
        if self.role == "Мафия":
            return "Ты — Мафия! Кого хочешь исключить этой ночью?"
        elif self.role == "Доктор":
            return "Ты — Доктор! Кого хочешь спасти этой ночью?"
        return "Ночь наступила, город спит. Ждём утра..."

    async def day_phase(self, bot) -> str:
        return f"День {self.day}. В городе: {', '.join(self.alive)}. Кого ты подозреваешь?"

    async def make_choice(self, choice: str, phase: str, bot) -> tuple[str, bool]:
        if choice not in self.alive:
            return "Такого персонажа нет или он уже исключён. Выбери другого!", False
        
        if phase == "night" and self.role == "Доктор":
            self.saved_by_doctor = choice
            return f"Ты спасла {choice} этой ночью. Наступает день {self.day}.", False
        elif phase == "night" and self.role == "Мафия":
            if choice == self.saved_by_doctor:
                return f"Мафия пыталась исключить {choice}, но Доктор спас его! Наступает день {self.day}.", False
            self.alive.remove(choice)
            if choice == "Шериф":
                update_memory("game", {self.user_id: {"status": "lose", "day": self.day}})
                return "Мафия исключила Шерифа... Город проиграл. 😔 Хочешь сыграть снова?", True
            return f"Мафия исключила {choice}. Наступает день {self.day}.", False
        
        self.alive.remove(choice)
        if choice == "Мафия":
            update_memory("game", {self.user_id: {"status": "win", "day": self.day}})
            return "Поздравляю! Ты нашла Мафию! Город спасён! 🎉 Хочешь сыграть ещё?", True
        self.day += 1
        if len(self.alive) <= 2:
            update_memory("game", {self.user_id: {"status": "lose", "day": self.day}})
            return "Увы, Мафия победила... 😔 Хочешь попробовать снова?", True
        return f"Ты исключила {choice}, но это был не Мафия. Наступает ночь {self.day}.", False

def start_mafia_game(user_id: str) -> 'MafiaGame':
    game = MafiaGame(user_id)
    update_memory("game", {user_id: {"status": "ongoing", "day": game.day, "alive": game.alive, "state": game.state}})
    return game

def load_mafia_game(user_id: str) -> 'MafiaGame':
    game_data = read_memory("game").get(user_id, {})
    if game_data.get("status") == "ongoing":
        game = MafiaGame(user_id)
        game.day = game_data.get("day", 1)
        game.alive = game_data.get("alive", game.characters)
        game.state = game_data.get("state", "day")
        return game
    return start_mafia_game(user_id)