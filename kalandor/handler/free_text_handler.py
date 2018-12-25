import logging
import json
from os import environ
from kalandor.handler.handler import Handler

with open('kalandor/static/texts.json', 'r') as texts_json:
    texts = json.load(texts_json)
logger = logging.getLogger(__name__)


class FreeTextHandler(Handler):

    def __init__(self, provider):
        self.provider = provider

    def handle(self, book_name, user_id, message):
        logger.info('handle free text from %s: %s', user_id, message)
        self.provider.record_action(user_id, message)

        actions = self.provider.get_actions(user_id)
        options = self.provider.get_last_valid_page(
            book_name, message, actions)['options']

        page = {}
        page['text'] = texts[environ['LAN']]['free_text'] % message
        page['options'] = options

        if environ['DEFAULT_MESSAGE'] == 'off':
            page = {}

        return page
