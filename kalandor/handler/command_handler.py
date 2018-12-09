import logging
import json
from os import environ
from kalandor.handler.handler import Handler

with open('kalandor/static/texts.json', 'r') as texts_json:
    texts = json.load(texts_json)
logger = logging.getLogger(__name__)


class CommandHandler(Handler):

    def __init__(self, provider):
        self.provider = provider

    def handle(self, user_id, message):
        command = message[1:]

        if command == 'select_book':
            # take away book (store the progress)
            self.provider.select_book(user_id, '')
            answer = {}
            answer['text'] = texts[environ['LAN']]['choose_adventure']
            answer['options'] = self.provider.get_books()
            return answer
        elif command == 'continue':
            book_name = self.provider.get_current_book_name(user_id)
            actions = self.provider.get_actions(user_id)
            return self.get_last_valid_page(book_name, actions[-1], actions)
        else:
            answer = {}
            answer['text'] = texts[environ['LAN']]['unknown_command'] % command
            answer['options'] = {'/continue'}
            return answer

    def get_last_valid_page(self, book_name, action, actions): # code duplication
        logger.info('get last valid page: %s; %s', actions, action)
        actions = list(filter(lambda a: a != action, actions))
        if not str(actions[-1]).isdigit():
            return self.get_last_options(book_name, actions.pop(), actions)
        try:
            page = self.provider.get_page(book_name, actions[-1])
        except Exception:
            return self.get_last_options(book_name, actions.pop(), actions)
        if 'options' in page:
            return page
        else:
            return self.get_last_options(book_name, actions.pop(), actions)
