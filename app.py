from flask import Flask, request, Response

from viber_chatbot import ViberChatBot
from message_handler import MessageHandler

app = Flask(__name__)

viber_chatbot = ViberChatBot()
message_handler = MessageHandler()


@app.route('/viber_hook', methods=['POST'])
def viber_hook():
    message = viber_chatbot.get_message(request)

    if message is not None:
        answer = message_handler.handle(message['user_id'], message['text'])
        viber_chatbot.send_message(message['user_id'], answer)

    return Response(status=200)


if __name__ == '__main__':
    app.run()
