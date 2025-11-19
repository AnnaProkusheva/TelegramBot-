"""
Обработчики основных команд Telegram бота и клавиатурных нажатий.
"""

from telebot import TeleBot
from keyboards.reply import get_main_reply_keyboard
from keyboards.inline import get_main_inline_keyboard
from telebot.types import Message


def register_command_handlers(bot: TeleBot) -> None:
    """
    Регистрирует обработчики команд /start, /stop, /help и обработку нажатий текстовых кнопок.

    Args:
        bot (TeleBot): Экземпляр Telegram бота.
    """

    @bot.message_handler(commands=["start"])
    def handle_start(message: Message) -> None:
        """
        Обработчик команды /start.
        Отправляет приветственное сообщение с использованием reply клавиатуры.
        """
        bot.send_message(
            message.chat.id,
            "Бот запущен! Используйте кнопки для управления.",
            reply_markup=get_main_reply_keyboard(),
        )

    @bot.message_handler(commands=["stop"])
    def handle_stop(message: Message) -> None:
        """
        Обработчик команды /stop.
        Отправляет сообщение о приостановке обработки.
        """
        bot.send_message(
            message.chat.id, "Обработка остановлена. Для возобновления нажмите /start."
        )

    @bot.message_handler(commands=["help"])
    def handle_help(message: Message) -> None:
        """
        Обработчик команды /help.
        Отправляет сообщение с перечнем доступных команд и inline клавиатурой.
        """
        inline_kb = get_main_inline_keyboard()
        bot.send_message(message.chat.id, "Выберите команду:", reply_markup=inline_kb)

    # Обработка нажатий reply-кнопок (текста)
    @bot.message_handler(func=lambda m: m.text == "Старт")
    def handle_start_text(message: Message) -> None:
        """
        Обработка нажатия кнопки "Старт" в reply клавиатуре.
        Вызывает обработчик /start.
        """
        handle_start(message)

    @bot.message_handler(func=lambda m: m.text == "Стоп")
    def handle_stop_text(message: Message) -> None:
        """
        Обработка нажатия кнопки "Стоп" в reply клавиатуре.
        Вызывает обработчик /stop.
        """
        handle_stop(message)

    @bot.message_handler(func=lambda m: m.text == "Помощь")
    def handle_help_text(message: Message) -> None:
        """
        Обработка нажатия кнопки "Помощь" в reply клавиатуре.
        Вызывает обработчик /help.
        """
        handle_help(message)
