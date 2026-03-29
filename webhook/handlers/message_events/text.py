from linebot.v3.webhooks import MessageEvent, TextMessageContent
from webhook.utils import build_text_messages, reply_messages
from ..base import handler, configuration


@handler.add(MessageEvent, TextMessageContent)
def handle_text_message(event):
    messages = build_text_messages(event.message.text)
    reply_messages(configuration, event.reply_token, messages)
