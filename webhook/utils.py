from linebot.v3.messaging import TextMessage


def build_text_messages(*args):
    res = []
    for text in args:
        res.append(TextMessage(text=text))
    return res
