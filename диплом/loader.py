"""
Инициализация и конфигурация Telegram бота с использованием StateMemoryStorage для управления состояниями.
"""
from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config

#Хранилище состояний пользователя в памяти
storage = StateMemoryStorage()

#Создание экземпляра бота с токеном и системой хранения состояний
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
