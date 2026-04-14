from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from unittest.mock import patch, MagicMock
from linebot.v3.messaging import RichMenuIdResponse
from linebot.v3.messaging.exceptions import ApiException
from webhook.models import RichMenu
import os


class UpdateRichMenusCommandTestCase(TestCase):
    def setUp(self):
        self.command = "update_rich_menus"
        self.rich_menu_name = "register"
        self.rich_menu_id = "richmenu-de7bcd264c0b50ca52b4e6e7a7ac4329"

        self.patcher_api_client = patch(
            "webhook.management.commands.update_rich_menus.ApiClient"
        )
        self.patcher_messaging_api = patch(
            "webhook.management.commands.update_rich_menus.MessagingApi"
        )
        self.patcher_messaging_api_blob = patch(
            "webhook.management.commands.update_rich_menus.MessagingApiBlob"
        )

        self.mock_api_client = self.patcher_api_client.start()
        self.mock_messaging_api = self.patcher_messaging_api.start()
        self.mock_messaging_api_blob = self.patcher_messaging_api_blob.start()

        self.mock_line_bot_api = MagicMock()
        self.mock_line_bot_api.delete_rich_menu.return_value = None
        self.mock_line_bot_api.create_rich_menu.return_value = RichMenuIdResponse(
            richMenuId=self.rich_menu_id
        )
        self.mock_messaging_api.return_value = self.mock_line_bot_api

        self.mock_line_bot_api_blob = MagicMock()
        self.mock_line_bot_api_blob.set_rich_menu_image.return_value = None
        self.mock_messaging_api_blob.return_value = self.mock_line_bot_api_blob

    def tearDown(self):
        self.patcher_api_client.stop()
        self.patcher_messaging_api.stop()
        self.patcher_messaging_api_blob.stop()

    def test_update_new_rich_menu(self):
        # Arrange
        rich_menu_count_before = RichMenu.objects.count()

        # Act
        call_command(self.command, name=self.rich_menu_name)

        # Asssert
        rich_menu_count_after = RichMenu.objects.count()
        self.assertEqual(rich_menu_count_before + 1, rich_menu_count_after)

        rich_menu = RichMenu.objects.filter(
            name=self.rich_menu_name, rich_menu_id=self.rich_menu_id
        )
        self.assertTrue(rich_menu.exists())

    def test_update_existing_rich_menu(self):
        # Arrange
        old_rich_menu_id = "123"
        RichMenu.objects.create(name=self.rich_menu_name, rich_menu_id=old_rich_menu_id)

        rich_menu_count_before = RichMenu.objects.count()

        # Act
        call_command(self.command, name=self.rich_menu_name)

        # Asssert
        rich_menu_count_after = RichMenu.objects.count()
        self.assertEqual(rich_menu_count_before, rich_menu_count_after)

        new_rich_menu = RichMenu.objects.filter(
            name=self.rich_menu_name, rich_menu_id=self.rich_menu_id
        )
        self.assertTrue(new_rich_menu.exists())

        old_rich_menu = RichMenu.objects.filter(
            name=self.rich_menu_name, rich_menu_id=old_rich_menu_id
        )
        self.assertFalse(old_rich_menu.exists())

    def test_missing_rich_menu_name(self):
        # Act & Assert
        with self.assertRaisesMessage(CommandError, "Rich menu name is required"):
            call_command(self.command)

    def test_invalid_rich_menu_name(self):
        # Arrange
        invalid_rich_menu_name = "foo-bar"

        # Act & Assert
        with self.assertRaisesMessage(
            CommandError, f"Rich menu name '{invalid_rich_menu_name}' is not available"
        ):
            call_command(self.command, name=invalid_rich_menu_name)

    def test_missing_rich_menu_image(self):
        # Arrange
        patcher_os = patch("webhook.management.commands.update_rich_menus.os")
        mock_os = patcher_os.start()
        self.addCleanup(patcher_os.stop)

        mock_os.path.join.side_effect = os.path.join
        mock_os.path.isfile.return_value = False

        # Act & Assert
        with self.assertRaisesMessage(
            CommandError, f"Image for rich menu '{self.rich_menu_name}' not found"
        ):
            call_command(self.command, name=self.rich_menu_name)

    def test_invalid_rich_menu_payload(self):
        # Arrange
        self.mock_line_bot_api.validate_rich_menu_object.side_effect = ApiException()

        # Act & Assert
        with self.assertRaisesMessage(
            CommandError, f"Invalid payload for rich menu '{self.rich_menu_name}'"
        ):
            call_command(self.command, name=self.rich_menu_name)
