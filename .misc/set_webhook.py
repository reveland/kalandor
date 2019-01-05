from pprint import pprint
import requests

bot_token = '<telegram_token>'
test_url = "https://<heroku_app_name>.herokuapp.com/{}".format(bot_token)


def get_url(method):
    return "https://api.telegram.org/bot{}/{}".format(bot_token, method)


r = requests.get(get_url("setWebhook"), data={"url": test_url})
r = requests.get(get_url("getWebhookInfo"))
pprint(r.status_code)
pprint(r.json())
