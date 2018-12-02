from sheet_adventure import SheetAdventure


class MessageHandler(object):

    def __init__(self):
        self.sheet_adventure = SheetAdventure('kalandor')

    def handle(self, user_id, message):
        page_id = message.split('-')[0]

        try:
            page = self.sheet_adventure.get_page(page_id)
        except Exception:
            return self.handle_free_text(user_id, message)

        page = self.check_juction(user_id, page)

        if 'options' not in page:
            actions = self.sheet_adventure.get_actions(user_id)
            page['options'] = self.get_last_options(actions, page_id)

        self.sheet_adventure.record_action(user_id, page_id)

        return page

    def check_juction(self, user_id, page):
        if 'text' not in page:
            return page
        parts = page['text'].split('$')
        if len(parts) == 4:
            if parts[1] in self.sheet_adventure.get_actions(user_id):
                page = self.handle(user_id, parts[2])
                page['text'] = parts[0] + page['text']
                return page
            else:
                page['text'] = parts[0] + parts[3]
        return page

    def handle_free_text(self, user_id, message):
        self.sheet_adventure.record_action(user_id, message)

        actions = self.sheet_adventure.get_actions(user_id)
        options = self.get_last_options(actions, message)

        page = {}
        page['text'] = '"' + message + '" - gondoltad magadban..'
        page['options'] = options

        return page

    def get_last_options(self, actions, action):
        actions = list(filter(lambda a: a != action, actions))
        if not str(actions[0]).isdigit():
            return self.get_last_options(actions[1:], actions[-1])
        page = self.sheet_adventure.get_page(actions[-1])
        if 'options' in page:
            return page['options']
        else:
            return self.get_last_options(actions[1:], actions[-1])
