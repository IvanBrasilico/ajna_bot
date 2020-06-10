import io
import logging
import sys

import requests

sys.path.append('.')
from datetime import datetime, timedelta

from telegram.ext import CommandHandler
from telegram.ext import Updater

from config import BOTTOKEN, APIURL

print(BOTTOKEN)

updater = Updater(token=BOTTOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger()


def start(update, context):
    logger.info('start')
    result = '''
    Bem vindo ao cliente Telegram do AJNA (alfa)
    Comandos disponíveis:
    /fichas <cpf> - lista fichas atribuídas para o CPF
    /conteiner <numero> - informações para o contêiner <numero>
    /scan <numero> - escaneamentos para o contêiner <numero>
    /fotos <id> - fotos de verificação para a ficha <id>
    /upload_ficha <id> <imagem> - Upload de imagem na ficha <id> 
    /upload <numero> <imagem> - Upload de imagem na ficha do contêiner <numero> (Se houver para o Usuário) 
    '''
    context.bot.send_message(chat_id=update.effective_chat.id, text=result)


def conteiner(update, context):
    fim = datetime.now()
    inicio = fim - timedelta(days=90)
    numero = context.args[0]
    logger.info('Consultando contêiner %s' % numero)
    payload = {'numerolote': numero,
               'datainicio': inicio,
               'datafim': fim}
    r = requests.post(APIURL + 'consulta_container_text', data=payload)
    context.bot.send_message(chat_id=update.effective_chat.id, text=r.text)


def conteiner2(update, context):
    fim = datetime.now()
    inicio = fim - timedelta(days=90)
    numero = context.args[0]
    logger.info('Consultando contêiner %s' % numero)
    payload = {'numerolote': numero,
               'datainicio': inicio,
               'datafim': fim}
    r = requests.post(APIURL + 'consulta_container', data=payload)
    context.bot.send_message(chat_id=update.effective_chat.id, text=r.text)


def minhas_fichas(update, context):
    cpf = context.args[0]
    logger.info(cpf)
    r = requests.get(APIURL + 'minhas_fichas_text?cpf=%s' % cpf)
    context.bot.send_message(chat_id=update.effective_chat.id, text=r.text)


def send_scan(update, context):
    numero = context.args[0]
    logger.info('Consultando contêiner %s' % numero)
    r = requests.get(APIURL + 'escaneamentos_container/%s' % numero)
    logger.info(r.text)
    imagens = r.json()
    for _id in imagens:
        r = requests.get(APIURL + 'scan/%s' % _id)
        bio = io.BytesIO(r.content)
        bio.name = '%s.jpeg' % _id
        bio.seek(0)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=bio)


def send_fotos(update, context):
    rvf_id = context.args[0]
    logger.info('Consultando rvf %s' % rvf_id)
    r = requests.get(APIURL + 'imagens_rvf/%s' % rvf_id)
    logger.info(r.text)
    imagens = r.json()
    for _id in imagens:
        r = requests.get(APIURL + 'image/%s' % _id)
        bio = io.BytesIO(r.content)
        bio.name = '%s.jpeg' % _id
        bio.seek(0)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=bio)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(CommandHandler('conteiner', conteiner))
dispatcher.add_handler(CommandHandler('conteiner2', conteiner2))
dispatcher.add_handler(CommandHandler('fichas', minhas_fichas))
dispatcher.add_handler(CommandHandler('scan', send_scan))
dispatcher.add_handler(CommandHandler('fotos', send_fotos))

updater.start_polling()
