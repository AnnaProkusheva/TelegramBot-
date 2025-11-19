"""
Модуль для работы с API Кинопоиска.
Содержит функции для поиска фильмов по различным критериям
и логирование всех запросов.
"""

from typing import List, Dict, Any
import requests
from config_data.config import API_KINOPOISK_TOKEN
from utils.logger_config import logger


def log_request_response(response: requests.Response, *args, **kwargs) -> None:
    """
    Логирует данные HTTP-запроса и соответствующего ответа.

    Args:
        response (requests.Response): Объект ответа от requests.
        *args: Дополнительные позиционные аргументы
        **kwargs: Дополнительные именованные аргументы

    """
    request = response.request
    log_data = {
        "request_method": request.method,
        "request_url": request.url,
        "request_headers": dict(request.headers),
        "request_body": (
            request.body.decode("utf-8")
            if request.body and isinstance(request.body, bytes)
            else request.body
        ),
        "response_status": response.status_code,
        "response_headers": dict(response.headers),
        "response_text": response.text,
    }
    logger.info("API HTTP call", extra={"props": log_data})


# Создаем сессию requests с хуками для логирования
session = requests.Session()
session.hooks["response"].append(log_request_response)


def search_films_by_name(name: str) -> List[Dict[str, Any]]:
    """
    Поиск фильмов по названию с помощью API Кинопоиска.
    Args:
        name (str): Название фильма для поиска.
    Returns:
        List[Dict[str, Any]]: Список найденных фильмов (каждый фильм - словарь с данными).
    """
    headers = {"X-API-KEY": API_KINOPOISK_TOKEN}
    params = {"query": name, "limit": 10}
    response = session.get(
        "https://api.kinopoisk.dev/v1.4/movie/search", headers=headers, params=params
    )
    logger.info(
        f"Запрос поиска фильмов по названию '{name}', статус: {response.status_code}"
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("docs", [])
    else:
        logger.error(
            f"Ошибка API при поиске по названию: {response.status_code} - {response.text}"
        )
        return []


def search_films_by_genre(genre: str) -> List[Dict[str, Any]]:
    """
    Поиск фильмов по жанру.

    Args:
        genre (str): Название жанра.

    Returns:
        List[Dict[str, Any]]: Список фильмов с указанным жанром.
    """
    headers = {"X-API-KEY": API_KINOPOISK_TOKEN}
    params = {"genres.name": genre, "limit": 10}
    response = session.get(
        "https://api.kinopoisk.dev/v1.4/movie", headers=headers, params=params
    )
    logger.info(
        f"Запрос поиска фильмов по жанру '{genre}', статус: {response.status_code}"
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("docs", [])
    else:
        logger.error(
            f"Ошибка API при поиске по жанру: {response.status_code} - {response.text}"
        )
        return []


def log_request_response(response: requests.Response, *args, **kwargs) -> None:
    request = response.request
    log_data = {
        "request_method": request.method,
        "request_url": request.url,
        "request_headers": dict(request.headers),
        "request_body": (
            request.body.decode("utf-8")
            if request.body and isinstance(request.body, bytes)
            else request.body
        ),
        "response_status": response.status_code,
        "response_headers": dict(response.headers),
        "response_text": response.text,
    }
    logger.info("API HTTP call", extra={"props": log_data})


session = requests.Session()
session.hooks["response"].append(log_request_response)


def search_films_by_rating(min_rating: float, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Поиск фильмов с рейтингом IMDB не ниже заданного.
    Args:
        min_rating(float): Минимальный рейтинг.
        limit(int): Максимальное число фильмов для возврата (по умолчанию 10).
    Returns:
        List[Dict[str, Any]]: Список фильмов с рейтингом >= min_rating.
    """
    headers = {"X-API-KEY": API_KINOPOISK_TOKEN}
    params = {"rating.imdb": f"{min_rating}-10", "limit": limit}
    response = session.get(
        "https://api.kinopoisk.dev/v1.4/movie", headers=headers, params=params
    )
    logger.info(
        f"Запрос поиска фильмов с рейтингом от {min_rating}, статус: {response.status_code}"
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("docs", [])
    else:
        logger.error(
            f"Ошибка API при поиске по рейтингу: {response.status_code} - {response.text}"
        )
        return []


def search_films_by_low_budget(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Поиск фильмов с низким бюджетом (не более 5 млн или без бюджета).

    Args:
        limit (int): Максимальное количество фильмов для возврата (по умолчанию 10).

    Returns:
         List[Dict[str, Any]]: Отфильтрованный список фильмов с низким бюджетом.
    """
    headers = {"X-API-KEY": API_KINOPOISK_TOKEN}
    params = {"limit": limit * 5}  # Запрашиваем больше для локальной фильтрации
    response = requests.get(
        "https://api.kinopoisk.dev/v1.4/movie", headers=headers, params=params
    )
    if response.status_code == 200:
        films = response.json().get("docs", [])
        filtered_films = []
        for film in films:
            budget = film.get("budget", {}).get("value")
            if budget is None or budget <= 5_000_000:
                filtered_films.append(film)
            if len(filtered_films) == limit:
                break
        return filtered_films
    else:
        return []


def search_films_by_high_budget(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Поиск фильмов с высоким бюджетом (не менее 10 млн).

    Args:
        limit (int): Максимальное количество фильмов для возврата (по умолчанию 10).

    Returns:
        List[Dict[str, Any]]: Отфильтрованный список фильмов с высоким бюджетом.
    """
    headers = {"X-API-KEY": API_KINOPOISK_TOKEN}
    params = {"limit": limit * 5}
    response = requests.get(
        "https://api.kinopoisk.dev/v1.4/movie", headers=headers, params=params
    )
    if response.status_code == 200:
        films = response.json().get("docs", [])
        filtered_films = []
        for film in films:
            budget = film.get("budget", {}).get("value")
            if budget is not None and budget >= 10_000_000:
                filtered_films.append(film)
            if len(filtered_films) == limit:
                break
        return filtered_films
    else:
        return []
