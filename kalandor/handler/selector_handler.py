import logging
import json
from os import environ
from kalandor.handler.handler import Handler

with open('kalandor/static/texts.json', 'r') as texts_json:
    texts = json.load(texts_json)
logger = logging.getLogger(__name__)


class SelectorHandler(Handler):

    def __init__(self, provider):
        self.provider = provider

    def handle(self, user_id, message):
        book = message
        books = self.provider.get_books()
        if book in books:
            start_point = self.provider.select_book(user_id, book)
            answer = {}
            answer['text'] = texts[str(environ['LAN'])]['adventure_selected']
            answer['options'] = [str(start_point) + '-Start!']
            return answer
        else:
            answer = {}
            answer['text'] = texts[environ['LAN']]['choose_adventure']
            answer['options'] = self.provider.get_books()
            return answer
