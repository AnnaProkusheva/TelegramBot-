"""
Обработчик поиска фильмов по названию с использованием машины состояний и
обработкой ошибок.
"""

from telebot import TeleBot
from telebot.types import Message
from api.kinopoisk_api import search_films_by_name
from .history import log_user_query
from states import MovieSearchStates
from utils.logger_config import logger
from utils.misc.formatters import get_favorite_inline_keyboard
from database import User, FavoriteMovie


def format_genres(film: dict) -> str:
    """
    Форматирует список жанров фильма в строку через запятую.

    Args:
        film (dict): Информация о фильме.

    Returns:
         str: Строка с перечисленными жанрами.
    """
    genres_list = film.get('genres', [])
    genres_names = [genre.get('name', '') for genre in genres_list]
    return ', '.join(genres_names)


def format_film_info(film: dict) -> str:
    """
    Форматирует подробную информацию о фильме для вывода.

    Args:
        film (dict):  Информация о фильме.

    Returns:
         str: Отформатированная строка с деталями фильма.
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

    genres = format_genres(film)
    age_limit = film.get('ratingAgeLimits', {}).get('name', '—')
    poster_url = film.get('poster', {}).get('url')

    info = f'Название: {name}\n'
    info += f'Описание: {description}\n'
    info += f'Рейтинг: {rating}\n'
    info += f'Год: {year}\n'
    info += f'Жанр: {genres}\n'
    info += f'Возрастной рейтинг: {age_limit}\n'
    if poster_url:
        info += f'Постер: {poster_url}\n'
    return info


def send_film_with_fav_buttons(
    bot: TeleBot, chat_id: int, user_id: int, film: dict
) -> None:
    """
    Отправляет подробную информацию о фильме с кнопкой добавления/удаления из избранного.

    Args:
        bot (TeleBot): Экземпляр Telegram бота.
        chat_id (int):ID чата для отправки сообщения.
        user_id (int): ID пользователя.
        film (dict): Данные фильма
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


def error_handler_decorator(bot: TeleBot):
    """
    Декоратор для обработки ошибок в обработчиках сообщений.

    Args:
        bot (TeleBot): Экземпляр Telegram бота.

    Returns:
        Callable: Декоратор функции.
    """

    def decorator(func=None, *, custom_error_msg='Произошла ошибка. Попробуйте позже.'):
        if func is None:

            def wrapper(f):
                return decorator(f, custom_error_msg=custom_error_msg)

            return wrapper

        def inner(message, *args, **kwargs):
            try:
                input_text = message.text.strip()
                logger.info(
                    f'Проверка ввода названия фильма: "{input_text}" от пользователя {message.from_user.id}'
                )
                if not input_text:
                    bot.send_message(
                        message.chat.id, 'Пожалуйста, введите название фильма.'
                    )
                    return
                if input_text.isdigit():
                    bot.send_message(
                        message.chat.id,
                        'Название не может состоять только из цифр. Попробуйте снова.',
                    )
                    return
                return func(message, *args, **kwargs)
            except Exception as e:
                logger.error(
                    f'Ошибка в обработчике {func.__name__}: {e}', exc_info=True
                )
                bot.send_message(message.chat.id, custom_error_msg)

        return inner

    return decorator


def register_name_search(bot: TeleBot) -> None:
    """
    Регистрирует обработчики команды /movie_search и состояния ожидания названия
    фильма.

    Args:
        bot (TeleBot): Экземпляр Telegram бота.
    """

    decorator = error_handler_decorator(bot)

    @bot.message_handler(commands=['movie_search'])
    @decorator(
        custom_error_msg='Ошибка при обработке команды поиска. Попробуйте позже.'
    )
    def ask_movie_name(message: Message):
        logger.info(f'Пользователь {message.from_user.id} вызвал команду /movie_search')
        log_user_query(message.from_user.id, message.text, command='/movie_search')
        bot.set_state(
            message.from_user.id, MovieSearchStates.waiting_for_name, message.chat.id
        )
        bot.send_message(message.chat.id, 'Введите название фильма:')

    @bot.message_handler(state=MovieSearchStates.waiting_for_name)
    @decorator(custom_error_msg='Ошибка при поиске фильма. Попробуйте еще раз.')
    def process_movie_name_step(message: Message):
        movie_name = message.text.strip()
        logger.info(f'Ищем фильмы по названию: {movie_name}')
        films = []
        try:
            films = search_films_by_name(movie_name)
        except Exception as e:
            logger.error(f'Ошибка при вызове search_films_by_name: {e}', exc_info=True)
            bot.send_message(
                message.chat.id, 'Ошибка при обращении к API. Попробуйте позже.'
            )
            bot.delete_state(message.from_user.id, message.chat.id)
            return

        if films:
            # Передаём фильм в log_user_query для сохранения полного описания
            log_user_query(
                message.from_user.id, movie_name, command='/movie_search', film=films[0]
            )
            reply = f'Результаты поиска по названию "{movie_name}":\n\n'
            for film in films[:1]:
                reply += format_film_info(film) + '\n---\n'
            send_film_with_fav_buttons(
                bot, message.chat.id, message.from_user.id, films[0]
            )
            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            bot.send_message(
                message.chat.id,
                'Фильмы с таким названием не найдены. Попробуйте другой запрос.',
            )
            # Состояние не удаляем, чтобы дать возможность повторить ввод
