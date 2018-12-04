import logging
from kalandor.provider.sheet_adventure import SheetAdventure

logger = logging.getLogger(__name__)


class MessageHandler(object):

    def __init__(self):
        self.sheet_adventure = SheetAdventure('kalandor')

    def handle(self, user_id, message):
        page_id = message.split('-')[0]

        try:
            page = self.sheet_adventure.get_page(page_id)
        except Exception:
            logger.warn('page not found: %s', page_id)
            return self.handle_free_text(user_id, message)

        page = self.check_juction(user_id, page)

        if 'options' not in page:
            logger.info('options not found for %s, add previous.', page_id)
            actions = self.sheet_adventure.get_actions(user_id)
            page['options'] = self.get_last_options(page_id, actions)

        self.sheet_adventure.record_action(user_id, page_id)

        return page

    def check_juction(self, user_id, page):
        if 'text' not in page:
            return page
        parts = page['text'].split('$')
        if len(parts) == 4:
            logger.info('juction found: go %s if %s else continue',
                        parts[2], parts[1])
            if parts[1] in self.sheet_adventure.get_actions(user_id):
                page = self.handle(user_id, parts[2])
                page['text'] = parts[0] + page['text']
                return page
            else:
                page['text'] = parts[0] + parts[3]
        return page

    def handle_free_text(self, user_id, message):
        logger.info('handle free text from %s: %s', user_id, message)
        self.sheet_adventure.record_action(user_id, message)

        actions = self.sheet_adventure.get_actions(user_id)
        options = self.get_last_options(message, actions)

        page = {}
        page['text'] = '"' + message + '" - gondoltad magadban..'
        page['options'] = options

        return page

    def get_last_options(self, action, actions):
        logger.info('get last options: %s; %s', actions, action)
        actions = list(filter(lambda a: a != action, actions))
        if not str(actions[-1]).isdigit():
            return self.get_last_options(actions.pop(), actions)
        try:
            page = self.sheet_adventure.get_page(actions[-1])
        except Exception:
            return self.get_last_options(actions.pop(), actions)
        if 'options' in page:
            return page['options']
        else:
            return self.get_last_options(actions.pop(), actions)
