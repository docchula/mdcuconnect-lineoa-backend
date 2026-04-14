from django.test import TestCase
from unittest.mock import patch, MagicMock
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent
from linebot.v3.messaging.models import UserProfileResponse
from webhook.handlers.message_events.text import handle_default_message
from webhook.constants import Message
from profiles.models import Profile
from ...utils import get_mock_event


class HandleDefaultMessageTestCase(TestCase):
    def setUp(self):
        self.line_display_name = "Top"

        self.patcher_api_client = patch(
            "webhook.handlers.message_events.text.ApiClient"
        )
        self.patcher_messaging_api = patch(
            "webhook.handlers.message_events.text.MessagingApi"
        )

        self.mock_api_client = self.patcher_api_client.start()
        self.mock_messaging_api = self.patcher_messaging_api.start()

        self.mock_line_bot_api = MagicMock()
        self.mock_line_bot_api.get_profile.return_value = UserProfileResponse(
            userId="", displayName=self.line_display_name
        )
        self.mock_messaging_api.return_value = self.mock_line_bot_api

    def tearDown(self):
        self.patcher_api_client.stop()
        self.patcher_messaging_api.stop()

    def _create_existed_user(self, line_user_id, student_id):
        Profile.objects.create(
            line_user_id=line_user_id,
            student_id=student_id,
        )

    def test_send_by_unregistered_user(self):
        """
        when an unregistered user send a message to LINE OA,
        the user should receieve a registration message
        """
        # Arrange
        event = get_mock_event(MessageEvent, TextMessageContent)

        reply_token = event.reply_token

        # Act
        handle_default_message(event)

        # Assert
        self.mock_line_bot_api.get_profile.assert_not_called()
        self.mock_line_bot_api.reply_message.assert_called_once()

        reply_message_request = self.mock_line_bot_api.reply_message.call_args.args[0]
        self.assertEqual(reply_token, reply_message_request.reply_token)
        self.assertEqual(1, len(reply_message_request.messages))
        self.assertEqual(
            Message.REGISTER_PENDING, reply_message_request.messages[0].text
        )

    def test_send_by_unverified_user(self):
        """
        when an unverified user send a message to LINE OA,
        the user should receieve a registration message
        """
        # Arrange
        event = get_mock_event(MessageEvent, TextMessageContent)

        line_user_id = event.source.user_id
        reply_token = event.reply_token

        self._create_existed_user(line_user_id, None)

        # Act
        handle_default_message(event)

        # Assert
        self.mock_line_bot_api.get_profile.assert_not_called()
        self.mock_line_bot_api.reply_message.assert_called_once()

        reply_message_request = self.mock_line_bot_api.reply_message.call_args.args[0]
        self.assertEqual(reply_token, reply_message_request.reply_token)
        self.assertEqual(1, len(reply_message_request.messages))
        self.assertEqual(
            Message.REGISTER_PENDING, reply_message_request.messages[0].text
        )

    def test_send_by_verified_user(self):
        """
        when a verified user send a message to LINE OA,
        the user should receieve a greeting message
        """
        # Arrange
        event = get_mock_event(MessageEvent, TextMessageContent)

        line_user_id = event.source.user_id
        reply_token = event.reply_token

        self._create_existed_user(line_user_id, "6422781234")

        # Act
        handle_default_message(event)

        # Assert
        self.mock_line_bot_api.get_profile.assert_called_once_with(line_user_id)
        self.mock_line_bot_api.reply_message.assert_called_once()

        reply_message_request = self.mock_line_bot_api.reply_message.call_args.args[0]
        self.assertEqual(reply_token, reply_message_request.reply_token)
        self.assertEqual(1, len(reply_message_request.messages))
        self.assertEqual(
            Message.GREETING.format(self.line_display_name),
            reply_message_request.messages[0].text,
        )
