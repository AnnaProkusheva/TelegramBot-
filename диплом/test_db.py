"""
Скрипт для проверки подключения и количества записей в таблице SearchHistory.
"""

from database import SearchHistory

count = SearchHistory.select().count()
if count > 0:
    print(f"В таблице SearchHistory {count} записей.")
else:
    print("Таблица SearchHistory пустая.")
