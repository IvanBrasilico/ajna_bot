import logging

from telegram.ext import CommandHandler
from telegram.ext import Updater
from config import BOTTOKEN

updater = Updater(token=BOTTOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger()


def start(update, context):
    logger.info('start')
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def container(update, context):
    numero = context.args[0]
    print(context.args, type(context.args))
    logger.info(numero)
    context.bot.send_message(chat_id=update.effective_chat.id, text=numero)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
caps_handler = CommandHandler('container', container)
dispatcher.add_handler(caps_handler)

updater.start_polling()
