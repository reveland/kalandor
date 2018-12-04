import os
import ast
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from kalandor.provider.adventure import Adventure

logger = logging.getLogger(__name__)


class SheetAdventure(Adventure):

    def __init__(self, name):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        creds_dict = ast.literal_eval(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope)
        client = gspread.authorize(creds)
        document = client.open(name)
        self.book_sheet = document.get_worksheet(0)
        self.user_sheet = document.get_worksheet(1)

    def get_page(self, page_id):
        cell = self.book_sheet.find(page_id)
        row_number = cell.row
        row = self.book_sheet.row_values(row_number)

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
            actions = self.user_sheet.cell(row_number, 2).value
            self.user_sheet.update_cell(row_number, 2, actions + '#' + action)
            logger.info('action recorded for %s: %s', user_id, action)
        except gspread.CellNotFound:
            logger.info('first action of %s recorded: %s', user_id, action)
            self.user_sheet.append_row([user_id, action])

    def get_actions(self, user_id):
        row_number = self.user_sheet.find(user_id).row
        actions = self.user_sheet.cell(row_number, 2).value
        actions = actions.split('#')
        logger.debug('actions found for %s: %s', user_id, actions)
        return actions
