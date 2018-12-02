from flask import Flask, request, Response

from viber_chatbot import ViberChatBot
from sheet_adventure import SheetAdventure

app = Flask(__name__)

viber_chatbot = ViberChatBot()
sheet_adventure = SheetAdventure('tenopia')


@app.route('/viber_hook', methods=['POST'])
def viber_hook():
    received_message = viber_chatbot.get_message(request)

    if received_message is not None:
        message = sheet_adventure.get_page(received_message['text'])
        viber_chatbot.send_message(received_message['user_id'], message)

    return Response(status=200)


if __name__ == '__main__':
    app.run()
