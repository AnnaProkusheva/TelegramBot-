"""
Обработчики команд и callback для управления списком избранных фильмов пользователя.
"""

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from database import User, FavoriteMovie
from utils.logger_config import logger
from utils.misc.formatters import get_favorite_inline_keyboard, format_film_info
from api.kinopoisk_api import session, API_KINOPOISK_TOKEN  # импорт из kinopoisk_api.py


def get_film_data_by_id(movie_id: str) -> dict | None:
    """
    Получение подробных данных о фильме по его ID из API Кинопоиска.

    Args:
        movie_id (str): Идентификатор фильма

    Returns:
         dcit | None: Словарь с данными фильма, или None при ошибке.
    """
    headers = {"X-API-KEY": API_KINOPOISK_TOKEN}
    response = session.get(
        f"https://api.kinopoisk.dev/v1.4/movie/{movie_id}", headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        logger.error(
            f"Ошибка при получении данных фильма с ID {movie_id}: {response.text}"
        )
        return None


def register_favorite_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчики сообщений для работы с избранным:
    добавление, показ и удаление фильмов из избранного.

    Args:
        bot (Telebot): Экземпляр Telegram бота.
    """

    @bot.message_handler(commands=['add_favorite'])
    def add_favorite(message: Message):
        user_id = str(message.from_user.id)
        user, _ = User.get_or_create(user_id=user_id)

        try:
            _, movie_id, title = message.text.split(maxsplit=2)
        except ValueError:
            bot.send_message(
                message.chat.id,
                'Неверный формат команды. Используйте:\n/add_favorite <movie_id> <название фильма>',
            )
            return

        exists = (
            FavoriteMovie.select()
            .where((FavoriteMovie.user == user) & (FavoriteMovie.movie_id == movie_id))
            .exists()
        )
        if exists:
            bot.send_message(message.chat.id, 'Этот фильм уже добавлен в избранное.')
            return

        film_data = get_film_data_by_id(movie_id)
        if not film_data:
            bot.send_message(
                message.chat.id, "Не удалось получить данные фильма по ID."
            )
            return

        FavoriteMovie.create(
            user=user,
            movie_id=movie_id,
            title=film_data.get("name") or "Название неизвестно",
            description=film_data.get("description"),
            rating=str(
                film_data.get("rating", {}).get("kp")
                or film_data.get("rating", {}).get("imdb")
            ),
            movie_year=str(film_data.get("year")),
            movie_genre=", ".join(g.get("name") for g in film_data.get("genres", [])),
            movie_age_limit=film_data.get("ratingAgeLimits", {}).get("name"),
            movie_poster_url=film_data.get("poster", {}).get("url"),
        )
        bot.send_message(
            message.chat.id, f'Фильм "{film_data.get("name")}" добавлен в избранное.'
        )
        logger.info(
            f'Пользователь {user_id} добавил фильм "{film_data.get("name")}" в избранное.'
        )

    @bot.message_handler(commands=['favorites'])
    def show_favorites(message: Message):
        user_id = str(message.from_user.id)
        user, _ = User.get_or_create(user_id=user_id)

        favorites = FavoriteMovie.select().where(FavoriteMovie.user == user)

        if favorites.count() == 0:
            bot.send_message(message.chat.id, 'Ваш список избранных фильмов пуст.')
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

        bot.send_message(message.chat.id, reply)

    @bot.message_handler(commands=['remove_favorite'])
    def remove_favorite(message: Message):
        user_id = str(message.from_user.id)
        user, _ = User.get_or_create(user_id=user_id)

        try:
            _, movie_id = message.text.split(maxsplit=1)
        except ValueError:
            bot.send_message(
                message.chat.id,
                'Неверный формат команды. Используйте:\n/remove_favorite <movie_id>',
            )
            return

        deleted = (
            FavoriteMovie.delete()
            .where((FavoriteMovie.user == user) & (FavoriteMovie.movie_id == movie_id))
            .execute()
        )

        if deleted:
            bot.send_message(
                message.chat.id, f'Фильм с ID {movie_id} удалён из избранного.'
            )
            logger.info(
                f'Пользователь {user_id} удалил фильм с ID {movie_id} из избранного.'
            )
        else:
            bot.send_message(message.chat.id, 'Фильм не найден в вашем избранном.')


def register_favorite_callback_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчик callback запросов для inline кнопок добавления и удаоения
    фильмов из избранного.

    Args:
        bot (Telebot): Экземпляр бота.
    """

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith(("add_fav:", "remove_fav:"))
    )
    def favorite_callback_handler(call: CallbackQuery):
        try:
            action, movie_id = call.data.split(":")
            user_id = str(call.from_user.id)
            user, _ = User.get_or_create(user_id=user_id)

            if action == "add_fav":
                exists = (
                    FavoriteMovie.select()
                    .where(
                        (FavoriteMovie.user == user)
                        & (FavoriteMovie.movie_id == movie_id)
                    )
                    .exists()
                )
                if exists:
                    bot.answer_callback_query(call.id, text="Фильм уже в избранном")
                    return

                film_data = get_film_data_by_id(movie_id)
                if not film_data:
                    bot.answer_callback_query(
                        call.id, text="Не удалось получить данные фильма"
                    )
                    return

                FavoriteMovie.create(
                    user=user,
                    movie_id=movie_id,
                    title=film_data.get("name") or "Название неизвестно",
                    description=film_data.get("description"),
                    rating=str(
                        film_data.get("rating", {}).get("kp")
                        or film_data.get("rating", {}).get("imdb")
                    ),
                    movie_year=str(film_data.get("year")),
                    movie_genre=", ".join(
                        g.get("name") for g in film_data.get("genres", [])
                    ),
                    movie_age_limit=film_data.get("ratingAgeLimits", {}).get("name"),
                    movie_poster_url=film_data.get("poster", {}).get("url"),
                )
                bot.answer_callback_query(call.id, text="Добавлено в избранное")
            elif action == "remove_fav":
                deleted = (
                    FavoriteMovie.delete()
                    .where(
                        (FavoriteMovie.user == user)
                        & (FavoriteMovie.movie_id == movie_id)
                    )
                    .execute()
                )
                if deleted:
                    bot.answer_callback_query(call.id, text="Удалено из избранного")
                else:
                    bot.answer_callback_query(
                        call.id, text="Фильм не найден в избранном"
                    )
            else:
                bot.answer_callback_query(call.id, text="Неизвестное действие")

            is_favorite = (
                FavoriteMovie.select()
                .where(
                    (FavoriteMovie.user == user) & (FavoriteMovie.movie_id == movie_id)
                )
                .exists()
            )

            keyboard = get_favorite_inline_keyboard(movie_id, is_favorite)
            bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в favorite_callback_handler: {e}", exc_info=True)
            bot.answer_callback_query(call.id, text=f"Ошибка: {e}")
