"""
Модуль для управления пользователями в базе данных
"""

from database import User


def get_or_create_user(
    user_id: str, username: str = None, first_name: str = None
) -> User:
    """
    Получить существующего  пользователя по user_id или создать нового, если не существует.

    Args:
        user_id (str): Уникальный ID пользователя.
        username (str, optional): Имя пользователя в Telegram.
        first_name (str, optional): Имя пользователя.

    Returns:
        User: Объект пользователя из базы.
    """
    user, created = User.get_or_create(
        user_id=user_id, defaults={"username": username, "first_name": first_name}
    )
    return user
