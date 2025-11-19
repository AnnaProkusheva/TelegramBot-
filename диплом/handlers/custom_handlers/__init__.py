"""
Регистрирует все кастомные обработчики команд Telegram бота.
"""

from telebot import TeleBot
from .genre import register_genre_handler
from .name_search import register_name_search
from .rating import register_rating_handler
from .low_budget import register_low_budget_handler
from .high_budget import register_high_budget_handler
from .history import register_history_handler
from .favorites import register_favorite_handler, register_favorite_callback_handler


def register_custom_handlers(bot: TeleBot) -> None:
    register_genre_handler(bot)
    register_name_search(bot)
    register_rating_handler(bot)
    register_low_budget_handler(bot)
    register_high_budget_handler(bot)
    register_history_handler(bot)
    register_favorite_handler(bot)
    register_favorite_callback_handler(bot)
