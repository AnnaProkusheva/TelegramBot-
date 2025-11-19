from telebot import TeleBot
from .start import register_start_handler
from .help import register_help_handler
from .stop import register_stop_handler
from .command_handlers import register_command_handlers


def register_default_handlers(bot: TeleBot) -> None:
    """
    Регистрирует стандартные обработчики команд в боте.

    Args:
        bot (TeleBot): Экземпляр Telegram бота.
    """
    register_start_handler(bot)
    register_help_handler(bot)
    register_stop_handler(bot)
    register_command_handlers(bot)
