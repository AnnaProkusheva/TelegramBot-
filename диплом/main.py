"""
Главный скрипт запуска Telegram бота.
Инициализация, регистрация обработчиков, запуск polling.
"""

import telebot
from telebot.storage import StateMemoryStorage
from telebot import custom_filters
from config_data.config import BOT_TOKEN
from database import initialize_db
from handlers.default_handlers import register_default_handlers
from handlers.custom_handlers import register_custom_handlers
from handlers.custom_handlers.callback import register_callback_handlers
from utils.logger_config import logger
import time

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)

bot.add_custom_filter(custom_filters.StateFilter(bot))


def main():
    """
    Главная функция запуска бота.
    Подключает базу и регистрирует обработчики.
    Запускает бесконечный цикл polling Telegram API.
    """
    print("Бот запущен...")
    logger.info("Запуск бота.")

    initialize_db()

    register_default_handlers(bot)
    register_custom_handlers(bot)
    register_callback_handlers(bot)

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            logger.error(f"Ошибка в основном цикле бота: {e}", exc_info=True)
            print(f"Ошибка: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
