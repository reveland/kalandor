import os
import ast
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from adventure import Adventure


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

        response = {}
        if len(row) > 1:
            if row[1] != '' and row[1] != ' ':
                response.update({'text': row[1]})
        if len(row) > 2:
            response.update({'options': row[2].split('#')})
        if len(row) > 3:
            response.update({'image': row[3]})

        return response

    def record_action(self, user_id, action):
        pass

    def get_actions(self, user_id):
        pass
