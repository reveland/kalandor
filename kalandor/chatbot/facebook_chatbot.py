import os
import json
import requests
from kalandor.chatbot.chatbot import ChatBot


class FacebookChatBot(ChatBot):

    def get_message(self, request):
        data = request.get_json()
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    if messaging_event.get("message"):
                        user_id = messaging_event["sender"]["id"]
                        if 'text' in messaging_event["message"]:
                            text = messaging_event["message"]["text"]
                        else:
                            return None
                        return {'user_id': user_id, 'text': text}
                    elif messaging_event.get("delivery"):
                        pass
                    elif messaging_event.get("optin"):
                        pass
                    elif messaging_event.get("postback"):
                        user_id = messaging_event["sender"]["id"]
                        text = messaging_event["postback"]['payload']
                        return {'user_id': user_id, 'text': text}

    def send_message(self, user_id, answer):
        if 'text' in answer:
            self.__send(user_id, {'text': answer['text']})
        if 'image' in answer:
            url_prefix = 'https://drive.google.com/uc?export=download&id='
            image_url = url_prefix + answer['image']
            self.__send(user_id, {
                'attachment': {
                    'type': 'image',
                    'payload':
                    {
                        'url': image_url,
                        'is_reusable': True
                    }
                }
            }
            )
        if 'options' in answer:
            buttons = []
            for option in answer['options']:
                show = option.split('-')[1] if '-' in option else option
                buttons.append({
                    'type': 'postback',
                    'title': show,
                    'payload': option
                })
            message = {
                'attachment':
                {
                    'type': 'template',
                    'payload':
                    {
                        'template_type': 'button',
                        'text': '-------------------------',
                        'buttons': buttons
                    }
                }
            }
            self.__send(user_id, message)

    def __send(self, user_id, message):
        params = {
            "access_token": os.environ["FACEBOOK_ACCESS_TOKEN"]
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": user_id
            },
            "message": message
        })
        requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)

    def verify(self, request):
        mode = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        verify_token = request.args.get("hub.verify_token")
        if mode == "subscribe" and challenge:
            if not verify_token == os.environ["FACEBOOK_VERIFY_TOKEN"]:
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200
