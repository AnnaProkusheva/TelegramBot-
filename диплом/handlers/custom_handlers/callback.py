"""
Обработчики callback-запросов от inline-кнопок Telegram бота.
"""

from utils.logger_config import logger
from api.kinopoisk_api import search_films_by_low_budget, search_films_by_high_budget
from states import MovieSearchStates
from database import User, FavoriteMovie
from utils.misc.formatters import format_film_info
from telebot.types import CallbackQuery

MAX_MESSAGE_LENGTH = 4000


def send_long_message(bot, chat_id: int, text: str) -> None:
    """
    Разбивает длинное сообщение на части, чтобы не превышать лимит Telegram.
    Args:
        bot: Экземпляр бота.
        chat_id (int): ID чата для отправки.
        text (str): Текст сообщения.
    """
    while text:
        if len(text) > MAX_MESSAGE_LENGTH:
            part = text[:MAX_MESSAGE_LENGTH]
            last_newline = part.rfind('\n')
            if last_newline != -1:
                part = part[:last_newline]
                text = text[last_newline + 1 :]
            else:
                text = text[MAX_MESSAGE_LENGTH:]
        else:
            part = text
            text = ''
        bot.send_message(chat_id, part)


def register_callback_handlers(bot) -> None:
    """
    Регистрирует универсальный обработчик для всех callback-запросов inline-кнопок.
    Args:
        bot: Экземпляр Telegram бота.
    """

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline_handler(call: CallbackQuery) -> None:
        bot.answer_callback_query(call.id)
        data = call.data
        chat_id = call.message.chat.id
        user_id = call.from_user.id

        logger.info(f"Пользователь {user_id} нажал кнопку с callback_data '{data}'")

        if data == "movie_search":
            bot.set_state(user_id, MovieSearchStates.waiting_for_name, chat_id)
            bot.send_message(chat_id, "Введите название фильма:")
        elif data == "movie_by_rating":
            bot.set_state(user_id, MovieSearchStates.waiting_for_rating, chat_id)
            bot.send_message(chat_id, "Введите минимальный рейтинг IMDB:")
        elif data == "movie_by_genre":
            bot.set_state(user_id, MovieSearchStates.waiting_for_genre, chat_id)
            bot.send_message(chat_id, "Введите жанр фильма:")
        elif data == "low_budget_movie":
            films = search_films_by_low_budget()
            if films:
                reply = "Фильмы с низким бюджетом:\n\n"
                for film in films[:5]:
                    name = (
                        film.get("name")
                        or film.get("alternativeName")
                        or "Название неизвестно"
                    )
                    reply += f"{name}\n"
                send_long_message(bot, chat_id, reply)
            else:
                bot.send_message(chat_id, "Фильмы с низким бюджетом не найдены.")
        elif data == "high_budget_movie":
            films = search_films_by_high_budget()
            if films:
                reply = "Фильмы с высоким бюджетом:\n\n"
                for film in films[:5]:
                    name = (
                        film.get("name")
                        or film.get("alternativeName")
                        or "Название неизвестно"
                    )
                    reply += f"{name}\n"
                send_long_message(bot, chat_id, reply)
            else:
                bot.send_message(chat_id, "Фильмы с высоким бюджетом не найдены.")
        elif data == "history":
            bot.set_state(user_id, MovieSearchStates.waiting_for_history_date, chat_id)
            bot.send_message(chat_id, "Введите дату для истории:")
        elif data == "help":
            bot.send_message(
                chat_id, "Доступные команды:\n/start\n/help\n/movie_search\n..."
            )
        elif data == "show_favorites":
            user, _ = User.get_or_create(user_id=str(user_id))
            favorites = FavoriteMovie.select().where(FavoriteMovie.user == user)
            if not favorites.exists():
                bot.send_message(chat_id, "Ваш список избранных фильмов пуст.")
                return
            reply = "Ваши избранные фильмы:\n\n"
            for fav in favorites:
                film_data = {
                    "name": fav.title or "Название неизвестно",
                    "description": fav.description or "Нет описания",
                    "year": fav.movie_year or "неизвестно",
                    "rating": {"kp": float(fav.rating) if fav.rating else None},
                    "genres": (
                        [{"name": g.strip()} for g in fav.movie_genre.split(",")]
                        if fav.movie_genre
                        else []
                    ),
                    "ratingAgeLimits": {"name": fav.movie_age_limit or "—"},
                    "poster": {"url": fav.movie_poster_url},
                }
                reply += format_film_info(film_data) + "\n---\n"
            send_long_message(bot, chat_id, reply)
        else:
            bot.send_message(chat_id, "Неизвестная команда.")
