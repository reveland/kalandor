import logging
from kalandor.handler.handler import Handler

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
            answer['text'] = 'Adventure selected, please click to continue.'
            answer['options'] = [str(start_point) + '-Start!']
            return answer
        else:
            answer = {}
            answer['text'] = 'Please choose an adventure:'
            answer['options'] = self.provider.get_books()
            return answer
