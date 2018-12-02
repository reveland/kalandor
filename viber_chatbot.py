import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberSeenRequest
from viberbot.api.viber_requests import ViberDeliveredRequest
from viberbot.api.messages.text_message import TextMessage

from chatbot import ChatBot

class ViberChatBot(ChatBot):

	def __init__(self):
		name = 'Guide'	
		avatar = 'https://st2.depositphotos.com/3146979/9765/v/950/depositphotos_97658722-stock-illustration-vector-round-icon-pile-of.jpg'
		auth_token = os.environ['VIBER_AUTH_TOKEN']
		viber_bot_config = BotConfiguration(
			name=name,
			avatar=avatar,
			auth_token=auth_token
		)
		self.viber_bot = Api(viber_bot_config)

	def get_message(self, request):
		if not self.viber_bot.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
			raise 'Invalid Signature!', request.headers.get('X-Viber-Content-Signature')

		viber_request = self.viber_bot.parse_request(request.get_data())

		if isinstance(viber_request, ViberMessageRequest):
			return {'user_id': viber_request.sender.id, 'text': viber_request.message.text}
		elif isinstance(viber_request, ViberSubscribedRequest):
			pass
		elif isinstance(viber_request, ViberSeenRequest):
			pass
		elif isinstance(viber_request, ViberDeliveredRequest):
			pass
		elif isinstance(viber_request, ViberFailedRequest):
			raise 'client failed receiving message. failure: {0}'.format(viber_request)
		else:
			raise 'Unexpected Message Type'

	def send_message(self, user_id, text=None):
		if text is not None:
			message = [TextMessage(text=text)]

		self.viber_bot.send_messages(user_id, message)
