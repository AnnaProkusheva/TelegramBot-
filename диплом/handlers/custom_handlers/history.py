"""
Обработчик команды и состояния для управления историец запросов пользователя с
использованием машины состояний.
"""

from telebot import TeleBot
from telebot.types import Message
from telebot.handler_backends import State, StatesGroup
from peewee import fn
from database import User, SearchHistory
from datetime import datetime
from utils.logger_config import logger

bot = TeleBot('YOUR_BOT_TOKEN', parse_mode='HTML')


class MovieSearchStates(StatesGroup):
    """Состояния для работы с историей поиска"""

    waiting_for_history_date = State()


def log_user_query(
    user_id: int, query: str, command: str = None, film: dict = None
) -> None:
    """
    Записывает запрос пользователя и связанную информацию о фильме в историю.

    Args:
        user_id (int): ID пользователя
        query (str): Текст запроса
        command (str, optional): Команда, связанная с запросом
        film (dict, optional):  Данные о фильме для записи дополнительной
    информации.
    """
    user, _ = User.get_or_create(user_id=str(user_id))
    movie_data = {
        "movie_title": None,
        "movie_description": None,
        "movie_rating": None,
        "movie_year": None,
        "movie_genre": None,
        "movie_age_limit": None,
        "movie_poster_url": None,
    }
    if film:
        movie_data["movie_title"] = film.get("name") or film.get("alternativeName")
        movie_data["movie_description"] = film.get("description")
        rating_data = film.get("rating", {})
        rating_kp = rating_data.get("kp")
        rating_imdb = rating_data.get("imdb")
        if rating_kp and rating_kp > 0:
            movie_data["movie_rating"] = str(rating_kp)
        elif rating_imdb:
            movie_data["movie_rating"] = str(rating_imdb)
        movie_data["movie_year"] = str(film.get("year"))
        genres_list = film.get("genres", [])
        movie_data["movie_genre"] = ", ".join(
            g.get("name") for g in genres_list if g.get("name")
        )
        movie_data["movie_age_limit"] = film.get("ratingAgeLimits", {}).get("name")
        movie_data["movie_poster_url"] = film.get("poster", {}).get("url")

    SearchHistory.create(
        user=user,
        query=query,
        command=command,
        timestamp=datetime.now(),
        movie_title=movie_data["movie_title"],
        movie_description=movie_data["movie_description"],
        movie_rating=movie_data["movie_rating"],
        movie_year=movie_data["movie_year"],
        movie_genre=movie_data["movie_genre"],
        movie_age_limit=movie_data["movie_age_limit"],
        movie_poster_url=movie_data["movie_poster_url"],
    )
    logger.info(f"Запись истории: пользователь {user.user_id}, запрос '{query}'")


def format_history_entry(entry) -> str:
    """
    Форматирует запись истории для вывода пользователю.

    Args:
        entry: Объект записи SearchHistory.

    Returns:
        str: Отформатированное строковое представление записи.
    """
    date = entry.timestamp.strftime('%d.%m.%Y %H:%M:%S')
    cmd = entry.command or "неизвестная команда"
    return (
        f'Дата поиска: {date}\n'
        f'Команда: {cmd}\n'
        f'Название: {entry.movie_title or "Неизвестно"}\n'
        f'Описание: {entry.movie_description or "Отсутствует"}\n'
        f'Рейтинг: {entry.movie_rating or "Нет данных"}\n'
        f'Год: {entry.movie_year or "Неизвестно"}\n'
        f'Жанр: {entry.movie_genre or "Неизвестно"}\n'
        f'Возрастной рейтинг: {entry.movie_age_limit or "—"}\n'
        + (f'Постер: {entry.movie_poster_url}\n' if entry.movie_poster_url else '')
    )


def register_history_handler(bot: TeleBot) -> None:
    """
    Регистрирует обработчики команды /history  и состояния ожидания даты.
    Позволяет запросить и вывести историю поисков.

    Args:
        bot (TeleBot): Экземпляр бота.
    """

    @bot.message_handler(commands=['history'])
    def history_command(message: Message):
        bot.set_state(
            message.from_user.id,
            MovieSearchStates.waiting_for_history_date,
            message.chat.id,
        )
        bot.send_message(
            message.chat.id,
            "Введите дату в формате дд.мм.гггг для фильтрации истории или 'все' для всей истории:",
        )

    @bot.message_handler(state=MovieSearchStates.waiting_for_history_date)
    def process_history_date(message: Message):
        user_id = message.from_user.id
        text = message.text.strip().lower()
        user, _ = User.get_or_create(user_id=str(user_id))

        if text == 'все':
            history = (
                SearchHistory.select()
                .where(SearchHistory.user == user)
                .order_by(SearchHistory.timestamp.desc())
            )
        else:
            try:
                target_date = datetime.strptime(text, '%d.%m.%Y').date()
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "Неверный формат даты. Введите дату в формате дд.мм.гггг или 'все'. Попробуйте снова.",
                )
                return
            history = (
                SearchHistory.select()
                .where(
                    (SearchHistory.user == user)
                    & (fn.DATE(SearchHistory.timestamp) == target_date)
                )
                .order_by(SearchHistory.timestamp.desc())
            )

        if not history.exists():
            bot.send_message(message.chat.id, "По вашему запросу история пустая.")
            bot.delete_state(user_id, message.chat.id)
            return

        for entry in history.limit(10):
            text = format_history_entry(entry)
            bot.send_message(message.chat.id, text)  # Кнопки не добавляем

        bot.delete_state(user_id, message.chat.id)
