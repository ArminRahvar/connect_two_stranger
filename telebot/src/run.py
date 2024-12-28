import emoji
from loguru import logger

from src.constants import keyboards, keys, states
from src.bot import bot
from src.db import db


class Bot:
    def __init__(self, telebot, mongodb):
        self.bot = telebot
        self.db = mongodb
        # register handler
        self.handlers()

        # run Bot
        logger.info('bot is runnig...')
        self.bot.infinity_polling()

    def handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            print("here")
            self.send_message(
             message.chat.id,
             f"hey {message.chat.first_name}",
              reply_markup=keyboards.main)

            db.users.update_one({'chat.id': message.chat.id},
                                {'$set': message.json}, upsert=True)
            self.update_state(message.chat.id, states.main)

        @self.bot.message_handler(regexp=emoji.emojize(keys.random_connect))
        def random_connect(message):
            self.send_message(
                    message.chat.id,
                    "connecting to a random stranger...",
                    reply_markup=keyboards.exit
                    )
            self.update_state(message.chat.id, states.random_connect)
            other_user = self.db.users.find_one(
                {
                    'state': states.random_connect,
                    'chat.id': {'$ne': message.chat.id}
                }
            )
            if not other_user:
                return
            # update other user state
            self.update_state(other_user["chat"]["id"], states.connected)
            self.send_message(
                other_user["chat"]["id"],
                f'Connected to {other_user["chat"]["id"]}...'
            )

            # update current user state
            self.update_state(message.chat.id, states.connected)
            self.send_message(
                message.chat.id,
                f'Connected to {other_user["chat"]["id"]}...'
            )

            # store connected users
            self.db.users.update_one(
                {'chat.id': message.chat.id},
                {'$set': {'connected_to': other_user["chat"]["id"]}}
            )
            self.db.users.update_one(
                {'chat.id': other_user["chat"]["id"]},
                {'$set': {'connected_to': message.chat.id}}
            )

            self.db.users.find_one()

        @self.bot.message_handler(regexp=emoji.emojize(keys.exit))
        def exit(message):
            self.send_message(
                    message.chat.id,
                    keys.exit,
                    reply_markup=keyboards.main
                    )
            self.update_state(message.chat.id, states.random_connect)

            # get connected to user
            other_user = self.db.users.find_one(
                {'chat.id': message.chat.id}
            )
            if not other_user.get('connected_to'):
                return

            # update connected to user state and terminate the connection
            other_chat_id = other_user['connected_to']
            self.update_state(other_chat_id, states.main)
            self.send_message(
                other_chat_id,
                keys.exit,
                reply_markup=keyboards.main
            )

            # remove connected users
            self.db.users.update_one(
                {'chat.id': message.chat.id},
                {'$set': {'connected_to': None}}
            )
            self.db.users.update_one(
                {'chat.id': other_chat_id},
                {'$set': {'connected_to': None}}
            )

        @self.bot.message_handler(func=lambda _: True)
        def echo_all(message):
            user = self.db.users.find_one(
                {'chat.id': message.chat.id}
            )

            if (not user) or\
                (user['state'] != states.connected) or\
                    (user['connected_to'] is None):
                return

            self.send_message(
                user['connected_to'],
                message.text,
            )

    def send_message(self, chat_id, text, reply_markup=None, emojize=True):
        if emojize:
            text = emoji.emojize(text)
        self.bot.send_message(chat_id, text, reply_markup=reply_markup)

    def update_state(self, chat_id, state):
        self.db.users.update_one(
            {'chat.id': chat_id},
            {'$set': {'state': state}}
            )


if __name__ == '__main__':
    logger.info('bot started')
    n_bot = Bot(telebot=bot, mongodb=db)
