from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(
        KeyboardButton("Старт"), KeyboardButton("Стоп"), KeyboardButton("Помощь")
    )
    return keyboard
