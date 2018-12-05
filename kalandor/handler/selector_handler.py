import logging
from kalandor.handler.handler import Handler

logger = logging.getLogger(__name__)


class SelectorHandler(Handler):

    def __init__(self, provider):
        self.provider = provider

    def handle(self, user_id, message):
        message = {}
        message['text'] = 'Adventure selection is not supported yet.'
        return message
