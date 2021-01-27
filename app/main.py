import sys
import warnings

from ficha import start, minhas_fichas, get_scan, get_fotos, get_conteiner, get_empresa, \
    seleciona_ficha, consulta_conteiner, consulta_empresa, send_scan, send_fotos, fecha_ficha, \
    mostra_ficha, seleciona_rvf, mostra_rvf, edita_descricao_ficha, upload_foto, cancel, get_taseda, \
    inclui_descricao_rvf

warnings.simplefilter('ignore')

from telegram.ext import ConversationHandler, CommandHandler, Filters, MessageHandler

from base import MENU, MINHAS_FICHAS, CONSULTA_CONTEINER, CONSULTA_EMPRESA, \
    SCAN, FOTOS, SELECIONA_FICHA, CONSULTA_FICHA, SELECIONA_RVF, CONSULTA_RVF, \
    RVF_ABERTA, ADICIONA_DESCRICAO
from novaficha import SELECAO_CAMPOS_FICHA, TYPING, save_input, abre_novaficha, submit, \
    salva_ce, salva_due, salva_cnpj, save_input_rvf, TYPING_RVF, SELECAO_CAMPOS_RVF, \
    salva_conteiner, submit_rvf, abre_novarvf
from utils import logger, error

sys.path.append('.')

from telegram.ext import Updater

from config import BOTTOKEN

updater = Updater(token=BOTTOKEN, use_context=True)
dispatcher = updater.dispatcher

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        MENU: [MessageHandler(Filters.regex('Minhas Fichas'), minhas_fichas),
               MessageHandler(Filters.regex('Imagem Escaner'), get_scan),
               MessageHandler(Filters.regex('Fotos verificacao'), get_fotos),
               MessageHandler(Filters.regex('Consulta Conteiner'), get_conteiner),
               MessageHandler(Filters.regex('Consulta Empresa'), get_empresa),
               MessageHandler(Filters.regex('Abre Ficha.*'), seleciona_ficha),
               MessageHandler(Filters.regex('Nova Ficha'), abre_novaficha),
               MessageHandler(Filters.text, start)],
        MINHAS_FICHAS: [MessageHandler(Filters.text, minhas_fichas)],
        CONSULTA_CONTEINER: [MessageHandler(Filters.text, consulta_conteiner)],
        CONSULTA_EMPRESA: [MessageHandler(Filters.text, consulta_empresa)],
        SCAN: [MessageHandler(Filters.text, send_scan)],
        FOTOS: [MessageHandler(Filters.text, send_fotos)],
        SELECIONA_FICHA: [MessageHandler(Filters.text, seleciona_ficha)],
        CONSULTA_FICHA: [MessageHandler(Filters.regex('[S|s]air'), fecha_ficha),
                         MessageHandler(Filters.text, mostra_ficha)],
        SELECIONA_RVF: [MessageHandler(Filters.regex('[S|s]air'), fecha_ficha),
                        MessageHandler(Filters.regex('Nova RVF'), abre_novarvf),
                        MessageHandler(Filters.text, seleciona_rvf)],
        CONSULTA_RVF: [MessageHandler(Filters.regex('[S|s]air'), fecha_ficha),
                       MessageHandler(Filters.text, mostra_rvf)],
        RVF_ABERTA: [MessageHandler(Filters.regex('[S|s]air'), fecha_ficha),
                     #MessageHandler(Filters.text, edita_descricao_ficha),
                     #MessageHandler(Filters.regex('Descrição'), edita_descricao_ficha),
                     MessageHandler(Filters.regex('Descrição'), inclui_descricao_rvf),
                     MessageHandler(Filters.photo, upload_foto),
                     MessageHandler(Filters.regex('Taseda'), get_taseda)],
        ADICIONA_DESCRICAO: [MessageHandler(Filters.text, edita_descricao_ficha)],
        SELECAO_CAMPOS_FICHA: [
            MessageHandler(Filters.regex('Informar CE'), salva_ce),
            MessageHandler(Filters.regex('Informar DUE'), salva_due),
            MessageHandler(Filters.regex('Informar CNPJ'), salva_cnpj),
            MessageHandler(Filters.regex('Criar Ficha'), submit),
            MessageHandler(Filters.regex('[S|s]air'), fecha_ficha),
        ],
        TYPING: [MessageHandler(Filters.text, save_input)],
        SELECAO_CAMPOS_RVF: [
            MessageHandler(Filters.regex('Informar Contêiner'), salva_conteiner),
            MessageHandler(Filters.regex('Criar RVF'), submit_rvf),
            MessageHandler(Filters.regex('[S|s]air'), fecha_ficha),
        ],
        TYPING_RVF: [MessageHandler(Filters.text, save_input_rvf)],
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(conv_handler)

dispatcher.add_error_handler(error)
logger.info('poll start...')
updater.start_polling()
