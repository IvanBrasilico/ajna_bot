"""Recebe um código ISBN e consulta na base ISBN."""
import csv
import sys

import requests

from biblio.models import Livro, session

sys.path.append('.')

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from bot_token import BOTTOKEN
from app.utils import error, logger

updater = Updater(token=BOTTOKEN, use_context=True)
dispatcher = updater.dispatcher

fields = 'RowKey,Title,Colection,Subject,Authors'

ISBN_URL = 'https://isbn-search-br.search.windows.net/indexes/isbn-index/docs/search?api-version=2016-09-01'
headers = {'api-key': '100216A23C5AEE390338BBD19EA86D29'}
payload = {'searchMode': 'any', 'searchFields': 'FormattedKey,RowKey', 'queryType': 'full',
           'search': '9788542207910', 'top': 12,
           'select': fields, 'skip': 0,
           'count': True, 'facets': ['Imprint,count:1', 'Authors,count:1']}

csv_out = open('livros.csv', 'a', newline='')
writer = csv.DictWriter(csv_out, fieldnames=[*fields.split(','), 'estante'], extrasaction='ignore')


# writer.writeheader()


def start(update, context):
    text = '''Digite ou leia código de barras de um ISBN
    para consultar no site isbn-search-br
    
    Digite /estante <num> para informar o número da estante
    '''
    update.message.reply_text(text)


def set_prateleira(update, context):
    if update.message:
        args = update.message.text.split()
        if len(args) > 1:
            estante = args[1]
            context.user_data['estante'] = estante
            update.message.reply_text('setando estante {}'.format(estante))


def consulta_ISBN(update, context):
    try:
        estante = context.user_data.get('estante', '-')
        text = update.message.text.strip()
        payload['search'] = text
        logger.info('Recebeu ISBN {}'.format(text))
        r = requests.post(ISBN_URL, json=payload, headers=headers)
        try:
            livro_json = r.json()['value'][0]
        except IndexError:
            livro_json = {'RowKey': text,
                          'Title': text,
                          'Colection': '',
                          'Subject': 'ISBN não encontrado',
                          'Authors': ''}
        livro_json['estante'] = estante
        writer.writerow(livro_json)
        csv_out.flush()
        livro = Livro(livro_json)
        session.add(livro)
        session.commit()
        reply_text = livro_json['RowKey'] + ' - ' + livro_json['Title']
    except Exception as err:
        reply_text = 'ERRO:' + str(err)
        logger.error(err, exc_info=True)
    update.message.reply_text(reply_text)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('estante', set_prateleira))
dispatcher.add_handler(MessageHandler(Filters.text, consulta_ISBN))

dispatcher.add_error_handler(error)
logger.info('poll start...')
updater.start_polling()
# csv_out.close()
