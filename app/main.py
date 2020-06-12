import sys
import warnings
warnings.simplefilter('ignore')

from ficha import conv_handler
from utils import logger, error

sys.path.append('.')

from telegram.ext import Updater

from config import BOTTOKEN

updater = Updater(token=BOTTOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(conv_handler)

dispatcher.add_error_handler(error)
logger.info('poll start...')
updater.start_polling()
