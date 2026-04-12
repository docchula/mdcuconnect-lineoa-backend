from linebot.v3.webhooks import FollowEvent
from linebot.v3.messaging import ApiClient, MessagingApi
from .base import handler, configuration
from webhook.utils import build_text_messages, reply_messages
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

    Profile.objects.get_or_create(line_user_id=line_user_id)

    messages = build_text_messages(
        Message.GREETING.format(line_profile.display_name), Message.REGISTER_PENDING
    )
    reply_messages(configuration, event.reply_token, messages)
