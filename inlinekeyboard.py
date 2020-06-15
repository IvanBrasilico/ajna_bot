import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

from bot_token import BOTTOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

INFORMA_CE = 0
INFORMA_DUE = 1
INFORMA_CNPJ = 2
SELECAO_CAMPOS_FICHA = 100
TYPING = 101
SUBMIT = 102
END = 999

campos = {INFORMA_CE: 'CE', INFORMA_DUE: 'DUE', INFORMA_CNPJ: 'CNPJ'}


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    buttons = [
        [InlineKeyboardButton(text='Informar CE', callback_data=str(INFORMA_CE))],
        [InlineKeyboardButton(text='Informar DI', callback_data=str(INFORMA_DUE))],
        [InlineKeyboardButton(text='Informar CNPJ Fiscalizado',
                              callback_data=str(INFORMA_CNPJ))],
        [InlineKeyboardButton(text='Criar Ficha', callback_data=str(SUBMIT))]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text='Informe alguns campos, depois confirme criação',
                              reply_markup=keyboard)
    return SELECAO_CAMPOS_FICHA


def save_callback(update, context):
    logger.info('save_callback')
    print(int(update.callback_query.data), SUBMIT)
    if int(update.callback_query.data) == SUBMIT:
        logger.info('calling_submit')
        submit(update, context)
    context.user_data['callback'] = update.callback_query.data
    return TYPING


def save_input(update, context):
    """Save input for feature and return to feature selection."""
    logger.info('save_input')
    try:
        ud = context.user_data
        campo = campos[int(ud['callback'])]
        text = update.message.text
        ud[campo] = text
        print('UD: ', ud)
        update.message.reply_text('{} atualizado para {}'.format(campo, text))
    except Exception as err:
        logger.error(err, exc_info=True)
        update.message.reply_text(str(err))
    return SELECAO_CAMPOS_FICHA


def submit(update, context):
    ud = context.user_data
    print(ud)
    return SELECAO_CAMPOS_FICHA


def stop(update, context):
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')
    return END


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()
    text = 'See you around!'
    update.callback_query.edit_message_text(text=text)
    return END


selection_handlers = [
    CallbackQueryHandler(save_callback, pattern='^{}$'.format(INFORMA_CE)),
    CallbackQueryHandler(save_callback, pattern='^{}$'.format(INFORMA_DUE)),
    CallbackQueryHandler(save_callback, pattern='^{}$'.format(INFORMA_CNPJ)),
    CallbackQueryHandler(save_callback, pattern='^{}$'.format(SUBMIT)),
    CallbackQueryHandler(end, pattern='^{}$'.format(END)),
]
nova_ficha_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        SELECAO_CAMPOS_FICHA: selection_handlers,
        TYPING: [MessageHandler(Filters.text, save_input)],
        END: [MessageHandler(Filters.text, end)],
    },
    fallbacks=[CommandHandler('stop', stop),
               CallbackQueryHandler(end, pattern='^{}$'.format(END)),
               ],
)


