"""
Inline-клавиатуры для Telegram бота.
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_inline_keyboard():
    """
    Возвращает основную инлайн клавиатуру меню с кнопками.

    Returns:
         InlineKeyboardMarkup: Объект клавиатуры для Telegram.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Поиск по названию", callback_data="movie_search"),
        InlineKeyboardButton("Поиск по рейтингу", callback_data="movie_by_rating"),
        InlineKeyboardButton("Поиск по жанру", callback_data="movie_by_genre"),
        InlineKeyboardButton("Низкий бюджет", callback_data="low_budget_movie"),
        InlineKeyboardButton("Высокий бюджет", callback_data="high_budget_movie"),
        InlineKeyboardButton("История", callback_data="history"),
        InlineKeyboardButton("Просмотр избранного", callback_data="show_favorites"),
    )
    return keyboard
