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

        sheet_key = os.environ['SHEET_KEY']
        self.document = client.open_by_key(sheet_key)
        self.user_sheet = self.document.worksheet('users')
        self.book_sheet = self.document.worksheet('books')

    def get_page(self, book_name, page_id):
        book_sheet = self.document.worksheet(book_name)

        cell = book_sheet.find(page_id)
        row_index = cell.row
        row = book_sheet.row_values(row_index)

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
            row_index = self.user_sheet.find(user_id).row
            actions = self.user_sheet.cell(row_index + 1, 2).value
            updated_actions = actions + '#' + action
            self.user_sheet.update_cell(row_index + 1, 2, updated_actions)
            logger.info('action recorded for %s: %s', user_id, action)
        except gspread.CellNotFound:
            logger.info('first action of %s recorded: %s', user_id, action)
            self.user_sheet.append_row([user_id, action])

    def get_actions(self, user_id):
        row_index = self.user_sheet.find(user_id).row
        actions = self.user_sheet.cell(row_index + 1, 2).value
        actions = actions.split('#')
        logger.info('actions found for %s', user_id)
        return actions

    def get_current_book_name(self, user_id):
        try:
            row_index = self.user_sheet.find(user_id).row
            current_book_name = self.user_sheet.cell(row_index, 2).value
        except gspread.CellNotFound:
            self.user_sheet.append_row([user_id, ''])
            self.user_sheet.append_row(['#', ''])
            current_book_name = ''
        if current_book_name is '':
            logger.info('current book was not found for user: %s', user_id)
            return None
        else:
            logger.info('current book found: %s', current_book_name)
            return current_book_name

    def get_books(self):
        books = self.book_sheet.col_values(2)
        return books

    def select_book(self, user_id, book_name):
        row_index = self.user_sheet.find(user_id).row
        user_books = self.user_sheet.row_values(row_index)[2:]
        # save to existed if possible
        current_book_name = self.user_sheet.cell(row_index, 2).value
        current_book_progress = self.user_sheet.cell(
            row_index + 1, 2).value
        self.user_sheet.update_cell(
            row_index, len(user_books) + 3, current_book_name)
        self.user_sheet.update_cell(
            row_index + 1, len(user_books) + 3, current_book_progress)
        if book_name in user_books:
            col_index = user_books.index(book_name)
            actions = self.user_sheet.cell(row_index + 1, col_index + 2).value
            self.user_sheet.update_cell(row_index, 2, book_name)
            self.user_sheet.update_cell(row_index + 1, 2, actions)
            logger.info('started book selected for %s: %s', user_id, book_name)
        else:
            # load existed if there is
            self.user_sheet.update_cell(row_index, 2, book_name)
            self.user_sheet.update_cell(row_index + 1, 2, '')
            logger.info('book selected for %s: %s', user_id, book_name)

    def get_last_valid_page(self, book_name, action, actions):
        logger.info('get last valid page: %s; %s', actions, action)
        if not actions or actions[0] == '':
            # record the action
            book_row_index = self.book_sheet.find(book_name).row
            book_pages = self.book_sheet.cell(book_row_index, 3).value
            return self.get_page(book_name, book_pages.split('#')[0])
        actions = list(filter(lambda a: a != action, actions))
        if not str(actions[-1]).isdigit():
            return self.get_last_valid_page(book_name, actions.pop(), actions)
        try:
            page = self.get_page(book_name, actions[-1])
        except Exception:
            return self.get_last_valid_page(book_name, actions.pop(), actions)
        if 'options' in page:
            return page
        else:
            return self.get_last_valid_page(book_name, actions.pop(), actions)
