import logging
from kalandor.handler.handler import Handler
import json

with open('kalandor/static/texts.json', 'r') as texts_json:
    texts = json.load(texts_json)
logger = logging.getLogger(__name__)


class AdventureHandler(Handler):

    def __init__(self, provider):
        self.provider = provider

    def handle(self, book_name, user_id, message):
        # this should use the user_id to get the book_name, but well..
        page_id = message.split('-')[0]

        try:
            page = self.provider.get_page(book_name, page_id)
        except Exception:
            logger.warn('page not found: %s', page_id)
            return self.handle_free_text(book_name, user_id, message)

        page = self.check_juction(user_id, page)

        if 'options' not in page:
            logger.info('options not found for %s, add previous.', page_id)
            actions = self.provider.get_actions(user_id)
            page['options'] = self.get_last_options(
                book_name, page_id, actions)

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

    def handle_free_text(self, book_name, user_id, message):
        logger.info('handle free text from %s: %s', user_id, message)
        self.provider.record_action(user_id, message)

        actions = self.provider.get_actions(user_id)
        options = self.get_last_options(book_name, message, actions)

        page = {}
        page['text'] = texts['free_text'] % message
        page['options'] = options

        return page

    def get_last_options(self, book_name, action, actions):
        logger.info('get last options: %s; %s', actions, action)
        actions = list(filter(lambda a: a != action, actions))
        if not str(actions[-1]).isdigit():
            return self.get_last_options(book_name, actions.pop(), actions)
        try:
            page = self.provider.get_page(book_name, actions[-1])
        except Exception:
            return self.get_last_options(book_name, actions.pop(), actions)
        if 'options' in page:
            return page['options']
        else:
            return self.get_last_options(book_name, actions.pop(), actions)
