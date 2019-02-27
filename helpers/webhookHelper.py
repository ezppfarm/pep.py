from handlers.webhookHandler import Webhook

def postWebhook(url, args=None):
    embed = Webhook(url, **args, footer="osu!Yozora ❤")
    embed.post()