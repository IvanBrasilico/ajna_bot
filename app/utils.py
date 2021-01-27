"""Classes comuns do Bot"""
import logging
from abc import ABC

from telegram.ext import BaseFilter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger()


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


class FilterPrivateChat(BaseFilter, ABC):
    def filter(self, message):
        return message.chat_id > 0

    def __call__(self):
        pass


private_chat = FilterPrivateChat()
