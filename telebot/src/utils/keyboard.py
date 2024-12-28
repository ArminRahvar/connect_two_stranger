from telebot import types
import emoji


def create_keybord(*keys, row_width=2, resize_keyboard=True):

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keys = map(emoji.emojize, keys)
    buttuns = map(types.KeyboardButton, keys)
    markup.add(*buttuns)
    return markup
