import telebot
import logging
import os
from telegram.ext import Updater


class _Logger(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        logging.getLogger("requests").setLevel(logging.WARNING)


class _Bot(object):
    def __init__(self):
        self.updater = Updater(token=os.environ.get('BOT_TOKEN'))

    def startPolling(self):
        self.updater.start_polling()

    def getBot(self):
        return self.updater


class BotFacade(object):

    def __init__(self):
        self.bot = _Bot()
        self.logger = _Logger()

    def startBot(self):
        self.bot.startPolling()

    def getBot(self):
        return self.bot.getBot()
