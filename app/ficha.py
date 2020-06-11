"""Funções para consultar Endpoints do bhadrasana2."""
import io
from datetime import datetime, timedelta

import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, Filters, MessageHandler

from config import APIURL
from utils import logger

MENU, MINHAS_FICHAS, CONSULTA_CONTEINER, SCAN, FOTOS, ABRE_FICHA,\
CONSULTA_FICHA, FICHA_ABERTA = range(8)


def minhas_fichas(update, context):
    logger.info('minhas_fichas')
    logger.info('update')
    logger.info(update)
    cpf = update.message.text
    logger.info(cpf)
    try:
        r = requests.get(APIURL + 'minhas_fichas_text?cpf=%s' % cpf, verify=False)
        if r.status_code != 200:
            text = 'Erro: %s - %s' % (r.status_code, r.text)
        else:
            text = r.text
    except Exception as err:
        text = str(err)
    update.message.reply_text(text)
    return start(update, context)


def conteiner(update, context):
    try:
        fim = datetime.now()
        inicio = fim - timedelta(days=90)
        numero = update.message.text
        logger.info('Consultando contêiner %s' % numero)
        payload = {'numerolote': numero,
                   'datainicio': inicio,
                   'datafim': fim}
        r = requests.post(APIURL + 'consulta_container_text', data=payload, verify=False)
        update.message.reply_text(r.text)
    except Exception as err:
        text = str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(text)
    return start(update, context)


def send_scan(update, context):
    numero = update.message.text
    logger.info('Consultando contêiner %s' % numero)
    try:
        r = requests.get(APIURL + 'escaneamentos_container/%s' % numero, verify=False)
        imagens = r.json()
        for _id in imagens:
            r = requests.get(APIURL + 'scan/%s' % _id, verify=False)
            bio = io.BytesIO(r.content)
            bio.name = '%s.jpeg' % _id
            bio.seek(0)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=bio)
    except Exception as err:
        text = str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(text)
    return start(update, context)


def send_fotos(update, context):
    text = update.message.text
    try:
        if str(text).isnumeric():
            logger.info('Consultando fotos da rvf %s' % text)
            r = requests.get(APIURL + 'imagens_rvf/%s' % text, verify=False)
        else:
            # TODO: Consulta imagens por contêiner
            logger.info('Consultando fotos da rvf %s' % text)
            r = requests.get(APIURL + 'imagens_rvf/%s' % text, verify=False)

        logger.info(r.text)
        imagens = r.json()
        for _id in imagens:
            r = requests.get(APIURL + 'image/%s' % _id, verify=False)
            bio = io.BytesIO(r.content)
            bio.name = '%s.jpeg' % _id
            bio.seek(0)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=bio)
    except Exception as err:
        text = str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(text)
    return start(update, context)


def mostra_ficha(update, context):
    rvf_selecionado = 0
    text = []
    text.append('Ficha Selecionada: %s' % rvf_selecionado)
    # TODO: Exibir campos da Ficha
    text.append('Envie texto para adicionar na descrição da Ficha')
    text.append('Envie fotos para inserir na Ficha')
    text.append('Digite \'sair\' para voltar ao menu inicial')
    text = '\n'.join(text)
    update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardRemove())
    return FICHA_ABERTA


def edita_descricao_ficha(update, context):
    rvf_selecionado = 0
    update.message.reply_text(
        update.message.text,
        reply_markup=ReplyKeyboardRemove())
    return FICHA_ABERTA


def upload_foto(update, context):
    logger.info('Recebendo photo')
    file_id = update.message.photo[-1]
    new_file = context.bot.get_file(file_id)
    print(new_file)
    print(dir(new_file))
    print(update.message.message_id)
    print(update.message.chat_id)
    new_file.download('teste.jpg')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Arquivo salvo')
    return FICHA_ABERTA


def start(update, context):
    initial_menu = [['Minhas Fichas', 'Consulta Conteiner', 'Imagem Escaner',
                     'Fotos verificacao', 'Abre Ficha']]
    logger.info('start')
    update.message.reply_text(
        'Cliente Telegram do AJNA (alfa) - Escolha opção',
        reply_markup=ReplyKeyboardMarkup(initial_menu, one_time_keyboard=True))
    return MENU


def cancel(update, context):
    user = update.message.from_user
    logger.info("Usuário %s saiu.", user.first_name)
    update.message.reply_text('Retornando...',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def get_fichas(update, context):
    logger.info('get_fichas')
    update.message.reply_text(
        'Digite o CPF', reply_markup=ReplyKeyboardRemove())
    return MINHAS_FICHAS


def get_conteiner(update, context):
    logger.info('get_conteiner')
    update.message.reply_text(
        'Digite o número do contêiner', reply_markup=ReplyKeyboardRemove())
    return CONSULTA_CONTEINER


def get_scan(update, context):
    logger.info('get_scan')
    update.message.reply_text(
        'Digite o número do contêiner', reply_markup=ReplyKeyboardRemove())
    return SCAN


def get_fotos(update, context):
    logger.info('get_fotos')
    update.message.reply_text(
        'Digite o id da verificação física ou o número do contêiner',
        reply_markup=ReplyKeyboardRemove())
    return FOTOS


def abre_ficha(update, context):
    logger.info('abre_ficha')
    update.message.reply_text(
        'Digite o id da verificação física',
        reply_markup=ReplyKeyboardRemove())
    return CONSULTA_FICHA


def fecha_ficha(update, context):
    logger.info('fecha_ficha')
    return start(update, context)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        MENU: [MessageHandler(Filters.regex('Minhas Fichas'), get_fichas),
               MessageHandler(Filters.regex('Imagem Escaner'), get_scan),
               MessageHandler(Filters.regex('Fotos verificacao'), get_fotos),
               MessageHandler(Filters.regex('Consulta Conteiner'), get_conteiner),
               MessageHandler(Filters.regex('Abre Ficha'), abre_ficha),
               MessageHandler(Filters.text, start)],
        MINHAS_FICHAS: [MessageHandler(Filters.text, minhas_fichas)],
        CONSULTA_CONTEINER: [MessageHandler(Filters.text, conteiner)],
        SCAN: [MessageHandler(Filters.text, send_scan)],
        FOTOS: [MessageHandler(Filters.text, send_fotos)],
        ABRE_FICHA: [MessageHandler(Filters.text, abre_ficha)],
        CONSULTA_FICHA: [MessageHandler(Filters.text, mostra_ficha)],
        FICHA_ABERTA: [MessageHandler(Filters.regex('sair'), fecha_ficha),
                                      MessageHandler(Filters.text, edita_descricao_ficha),
                                      MessageHandler(Filters.photo, upload_foto),],
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)
