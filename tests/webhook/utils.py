from linebot.v3.webhooks.models import (
    MessageEvent,
    TextMessageContent,
    FollowEvent,
    FollowDetail,
)
from linebot.v3.webhooks.models.user_source import UserSource
from linebot.v3.webhooks.models.delivery_context import DeliveryContext


MOCK_FOLLOW_EVENT = FollowEvent(
    type="follow",
    source=UserSource(type="user", userId="U8189cf6745fc0d808977bdb0b9f22995"),
    timestamp=1625665242211,
    mode="active",
    webhookEventId="01FZ74A0TDDPYRVKNK77XKC3ZR",
    deliveryContext=DeliveryContext(isRedelivery=False),
    replyToken="7840b71058e24a5d91f9b5726c7512c9",
    follow=FollowDetail(isUnblocked=False),
)


MOCK_TEXT_MESSAGE_EVENT = MessageEvent(
    type="message",
    source=UserSource(type="user", userId="U8189cf6745fc0d808977bdb0b9f22995"),
    timestamp=1625665242211,
    mode="active",
    webhookEventId="01FZ74A0TDDPYRVKNK77XKC3ZR",
    deliveryContext=DeliveryContext(isRedelivery=False),
    replyToken="7840b71058e24a5d91f9b5726c7512c9",
    message=TextMessageContent(
        id="354718705033693861",
        type="text",
        text="Hello World",
        quoteToken="yHAz4Ua2wx730yhdy232",
    ),
)


def get_mock_event(event, type=None):
    if event is MessageEvent:
        if type is TextMessageContent:
            return MOCK_TEXT_MESSAGE_EVENT

    if event is FollowEvent:
        return MOCK_FOLLOW_EVENT

    return None
