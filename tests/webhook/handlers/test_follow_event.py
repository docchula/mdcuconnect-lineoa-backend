from django.test import TestCase
from unittest.mock import patch, MagicMock
from linebot.v3.webhooks.models import FollowEvent
from linebot.v3.messaging.models import UserProfileResponse
from webhook.handlers.follow_event import handle_follow
from webhook.models import RichMenu
from webhook.constants import RichMenuNameEnum, Message
from profiles.models import Profile
from ..utils import get_mock_event


class HandleFollowTestCase(TestCase):
    def setUp(self):
        self.line_display_name = "Top"

        self.patcher_api_client = patch("webhook.handlers.follow_event.ApiClient")
        self.patcher_messaging_api = patch("webhook.handlers.follow_event.MessagingApi")

        self.mock_api_client = self.patcher_api_client.start()
        self.mock_messaging_api = self.patcher_messaging_api.start()

        self.mock_line_bot_api = MagicMock()
        self.mock_line_bot_api.get_profile.return_value = UserProfileResponse(
            userId="", displayName=self.line_display_name
        )
        self.mock_line_bot_api.link_rich_menu_id_to_user.return_value = None
        self.mock_messaging_api.return_value = self.mock_line_bot_api

    def tearDown(self):
        self.patcher_api_client.stop()
        self.patcher_messaging_api.stop()

    def _create_register_rich_menu(self):
        mock_rich_menu_id = "richmenu-de7bcd264c0b50ca52b4e6e7a7ac4329"
        RichMenu.objects.create(
            name=RichMenuNameEnum.REGISTER.value,
            rich_menu_id=mock_rich_menu_id,
        )

        return mock_rich_menu_id

    def _create_existed_user(self, line_user_id, student_id):
        Profile.objects.create(
            line_user_id=line_user_id,
            student_id=student_id,
        )

    def test_new_user(self):
        """
        when a new user adds the LINE OA,
        the user should be linked to the rich menu and receive a registration message
        """
        # Arrange
        rich_menu_id = self._create_register_rich_menu()
        event = get_mock_event(FollowEvent)

        line_user_id = event.source.user_id
        reply_token = event.reply_token

        # Act
        handle_follow(event)

        # Assert
        self.mock_line_bot_api.get_profile.assert_called_once_with(line_user_id)
        self.mock_line_bot_api.link_rich_menu_id_to_user.assert_called_once_with(
            line_user_id, rich_menu_id
        )
        self.mock_line_bot_api.reply_message.assert_called_once()

        reply_message_request = self.mock_line_bot_api.reply_message.call_args.args[0]
        self.assertEqual(reply_token, reply_message_request.reply_token)
        self.assertEqual(2, len(reply_message_request.messages))
        self.assertEqual(
            Message.GREETING.format(self.line_display_name),
            reply_message_request.messages[0].text,
        )
        self.assertEqual(
            Message.REGISTER_PENDING, reply_message_request.messages[1].text
        )

    def test_register_rich_menu_does_not_exists(self):
        """
        when a register rich menu does not exists,
        the user should not be linked to rich menu
        """
        # Arrange
        event = get_mock_event(FollowEvent)

        # Act
        handle_follow(event)

        # Assert
        self.mock_line_bot_api.link_rich_menu_id_to_user.assert_not_called()

    def test_existed_user_with_veification(self):
        """
        when a user is already added LINE OA and completed verification,
        then the user should not receive a registration message
        """
        # Arrange
        event = get_mock_event(FollowEvent)

        line_user_id = event.source.user_id
        reply_token = event.reply_token

        self._create_existed_user(line_user_id, "6422781234")

        # Act
        handle_follow(event)

        # Assert
        self.mock_line_bot_api.reply_message.assert_called_once()

        reply_message_request = self.mock_line_bot_api.reply_message.call_args.args[0]
        self.assertEqual(reply_token, reply_message_request.reply_token)
        self.assertEqual(1, len(reply_message_request.messages))
        self.assertEqual(
            Message.GREETING.format(self.line_display_name),
            reply_message_request.messages[0].text,
        )

    def test_existed_user_without_verification(self):
        """
        when a user is already added LINE OA and but didn't complete the verification,
        then the user should receive a registration message
        """
        # Arrange
        event = get_mock_event(FollowEvent)

        line_user_id = event.source.user_id
        reply_token = event.reply_token

        self._create_existed_user(line_user_id, None)

        # Act
        handle_follow(event)

        # Assert
        self.mock_line_bot_api.reply_message.assert_called_once()

        reply_message_request = self.mock_line_bot_api.reply_message.call_args.args[0]
        self.assertEqual(reply_token, reply_message_request.reply_token)
        self.assertEqual(2, len(reply_message_request.messages))
        self.assertEqual(
            Message.GREETING.format(self.line_display_name),
            reply_message_request.messages[0].text,
        )
        self.assertEqual(
            Message.REGISTER_PENDING, reply_message_request.messages[1].text
        )
