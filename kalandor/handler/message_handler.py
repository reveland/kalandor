import logging
from kalandor.provider.sheet_provider import SheetProvider
from kalandor.handler.handler import Handler
from kalandor.handler.selector_handler import SelectorHandler
from kalandor.handler.adventure_handler import AdventureHandler

logger = logging.getLogger(__name__)


class MessageHandler(Handler):

    def __init__(self):
        self.sheet_provider = SheetProvider()
        self.adventure_selector_handler = SelectorHandler(self.sheet_provider)
        self.adventure_handler = AdventureHandler(self.sheet_provider)

    def handle(self, user_id, message):
        book_name = self.sheet_provider.get_current_book_name(user_id)
        if book_name is None:
            return self.adventure_selector_handler.handle(user_id, message)
        else:
            return self.adventure_handler.handle(book_name, user_id, message)
