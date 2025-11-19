"""
Обработчик команды и состояния для поиска фильмов по минимальному рейтингу IMDB.
"""

from telebot.types import Message
from api.kinopoisk_api import search_films_by_rating
from .history import log_user_query
from states import MovieSearchStates
from utils.logger_config import logger
from utils.misc.formatters import get_favorite_inline_keyboard, format_film_info
from database import User, FavoriteMovie

MAX_MESSAGE_LENGTH = 4000  # максимально допустимая длина сообщения в Telegram с запасом


def format_film(film: dict) -> str:
    """
    Форматирует подробную информацию о фильме для вывода в сообщении.

    Args:
        film (dict): Словарь с данными фильма.

    Returns:
        str: Отформатированный текст с данными фильма.
    """
    name = film.get('name') or film.get('alternativeName') or 'Название неизвестно'
    description = film.get('description', '')
    year = film.get('year', 'неизвестно')
    rating_data = film.get('rating', {})
    rating_kp = rating_data.get('kp')
    rating_imdb = rating_data.get('imdb')
    if rating_kp and rating_kp > 0:
        rating = rating_kp
    elif rating_imdb:
        rating = rating_imdb
    else:
        rating = 'Нет данных'

    genres_str = ', '.join([genre.get('name', '') for genre in film.get('genres', [])])
    age_limit = film.get('ratingAgeLimits', {}).get('name', '-')
    poster_url = film.get('poster', {}).get('url', '')

    info = (
        f'Название: {name}\nОписание: {description}\nРейтинг: {rating}\n'
        f'Год: {year}\nЖанр: {genres_str}\nВозрастной рейтинг: {age_limit}\n'
    )
    if poster_url:
        info += f'Постер: {poster_url}\n'
    return info


def send_long_message(bot, chat_id: int, text: str) -> None:
    """
    Разбивает длинное сообщение на части и отправляет несколько сообщений, чтобы не превышать лимит Telegram.

    Args:
        bot: Экземпляр бота.
        chat_id (int): ID чата для отправки сообщений.
        text (str): Текст для отправки.
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


def send_film_with_fav_buttons(bot, chat_id: int, user_id: int, film: dict) -> None:
    """
    Отправляет информацию о фильме с inline-кнопками добавления/удаления из избранного.

    Args:
        bot: Экземпляр бота.
        chat_id (int): ID чата.
        user_id (int): ID пользователя.
        film (dict): Информация о фильме.
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
    Декоратор для обработки ошибок в обработчиках сообщений.

    Args:
        bot: Экземпляр Telegram бота.

    Returns:
        Callable: декоратор.
    """

    def decorator(func=None, *, custom_error_msg='Произошла ошибка. Попробуйте позже.'):
        if func is None:

            def wrapper(f):
                return decorator(f, custom_error_msg=custom_error_msg)

            return wrapper

        def inner(message, *args, **kwargs):
            try:
                return func(message, *args, **kwargs)
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    'Некорректный ввод. Пожалуйста, введите число для рейтинга, например, 7.5.',
                )
            except Exception as e:
                logger.error(
                    f'Ошибка в обработчике {func.__name__}: {e}', exc_info=True
                )
                bot.send_message(message.chat.id, custom_error_msg)

        return inner

    return decorator


def register_rating_handler(bot) -> None:
    """
    Регистрирует обработчик команды /movie_by_rating.

    Args:
        bot: Экземпляр Telegram бота.
    """
    decorator = error_handler_decorator(bot)

    @bot.message_handler(commands=['movie_by_rating'])
    @decorator(custom_error_msg='Ошибка при обработке команды. Попробуйте позже.')
    def ask_rating_params(message: Message):
        logger.info(
            f'Пользователь {message.from_user.id} вызвал команду /movie_by_rating'
        )
        log_user_query(message.from_user.id, message.text, command='/movie_by_rating')
        bot.set_state(
            message.from_user.id, MovieSearchStates.waiting_for_rating, message.chat.id
        )
        bot.send_message(
            message.chat.id, 'Введите минимальный рейтинг IMDB (например, 7.5):'
        )

    @bot.message_handler(state=MovieSearchStates.waiting_for_rating)
    @decorator(custom_error_msg='Ошибка при обработке рейтинга. Попробуйте снова.')
    def process_min_imdb(message: Message):
        rating_str = message.text.strip().replace(',', '.')
        try:
            min_rating = float(rating_str)
            logger.info(f'Минимальный рейтинг для поиска: {min_rating}')
        except ValueError:
            bot.send_message(
                message.chat.id, 'Некорректный формат. Введите число, например, 7.5.'
            )
            return

        try:
            films = search_films_by_rating(min_rating)
        except Exception as e:
            logger.error(
                f'Ошибка при вызове search_films_by_rating: {e}', exc_info=True
            )
            bot.send_message(
                message.chat.id, 'Ошибка при обращении к API. Попробуйте позже.'
            )
            bot.delete_state(message.from_user.id, message.chat.id)
            return

        if films:
            log_user_query(
                message.from_user.id, message.text, command='/movie_by_rating'
            )
            parts = []
            current_part = ''
            for film in films:
                if film is None or not isinstance(film, dict):
                    continue
                film_info = format_film(film) + '\n---\n'
                if len(current_part) + len(film_info) > MAX_MESSAGE_LENGTH:
                    parts.append(current_part)
                    current_part = film_info
                else:
                    current_part += film_info
            if current_part:
                parts.append(current_part)

            for part in parts:
                bot.send_message(message.chat.id, part, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, 'По вашему запросу фильмы не найдены.')
        bot.delete_state(message.from_user.id, message.chat.id)
