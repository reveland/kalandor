import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberSeenRequest
from viberbot.api.viber_requests import ViberDeliveredRequest
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.picture_message import PictureMessage
from kalandor.chatbot.chatbot import ChatBot


class ViberChatBot(ChatBot):

    def __init__(self):
        name = 'Guide'
        avatar = 'https://st2.depositphotos.com/'\
            '3146979/9765/v/950/depositphotos_97658722'\
            '-stock-illustration-vector-round-icon-pile-of.jpg'
        auth_token = os.environ['VIBER_AUTH_TOKEN']
        viber_bot_config = BotConfiguration(
            name=name,
            avatar=avatar,
            auth_token=auth_token
        )
        self.viber_bot = Api(viber_bot_config)

    def get_message(self, request):
        signature = request.headers.get('X-Viber-Content-Signature')
        if not self.viber_bot.verify_signature(request.get_data(), signature):
            raise 'Invalid Signature!', signature

        viber_request = self.viber_bot.parse_request(request.get_data())

        if isinstance(viber_request, ViberMessageRequest):
            user_id = viber_request.sender.id
            text = viber_request.message.text
            return {'user_id': user_id, 'text': text}
        elif isinstance(viber_request, ViberSubscribedRequest):
            pass
        elif isinstance(viber_request, ViberSeenRequest):
            pass
        elif isinstance(viber_request, ViberDeliveredRequest):
            pass
        elif isinstance(viber_request, ViberFailedRequest):
            raise 'client failed receiving message. failure: {0}'.format(
                viber_request)
        else:
            pass

    def send_message(self, user_id, answer):
        viber_answer = []
        if 'text' in answer:
            text_message = TextMessage(text=answer['text'])
            viber_answer.append(text_message)
        if 'image' in answer:
            url_prefix = 'https://drive.google.com/uc?export=download&id='
            image_url = url_prefix + answer['image']
            picture_message = PictureMessage(media=image_url)
            viber_answer.append(picture_message)
        if 'options' in answer:
            keyboard = self.create_keyboard(answer['options'])
            keyboard_message = KeyboardMessage(
                tracking_data=None, keyboard=keyboard)
            viber_answer.append(keyboard_message)

        self.viber_bot.send_messages(user_id, viber_answer)

    def create_keyboard(self, connections):
        keyboard = {}
        keyboard['Type'] = 'keyboard'
        keyboard['Buttons'] = map(self.create_button, connections)
        return keyboard

    def create_button(self, connection):
        button = {}
        button['Columns'] = 6
        button['Rows'] = 1
        button['Text'] = '<font color="#000000"><b>' + \
            connection + '</b></font>'
        button['TextSize'] = 'large'
        button['TextHAlign'] = 'center'
        button['TextVAlign'] = 'middle'
        button['ActionType'] = 'reply'
        button['ActionBody'] = connection
        button['BgColor'] = '#b9e6f5'
        return button
