import logging
import os
import io
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
            logger.debug(self.get_url("sendMessage"), data)
            r = requests.post(self.get_url("sendMessage"), data=data)
            logger.debug("%s, %s, %s", r.status_code, r.reason, r.content)
        if 'image' in answer and not answer['image'] == '':
            url_prefix = 'http://drive.google.com/uc?export=download&id='
            image_url = url_prefix + answer['image']
            with open(answer['image'] + '.png', 'wb') as f:
                f.write(requests.get(image_url).content)
            files = {'photo': open(answer['image'] + '.png', 'rb')}
            data = {'chat_id': user_id}
            if 'options' in answer:
                data['reply_markup'] = self.create_markup(answer['options'])
            logger.debug("%s, %s, %s", self.get_url("sendPhoto"), files, data)
            r = requests.post(self.get_url("sendPhoto"),
                              files=files, data=data)
            logger.debug("%s, %s, %s", r.status_code, r.reason, r.content)

    def create_markup(self, options):
        reply_markup = {}
        reply_markup['keyboard'] = map(lambda o: [o], options)
        return json.dumps(reply_markup, separators=(',', ':')).replace(' ', '')

    def get_url(self, method):
        TELEGRAM_API_TOKEN = os.environ["TELEGRAM_API_TOKEN"]
        TELEGRAM_BASE_URL = 'https://api.telegram.org/bot{}/{}'
        return TELEGRAM_BASE_URL.format(TELEGRAM_API_TOKEN, method)
