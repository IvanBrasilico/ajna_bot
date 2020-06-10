import logging
import sys

sys.path.append('.')
from datetime import datetime, timedelta

from pymongo import MongoClient

from telegram.ext import CommandHandler
from telegram.ext import Updater

from bhadrasana.models import db_session
from bhadrasana.models.ovrmanager import get_ovr_responsavel, get_ovr_container
from bhadrasana.models.rvfmanager import get_rvfs_filtro
from bhadrasana.models.virasana_manager import get_dues_container, get_detalhes_mercante

from config import BOTTOKEN

from ajna_commons.flask.conf import DATABASE, MONGODB_URI

conn = MongoClient(host=MONGODB_URI)
mongodb = conn[DATABASE]

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
    fim = datetime.now()
    inicio = fim - timedelta(days=90)
    numero = context.args[0]
    logger.info('Consultando contêiner %s' % numero)
    logger.info('get_rvfs_filtro')
    rvfs = get_rvfs_filtro(db_session, {'numerolote': numero,
                                        'datainicio': inicio,
                                        'datafim': fim})
    logger.info('get_dues_container')
    dues = get_dues_container(mongodb, numero)
    lista_numeroDUEs = [due['numero'] for due in dues]
    logger.info('get_ovr_container')
    ces, ovrs = get_ovr_container(db_session, numero, inicio, fim,
                                  lista_numeroDUEs)
    logger.info('get detalhes CE Mercante')
    infoces = get_detalhes_mercante(db_session, ces)
    result = []
    result.append('Fichas')
    result.append(' - '.join([str(ovr.id) for ovr in ovrs]))
    result.append('Verificações Físicas')
    result.append(' - '.join([str(rvf.id) for rvf in rvfs]))
    result.append('DUEs')
    result.append(' - '.join(lista_numeroDUEs))
    result.append(str(infoces))
    result = '\n'.join(result)
    context.bot.send_message(chat_id=update.effective_chat.id, text=result)


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
