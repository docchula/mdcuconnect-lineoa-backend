from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(name="website.tasks.send_verification_email_task")
def send_verification_email_task(recipient_email, subject, content):

    try:
        from_email = settings.EMAIL_HOST_USER
        if not from_email:
            raise ValueError("EMAIL_HOST_USER is not configured in settings.")

        logger.info(f"Starting to send verification email to {recipient_email}")

        send_mail(
            subject=subject,
            message=content,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )

        logger.info(f"Verification email sent successfully to {recipient_email}")
        return f"Success: Email sent to {recipient_email}"

    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}. Error: {str(e)}")
        raise e
