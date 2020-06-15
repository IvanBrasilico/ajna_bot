"""Recebe um código ISBN e consulta na base ISBN."""
import csv
import sys

import requests

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

csv_out = open('livros.csv', 'w+', newline='')
writer = csv.DictWriter(csv_out, fieldnames=fields.split(','), extrasaction='ignore')
writer.writeheader()


def start(update, context):
    update.message.reply_text('Digite ou leia código de barras de um ISBN'
                              'para consultar no site isbn-search-br')


def consulta_ISBN(update, context):
    try:
        text = update.message.text.strip()
        payload['search'] = text
        logger.info('Recebeu ISBN {}'.format(text))
        r = requests.post(ISBN_URL, json=payload, headers=headers)
        text = r.text
        livro_json = r.json()['value'][0]
        writer.writerow(livro_json)
        csv_out.flush()
        text = livro_json['RowKey'] + ' - ' + livro_json['Title']
    except Exception as err:
        text = text + '\n' + str(err)
        logger.error(err, exc_info=True)
    update.message.reply_text(text)


dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(MessageHandler(Filters.text, consulta_ISBN))

dispatcher.add_error_handler(error)
logger.info('poll start...')
updater.start_polling()
# csv_out.close()
