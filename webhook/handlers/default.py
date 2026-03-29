from webhook.utils import build_text_messages, reply_messages
from webhook.constants import Message
from .base import handler, configuration


@handler.default()
def handle_default(event):
    messages = build_text_messages(Message.ERROR_UNKNOWN)
    reply_messages(configuration, event.reply_token, messages)
