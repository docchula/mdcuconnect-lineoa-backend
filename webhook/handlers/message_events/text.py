from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest
from webhook.utils import build_text_messages
from webhook.constants import Message
from profiles.models import Profile
from ..base import handler, configuration


@handler.add(MessageEvent)
def handle_default_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

    line_user_id = event.source.user_id
    profile = Profile.objects.filter(line_user_id=line_user_id).first()
    if profile is None or profile.student_id is None:
        messages = build_text_messages(Message.REGISTER_PENDING)
        line_bot_api.reply_message(
            ReplyMessageRequest(replyToken=event.reply_token, messages=messages)
        )
        return

    line_profile = line_bot_api.get_profile(line_user_id)
    messages = build_text_messages(Message.GREETING.format(line_profile.display_name))
    line_bot_api.reply_message(
        ReplyMessageRequest(replyToken=event.reply_token, messages=messages)
    )
