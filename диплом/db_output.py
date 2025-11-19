"""
Утилита для вывода содержимого таблицы SearchHistory из базы данных в консоль.
"""
from database import SearchHistory


def print_search_history() -> None:
    """
    Выводит все записи из таблицы SearchHistory в удобочитаемом виде.
    Отсутствие записей выводит соответствующее сообщение.
    """
    entries = SearchHistory.select()
    if entries.count() == 0:
        print("Таблица SearchHistory пуста.")
    else:
        for entry in entries:
            print(f"ID: {entry.id}")
            print(f"Пользователь: {entry.user.user_id}")
            print(f"Запрос: {entry.query}")
            print(f"Команда: {entry.command}")
            print(f"Время: {entry.timestamp}")
            print(f"Название фильма: {entry.movie_title}")
            print(f"Описание: {entry.movie_description}")
            print(f"Рейтинг: {entry.movie_rating}")
            print(f"Год: {entry.movie_year}")
            print(f"Жанр: {entry.movie_genre}")
            print(f"Возрастной рейтинг: {entry.movie_age_limit}")
            print(f"Постер URL: {entry.movie_poster_url}")
            print("------")


#Вызов функции печати истории при запуске модуля
print_search_history()
