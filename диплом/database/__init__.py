"""
Инициализация базы данных с использованием peewee ORM.
Определены модели пользователя, истории поиска и избранного.
"""

from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    TextField,
    DateTimeField,
    ForeignKeyField,
)
import datetime

# Инициализация базы данных SQLite для проекта
db = SqliteDatabase("Movies_bot.db")


class BaseModel(Model):
    """Базовый класс модели, связывающий с базой данных"""

    class Meta:
        database = db


class User(BaseModel):
    """Модель пользователя Telegram"""

    user_id = CharField(unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)


class SearchHistory(BaseModel):
    """Модель записи истории запросов пользователя"""

    user = ForeignKeyField(User, backref="searches", on_delete="CASCADE")
    query = CharField()
    command = CharField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    movie_title = CharField(null=True)
    movie_description = TextField(null=True)
    movie_rating = CharField(null=True)
    movie_year = CharField(null=True)
    movie_genre = CharField(null=True)
    movie_age_limit = CharField(null=True)
    movie_poster_url = CharField(null=True)


class FavoriteMovie(BaseModel):
    """Модель избранного фильма пользователя"""

    user = ForeignKeyField(User, backref="favorites", on_delete="CASCADE")
    movie_id = CharField()
    title = CharField()
    description = TextField(null=True)
    rating = CharField(null=True)
    movie_year = CharField(null=True)
    movie_genre = CharField(null=True)
    movie_age_limit = CharField(null=True)
    movie_poster_url = CharField(null=True)


def initialize_db():
    """
    Инициализирует подключение к базе данных и создает таблицы.
    Вызывать при старте приложения.
    """
    db.connect()
    db.create_tables([User, SearchHistory, FavoriteMovie], safe=True)
    db.close()
