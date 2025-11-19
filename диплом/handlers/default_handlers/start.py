"""
Обработчик команды /start для приветствия пользователя и начала взаимодействия с ботом.
"""

from telebot import TeleBot
from keyboards.inline import get_main_inline_keyboard
from utils.logger_config import logger


def register_start_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик команды /start, отправляющий приветственное сообщение с клавиатурой.

    Args:
        bot (TeleBot): Экземпляр Telegram бота.
    """

    @bot.message_handler(commands=["start"])
    def start_command(message):
        """
        Обработка команды /start.
        Отправляет пользователю приветственное сообщение и инлайн клавиатуру.

        Args:
            message (telebot.types.Message): Сообщение Telegram от пользователя.
        """
        logger.info(f"Пользователь {message.from_user.id} вызвал команду /start")
        welcome_text = (
            "Привет! Я бот для поиска фильмов.\n"
            "Используйте клавиатуру или /help для просмотра команд.\n"
            "Команда /tmdb_search позволяет искать фильмы через TMDB."
        )
        keyboard = get_main_inline_keyboard()
        bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)
