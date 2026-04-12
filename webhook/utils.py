from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)


def build_text_messages(*args):
    res = []
    for text in args:
        res.append(TextMessage(text=text))
    return res


def reply_messages(configuration, reply_token, messages):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=messages)
    )
