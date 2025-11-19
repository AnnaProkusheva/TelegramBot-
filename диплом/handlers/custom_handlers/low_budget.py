"""
Обработчик команды для поиска и вывода фильмов с низким бюджетом.
"""

from telebot.types import Message
from api.kinopoisk_api import search_films_by_low_budget, search_films_by_high_budget
from utils.logger_config import logger
from .history import log_user_query
from utils.misc.formatters import format_film_info, format_films_list
from utils.misc.formatters import get_favorite_inline_keyboard
from database import User, FavoriteMovie


def send_film_with_fav_buttons(bot, chat_id: int, user_id: int, film: dict) -> None:
    """
    Отправляет информацию о фильме с кнопкой добавления/удаления из избранного.

    Args:
        bot: Экземпляр бота.
        chat_id (int): ID чата пользователя.
        user_id (int): ID пользователя.
        film (dict): Словарь с данными фильма.
    """
    movie_id = film.get("id") or str(film.get("kinopoiskId", "unknown"))

    user = User.get_or_none(user_id=str(user_id))
    is_favorite = False
    if user:
        is_favorite = (
            FavoriteMovie.select()
            .where((FavoriteMovie.user == user) & (FavoriteMovie.movie_id == movie_id))
            .exists()
        )

    reply_text = format_film_info(film)

    keyboard = get_favorite_inline_keyboard(movie_id, is_favorite)
    bot.send_message(chat_id, reply_text, reply_markup=keyboard)


def error_handler_decorator(bot):
    """
    Декоратор для обработки исключений в обработчиках команд бота.

    Args:
        bot: Экземпляр Telegram бота.

    Returns:
        Декоратор функции обработчика.
    """

    def decorator(func=None, *, custom_error_msg="Произошла ошибка. Попробуйте позже."):
        if func is None:

            def wrapper(f):
                return decorator(f, custom_error_msg=custom_error_msg)

            return wrapper

        def inner(message, *args, **kwargs):
            try:
                return func(message, *args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Ошибка в обработчике {func.__name__}: {e}", exc_info=True
                )
                bot.send_message(message.chat.id, custom_error_msg)

        return inner

    return decorator


def register_low_budget_handler(bot) -> None:
    """
    Регистрирует обработчик команды /low_budget_movie.

    Args:
        bot: Экземпляр Telegram бота
    """
    decorator = error_handler_decorator(bot)

    @bot.message_handler(commands=["low_budget_movie"])
    @decorator(
        custom_error_msg="Ошибка при поиске фильмов с низким бюджетом. Попробуйте позже."
    )
    def send_low_budget_movies(message: Message):
        log_user_query(message.from_user.id, message.text)
        films = search_films_by_low_budget()
        if films:
            warning = (
                "⚠️ На Кинопоиске отсутствуют точные данные о бюджете фильмов, "
                "поэтому результаты могут содержать неточную информацию.\n\n"
            )
            reply = "Фильмы с низким бюджетом:\n\n" + format_films_list(films)
            bot.send_message(message.chat.id, reply)
        else:
            bot.send_message(message.chat.id, "Фильмы с низким бюджетом не найдены.")
