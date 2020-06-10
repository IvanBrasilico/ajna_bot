import logging
import sys
sys.path.append('.')
from telegram.ext import CommandHandler
from telegram.ext import Updater

from bhadrasana.models import db_session
from bhadrasana.models.ovrmanager import get_ovr_responsavel
from config import BOTTOKEN

print(BOTTOKEN)

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


def minhas_fichas(update, context):
    cpf = context.args[0]
    logger.info(cpf)
    ovrs = get_ovr_responsavel(db_session, cpf)
    logger.info(len(ovrs))
    if len(ovrs) == 0:
        result = 'Sem Fichas atribuídas para o Usuário {}'.format(cpf)
    else:
        result = '\n'.join([str(ovr.id) + ' - ' + ovr.numeroCEmercante for ovr in ovrs])
    context.bot.send_message(chat_id=update.effective_chat.id, text=result)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
caps_handler = CommandHandler('container', container)
dispatcher.add_handler(caps_handler)
caps_handler = CommandHandler('fichas', minhas_fichas)
dispatcher.add_handler(caps_handler)

updater.start_polling()
