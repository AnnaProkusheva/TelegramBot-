from telebot.handler_backends import State, StatesGroup


class MovieSearchStates(StatesGroup):
    """Состояния для различных этапов поиска фильмов"""

    waiting_for_name = State()
    waiting_for_genre = State()
    waiting_for_rating = State()
    waiting_for_low_budget = State()
    waiting_for_high_budget = State()
    waiting_for_history_date = State()
