from linebot.v3.webhooks import FollowEvent
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest
from .base import handler, configuration
from webhook.utils import build_text_messages
from webhook.constants import Message, RichMenuNameEnum
from webhook.models import RichMenu
from profiles.models import Profile


@handler.add(FollowEvent)
def handle_follow(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

    line_user_id = event.source.user_id
    line_profile = line_bot_api.get_profile(line_user_id)

    register_rich_menu = RichMenu.objects.filter(
        name=RichMenuNameEnum.REGISTER.value
    ).first()
    if register_rich_menu:
        line_bot_api.link_rich_menu_id_to_user(
            line_user_id, register_rich_menu.rich_menu_id
        )

    profile, created = Profile.objects.get_or_create(line_user_id=line_user_id)

    messages = [Message.GREETING.format(line_profile.display_name)]
    if created or profile.student_id is None:
        messages.append(Message.REGISTER_PENDING)

    messages = build_text_messages(*messages)
    line_bot_api.reply_message(
        ReplyMessageRequest(replyToken=event.reply_token, messages=messages)
    )
