import logging
import os
import requests
import json
from kalandor.chatbot.chatbot import ChatBot

logger = logging.getLogger(__name__)


class TelegramChatBot(ChatBot):

    def get_message(self, request):
        logger.debug('Telegram chatbot received request: %s',
                     request.get_json())
        if request.method == "POST":
            update = request.get_json()
            if "message" in update:
                if 'text' in update['message']:
                    message = {}
                    message['user_id'] = update['message']['chat']['id']
                    message['text'] = update['message']['text']
                    logger.info(
                        'Telegram chatbot received message: %s', message)
                    return message
                else:
                    return None
            else:
                return None
        else:
            return None

    def send_message(self, user_id, answer):
        logger.debug('Telegram chatbot send answer to %s: %s', user_id, answer)
        if 'text' in answer:
            data = {}
            data["chat_id"] = user_id
            data["text"] = answer['text']
            if 'options' in answer:
                data['reply_markup'] = self.create_markup(answer['options'])
            requests.post(self.get_url("sendMessage"), data=data)
        if 'image' in answer:
            data = {}
            data["chat_id"] = user_id
            url_prefix = 'https://drive.google.com/uc?export=download&id='
            image_url = url_prefix + answer['image']
            data["photo"] = image_url
            if 'options' in answer:
                data['reply_markup'] = self.create_markup(answer['options'])
            requests.post(self.get_url("sendPhoto"), data=data)

    def create_markup(self, options):
        reply_markup = {}
        reply_markup['keyboard'] = map(lambda o: [o], options)
        return json.dumps(reply_markup, separators=(',', ':')).replace(' ', '')

    def get_url(self, method):
        TELEGRAM_API_TOKEN = os.environ["TELEGRAM_API_TOKEN"]
        TELEGRAM_BASE_URL = 'https://api.telegram.org/bot{}/{}'
        return TELEGRAM_BASE_URL.format(TELEGRAM_API_TOKEN, method)
