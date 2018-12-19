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
                        pass

    def send_message(self, user_id, answer):
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
            "message": {
                "text": answer['text']
            }
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
        return "Hello world", 200
