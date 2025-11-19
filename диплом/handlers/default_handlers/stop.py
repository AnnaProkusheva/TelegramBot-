"""
Обработчики команд /stop и /start для управления статусом активности пользователя.
"""
from telebot import TeleBot
from telebot.types import Message

#Словарь состояния активности пользователя: True - активен, False - остановлен
user_active_status = {}


def register_stop_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчики команд /stop и /start,
    управляя статусом активности пользователя и состояниями бота.

    Args:
        bot (TeleBot): Экземпляр Telegram бота.
    """
    @bot.message_handler(commands=["stop", "Стоп"])
    def handle_stop(message: Message) -> None:
        """
        Обработчик команды /stop.
        Устанавливает пользователя как неактивного, удаляет состояние и сообщает об остановке.

        Args:
            message (Message): Telegram сообщение пользователя.
        """
        user_active_status[message.from_user.id] = False
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(
            message.chat.id, "Обработка остановлена. Для возобновления нажмите /start."
        )

    @bot.message_handler(commands=["start", "Старт"])
    def handle_start(message: Message) -> None:
        """
        Обработчик команды /start.
        Устанавливает пользователя как активного и отправляет приветственное сообщение.

        Args:
            message (Message): Telegram сообщение пользователя.
        """
        user_active_status[message.from_user.id] = True
        bot.send_message(message.chat.id, "Бот запущен, отправляйте команды.")

    def user_is_active(func):
        """
        Декоратор, позволяющий выполнять обработчик только если пользователь активен.

        Args:
            func (callable): Обработчик сообщения.

        Returns:
            callable: Обработчик с проверкой активности пользователя.
        """
        def wrapper(message: Message):
            if user_active_status.get(message.from_user.id, True):
                return func(message)
            else:
                # Игнорируем, если пользователь остановил бота
                return

        return wrapper
