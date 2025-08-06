from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from monika_bot.services.mafia_service import start_mafia_game, load_mafia_game
import logging

logger = logging.getLogger(__name__)
router = Router()

class MafiaStates(StatesGroup):
    PLAYING = State()

@router.callback_query(F.data == "mafia")
async def start_mafia(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = str(callback.from_user.id)
    game = start_mafia_game(user_id)
    keyboard = [[{"text": char, "callback_data": f"mafia_{char}"} for char in game.alive]]
    await callback.message.reply_text(
        await game.start_game(callback.message.bot),
        reply_markup={"inline_keyboard": keyboard}
    )
    await state.set_state(MafiaStates.PLAYING)

@router.callback_query(F.data.startswith("mafia_"))
async def handle_mafia_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = str(callback.from_user.id)
    choice = callback.data.replace("mafia_", "")
    game = load_mafia_game(user_id)
    
    phase = game.state
    response, game_over = await game.make_choice(choice, phase, callback.message.bot)
    
    if not game_over:
        game.state = "day" if phase == "night" else "night"
        update_memory("game", {user_id: {"status": "ongoing", "day": game.day, "alive": game.alive, "state": game.state}})
        next_message = await game.day_phase(callback.message.bot) if game.state == "day" else await game.night_phase(callback.message.bot)
        keyboard = [[{"text": char, "callback_data": f"mafia_{char}"} for char in game.alive]]
    else:
        keyboard = [[{"text": "Играть снова!", "callback_data": "mafia"}]]
        next_message = response
    
    await callback.message.reply_text(
        f"{response}\n{next_message}",
        reply_markup={"inline_keyboard": keyboard}
    )
    if game_over:
        await state.clear()