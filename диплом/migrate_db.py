"""
Скрипт миграции базы данных для добавления новых колонок в существующие таблицы.
Использует playhouse.migrate для миграций SQLite с проверкой наличия колонок.
Просматривает таблицы searchhistory и favoritemovie, добавляет поля, если их еще нет.
"""

from playhouse.migrate import SqliteMigrator, migrate
from peewee import CharField, TextField
from database import db


def column_exists(table_name: str, column_name: str) -> bool:
    """
    Проверяет, существует ли колонка в таблице базы данных.

    Args:
        table_name (str): Имя таблицы
        column_name (str): Имя колонки для проверки.

    Returns:
         bool: True, если колонка существует, иначе False.
    """
    query = f"PRAGMA table_info({table_name})"
    cursor = db.execute_sql(query)
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def migrate_db() -> None:
    """
    Выполняет миграции базы данных,
    добавляет недостающие колонки в таблицы searchhistory
    """
    migrator = SqliteMigrator(db)

    with db:
        # Миграции для таблицы searchhistory
        if not column_exists('searchhistory', 'movie_title'):
            migrate(
                migrator.add_column(
                    'searchhistory', 'movie_title', CharField(null=True)
                )
            )
        if not column_exists('searchhistory', 'movie_description'):
            migrate(
                migrator.add_column(
                    'searchhistory', 'movie_description', TextField(null=True)
                )
            )
        if not column_exists('searchhistory', 'movie_rating'):
            migrate(
                migrator.add_column(
                    'searchhistory', 'movie_rating', CharField(null=True)
                )
            )
        if not column_exists('searchhistory', 'movie_year'):
            migrate(
                migrator.add_column('searchhistory', 'movie_year', CharField(null=True))
            )
        if not column_exists('searchhistory', 'movie_genre'):
            migrate(
                migrator.add_column(
                    'searchhistory', 'movie_genre', CharField(null=True)
                )
            )
        if not column_exists('searchhistory', 'movie_age_limit'):
            migrate(
                migrator.add_column(
                    'searchhistory', 'movie_age_limit', CharField(null=True)
                )
            )
        if not column_exists('searchhistory', 'movie_poster_url'):
            migrate(
                migrator.add_column(
                    'searchhistory', 'movie_poster_url', CharField(null=True)
                )
            )

        # Миграции для таблицы favoritemovie
        if not column_exists('favoritemovie', 'description'):
            migrate(
                migrator.add_column(
                    'favoritemovie', 'description', TextField(null=True)
                )
            )
        if not column_exists('favoritemovie', 'rating'):
            migrate(
                migrator.add_column('favoritemovie', 'rating', CharField(null=True))
            )
        if not column_exists('favoritemovie', 'movie_year'):
            migrate(
                migrator.add_column('favoritemovie', 'movie_year', CharField(null=True))
            )
        if not column_exists('favoritemovie', 'movie_genre'):
            migrate(
                migrator.add_column(
                    'favoritemovie', 'movie_genre', CharField(null=True)
                )
            )
        if not column_exists('favoritemovie', 'movie_age_limit'):
            migrate(
                migrator.add_column(
                    'favoritemovie', 'movie_age_limit', CharField(null=True)
                )
            )
        if not column_exists('favoritemovie', 'movie_poster_url'):
            migrate(
                migrator.add_column(
                    'favoritemovie', 'movie_poster_url', CharField(null=True)
                )
            )

    print("Миграция базы данных выполнена успешно.")


if __name__ == "__main__":
    migrate_db()
