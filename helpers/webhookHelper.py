from helpers.webhookHandler import Webhook

def postWebhook(url, args=None):
    embed = Webhook(url, **args, footer="osu!Yozora :heart:")
    embed.post()