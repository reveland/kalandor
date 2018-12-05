import os
import ast
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from kalandor.provider.provider import Provider

logger = logging.getLogger(__name__)


class SheetProvider(Provider):

    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        creds_dict = ast.literal_eval(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope)
        client = gspread.authorize(creds)

        sheet_key = '1hzIsPhduZ_AIxk3KWZaLOIl-JIqbTDjx9s0jMpR2WKU'
        self.document = client.open_by_key(sheet_key)
        self.user_sheet = self.document.worksheet('users')

    def get_page(self, book_name, page_id):
        book_sheet = self.document.worksheet(book_name)

        cell = book_sheet.find(page_id)
        row_number = cell.row
        row = book_sheet.row_values(row_number)

        page = {}
        if len(row) > 1:
            if row[1] != '':
                page.update({'text': row[1]})
        if len(row) > 2:
            if row[2] != '':
                page.update({'options': row[2].split('#')})
        if len(row) > 3:
            page.update({'image': row[3]})
        logger.debug('page found: %s', page)
        return page

    def record_action(self, user_id, action):
        try:
            row_number = self.user_sheet.find(user_id).row
            actions = self.user_sheet.cell(row_number + 1, 2).value
            updated_actions = actions + '#' + action
            self.user_sheet.update_cell(row_number + 1, 2, updated_actions)
            logger.info('action recorded for %s: %s', user_id, action)
        except gspread.CellNotFound:
            logger.info('first action of %s recorded: %s', user_id, action)
            self.user_sheet.append_row([user_id, action])

    def get_actions(self, user_id):
        row_number = self.user_sheet.find(user_id).row
        actions = self.user_sheet.cell(row_number + 1, 2).value
        actions = actions.split('#')
        logger.info('actions found for %s', user_id)
        return actions

    def get_current_book_name(self, user_id):
        row_number = self.user_sheet.find(user_id).row
        current_book_name = self.user_sheet.cell(row_number, 2).value
        if current_book_name is '':
            logger.info('current book was not found for user: %s', user_id)
            return None
        else:
            logger.info('current book found: %s', current_book_name)
            return current_book_name
