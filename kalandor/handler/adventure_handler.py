import logging
import json
from kalandor.handler.handler import Handler
from kalandor.handler.free_text_handler import FreeTextHandler

with open('kalandor/static/texts.json', 'r') as texts_json:
    texts = json.load(texts_json)
logger = logging.getLogger(__name__)


class AdventureHandler(Handler):

    def __init__(self, provider):
        self.provider = provider
        self.free_text_handler = FreeTextHandler(provider)

    def handle(self, book_name, user_id, message):
        page_id = message.split('-')[0]

        try:
            page = self.provider.get_page(book_name, page_id)
        except Exception:
            logger.warn('page not found: %s', page_id)
            return self.free_text_handler.handle(book_name, user_id, message)

        page = self.check_juction(user_id, page)

        if 'options' not in page:
            logger.info('options not found for %s, add previous.', page_id)
            try:
                actions = self.provider.get_actions(user_id)
                page['options'] = self.provider.get_last_valid_page(
                    book_name, message, actions)['options']
            except KeyError:
                page['options'] = []

        self.provider.record_action(user_id, page_id)

        return page

    def check_juction(self, user_id, page):
        if 'text' not in page:
            return page
        parts = page['text'].split('$')
        if len(parts) == 4:
            logger.info('juction found: go %s if %s else continue',
                        parts[2], parts[1])
            if parts[1] in self.provider.get_actions(user_id):
                page = self.handle(user_id, parts[2])
                page['text'] = parts[0] + page['text']
                return page
            else:
                page['text'] = parts[0] + parts[3]
        return page
