from flask import Flask, request, Response
import json
import logging.config
from kalandor.chatbot.viber_chatbot import ViberChatBot
from kalandor.handler.message_handler import MessageHandler

with open('log_config.json', 'r') as log_config_json:
    log_config_dict = json.load(log_config_json)
logging.config.dictConfig(log_config_dict)

logger = logging.getLogger(__name__)
app = Flask(__name__)
viber_chatbot = ViberChatBot()
message_handler = MessageHandler()


@app.route('/viber_hook', methods=['POST'])
def viber_hook():
    logger.debug('Viber hook receive request: %s', request)
    message = viber_chatbot.get_message(request)
    if message is not None:
        logger.info('viber message receive from %s: %s',
                    message['user_id'], message['text'])
        answer = message_handler.handle(message['user_id'], message['text'])
        logger.info('viber answer send to %s', message['user_id'])
        viber_chatbot.send_message(message['user_id'], answer)
    return Response(status=200)


if __name__ == '__main__':
    app.run()
