"""
Обработчики основных команд бота и клавиатурных нажатий.
"""

from telebot import TeleBot
from keyboards.inline import get_main_inline_keyboard
from utils.logger_config import logger


def register_help_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчики команд /start, /stop, /help и обработку нажатий текстовых кнопок.

    Args:
        bot (TeleBot): Экземпляр Telegram бота.
    """

    @bot.message_handler(commands=["help"])
    def help_command(message):
        logger.info(f"Пользователь {message.from_user.id} вызвал команду /help")
        help_text = (
            "Доступные команды:\n"
            "/moviesearch - Поиск фильма по названию через Kinopoisk\n"
            "/movie_by_rating - Поиск фильмов по рейтингу\n"
            "/movie_by_genre - Поиск фильма по жанру\n"
            "/low_budget_movie - Фильмы с низким бюджетом\n"
            "/high_budget_movie - Фильмы с высоким бюджетом\n"
            "/history - История запросов\n"
            "/help - Вывод этого сообщения\n\n"
            "Выберите команду с помощью кнопок ниже."
        )
        inline_kb = get_main_inline_keyboard()
        bot.send_message(message.chat.id, help_text, reply_markup=inline_kb)
