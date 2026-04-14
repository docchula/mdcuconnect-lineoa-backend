from django.test import SimpleTestCase
from webhook.utils import build_text_messages


class BuildTextMessagesTestCase(SimpleTestCase):
    def test_empty_messages(self):
        # Arrange
        messages = []

        # Act
        result = build_text_messages(*messages)

        # Assert
        self.assertEqual(0, len(result))

    def test_multiple_messages(self):
        # Arrange
        messages = ["Hello", "World", "1234"]

        # Act
        result = build_text_messages(*messages)

        # Assert
        self.assertEqual(len(messages), len(result))

        for original_message, text_message in zip(messages, result):
            self.assertEqual(original_message, text_message.text)
