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
            elif 'callback_query' in update:
                message = {}
                if 'data' in update['callback_query']:
                    message['text'] = update['callback_query']['data']
                else:
                    return None
                if 'from' in update['callback_query']:
                    user_id = update['callback_query']['from']['id']
                    message['user_id'] = user_id
                else:
                    return None
                logger.info('Telegram chatbot received callback: %s', message)
                return message
            else:
                return None
        else:
            return None

    def send_message(self, user_id, answer):
        logger.debug('Telegram chatbot send answer to %s: %s', user_id, answer)
        data = {}
        data["chat_id"] = user_id
        if 'text' in answer:
            data["text"] = answer['text']
            if 'options' in answer and 'image' not in answer:
                data['reply_markup'] = self.create_keyboard(answer['options'])
            logger.debug(self.get_url("sendMessage"), data)
            r = requests.post(self.get_url("sendMessage"), data=data)
            logger.debug("%s, %s, %s", r.status_code, r.reason, r.content)
        if 'image' in answer and not answer['image'] == '':
            if 'options' in answer:
                data['reply_markup'] = self.create_keyboard(answer['options'])
            if not os.path.isfile('./' + answer['image'] + '.png'):
                self.download_image(answer['image'])
            path = './' + answer['image'] + '.png'
            files = {'photo': open(path, 'rb')}
            data['chat_id'] = user_id
            url = self.get_url('sendPhoto')
            r = requests.post(url, files=files, data=data)
            logger.debug("%s, %s, %s", r.status_code, r.reason, r.content)

    def create_button(self, option):
        return [{'text': option.split('-')[-1], 'callback_data': option}]

    def create_keyboard(self, options):
        buttons = list(map(self.create_button, options))
        return json.dumps({'inline_keyboard': buttons})

    def get_url(self, method):
        TELEGRAM_API_TOKEN = os.environ["TELEGRAM_API_TOKEN"]
        TELEGRAM_BASE_URL = 'https://api.telegram.org/bot{}/{}'
        return TELEGRAM_BASE_URL.format(TELEGRAM_API_TOKEN, method)

    def download_image(self, img_id):
        url = 'https://drive.google.com/uc?export=download&id=' + img_id
        r = requests.get(url, allow_redirects=True)
        open(img_id + '.png', 'wb').write(r.content)
