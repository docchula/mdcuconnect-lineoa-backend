from django.conf import settings
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration


configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
