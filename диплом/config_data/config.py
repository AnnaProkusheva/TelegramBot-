"""
Модуль конфигурации проекта.
Загружает переменные окружения из .env и определяет базовые константы и команды бота
"""

import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не найдены, создайте .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KINOPOISK_TOKEN = os.getenv("API_KINOPOISK_TOKEN")


# Команды бота с описаниями
DEFAULT_COMMANDS = [
    ("start", "Запустить бота"),
    ("help", "Получить помощь"),
    ("movie_search", "Поиск фильма по названию"),
    ("movie_by_rating", "Поиск фильмов по рейтингу"),
    ("movie_by_genre", "Поиск фильма по жанру"),
    ("low_budget_movie", "Фильмы с низким бюджетом"),
    ("high_budget_movie", "Фильмы с высоким бюджетом"),
    ("history", "История запросов"),
]
