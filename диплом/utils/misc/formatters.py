"""
Форматирование текстовых данных для вывода информации о фильмах.
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_favorite_inline_keyboard(
    movie_id: str, is_favorite: bool
) -> InlineKeyboardMarkup:
    """
    Возвращает inline-клавиатуру с кнопками добавить/удалить из избранного.
    Args:
        movie_id (str): ID фильма
        is_favorite (bool): Статус избранного.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    if is_favorite:
        keyboard.add(
            InlineKeyboardButton(
                text="Удалить из избранного", callback_data=f"remove_fav:{movie_id}"
            )
        )
    else:
        keyboard.add(
            InlineKeyboardButton(
                text="Добавить в избранное", callback_data=f"add_fav:{movie_id}"
            )
        )
    return keyboard


def format_genres(film):
    genres_list = film.get("genres", [])
    genres_names = [genre.get("name", "") for genre in genres_list]
    return ", ".join(genres_names) if genres_names else "Неизвестно"


def format_film_info(film: dict) -> str:
    """
    Форматирует информацию о фильме для вывода.
    Args:
        film (dict): Информация о фильме.

    Returns:
         str: Отформатированная строка с данными фильма.
    """
    name = film.get("name") or film.get("alternativeName") or "Название неизвестно"
    description = film.get("description") or "Нет описания"
    year = film.get("year") or "неизвестно"
    rating_data = film.get("rating", {})
    rating_kp = rating_data.get("kp")
    rating_imdb = rating_data.get("imdb")
    if rating_kp and rating_kp > 0:
        rating = rating_kp
    elif rating_imdb:
        rating = rating_imdb
    else:
        rating = "Нет данных"

    genres = format_genres(film)
    age_limit = film.get("ratingAgeLimits", {}).get("name", "---")
    poster_url = film.get("poster", {}).get("url")

    info = (
        f"Название: {name}\n"
        f"Описание: {description}\n"
        f"Рейтинг: {rating}\n"
        f"Год: {year}\n"
        f"Жанр: {genres}\n"
        f"Возрастной рейтинг: {age_limit}\n"
    )
    if poster_url:
        info += f"Постер: {poster_url}\n"
    return info


def format_films_list(films: list) -> str:
    """
    Форматирует список фильмов в текст для вывода.
    Args:
        films(list): Список фильмов

    Returns:
        str: Отформатированный текст с перечнем фильмов.
    """
    return "\n---\n".join(format_film_info(film) for film in films)
