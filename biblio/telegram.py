"""Interface gerenciadora da biblioteca via Telegram."""
import sys

from sqlalchemy import or_

sys.path.append('.')

from biblio.models import session, Livro

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from bot_token import BOTTOKEN
from app.utils import error, logger

updater = Updater(token=BOTTOKEN, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    text = '''Digite nome ou ISBN ou Autor para consultar
    '''
    update.message.reply_text(text)


def consulta_Livro(update, context):
    try:
        text = update.message.text.strip() + '%'
        rows = session.query(Livro).filter(
            or_(Livro.RowKey.like(text) , Livro.Title.like(text))
        ).limit(10).all()
        reply_text = '\n'.join(list(rows))
    except Exception as err:
        reply_text = 'ERRO:' + str(err)
        logger.error(err, exc_info=True)
    update.message.reply_text(reply_text)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, consulta_Livro))

dispatcher.add_error_handler(error)


if __name__ == '__main__':
    logger.info('Iniciando Telegram Biblio')
    updater.start_polling()

