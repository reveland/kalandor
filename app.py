from flask import Flask, request, Response

from viber_chatbot import ViberChatBot

app = Flask(__name__)

viber_chatbot = ViberChatBot()

@app.route("/")
def hello():
	return 'hello'

@app.route('/viber_hook', methods=['POST'])
def viber_hook():
	
	message = viber_chatbot.get_message(request)
	
	if message is not None:
		viber_chatbot.send_message(message['user_id'], message['text'])
	
	return Response(status=200)

if __name__ == '__main__':
	app.run()
