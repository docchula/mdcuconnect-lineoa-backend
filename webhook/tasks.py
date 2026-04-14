from celery import shared_task
from linebot.v3.exceptions import InvalidSignatureError
from .handlers import handler
import logging


logger = logging.getLogger(__name__)


@shared_task
def handle_webhook(body, signature):
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("invalid signature")
    except Exception as e:
        logger.exception(f"unexpected error - {e}")
