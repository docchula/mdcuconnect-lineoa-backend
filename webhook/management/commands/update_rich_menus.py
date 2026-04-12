from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from linebot.v3.messaging import ApiClient, MessagingApi
from linebot.v3.messaging.api import MessagingApiBlob
from linebot.v3.messaging.exceptions import ApiException
from webhook.handlers.base import configuration
from webhook.constants import RichMenuNameEnum, RICH_MENU_MAPPINGS
from webhook.models import RichMenu
import os
import logging


logger = logging.getLogger(__name__)


NAME_KEY = "name"


class Command(BaseCommand):
    help = "Command line to update rich menus"

    def add_arguments(self, parser):
        parser.add_argument(f"--{NAME_KEY}", type=str, help="Rich menu name to update")

    def handle(self, *args, **options):
        rich_menu_name = options.get(NAME_KEY)
        if rich_menu_name is None:
            raise CommandError("Rich menu name is required")

        rich_menu_name = rich_menu_name.strip().lower()
        try:
            RichMenuNameEnum(rich_menu_name)
        except ValueError:
            raise CommandError(f"Rich menu name '{rich_menu_name}' is not available")

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api_blob = MessagingApiBlob(api_client)

        rich_menu_object = RichMenu.objects.filter(name=rich_menu_name).first()
        if rich_menu_object:
            line_bot_api.delete_rich_menu(rich_menu_object.rich_menu_id)

        rich_menu_request = RICH_MENU_MAPPINGS.get(rich_menu_name)

        try:
            line_bot_api.validate_rich_menu_object(rich_menu_request)
        except ApiException:
            logger.warning(
                f"Invalid payload for rich menu '{rich_menu_name}', skip creation"
            )
            return

        path_to_file = os.path.join(
            settings.BASE_DIR, "assets", "images", "rich_menus", f"{rich_menu_name}.jpg"
        )
        if not os.path.isfile(path_to_file):
            logger.warning("Image for rich menu '{name}' not found, skip creation")
            return

        response = line_bot_api.create_rich_menu(rich_menu_request)
        rich_menu_id = response.rich_menu_id

        with open(path_to_file, "rb") as image_file:
            line_bot_api_blob.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=image_file.read(),
                _headers={"Content-Type": "image/png"},
            )

        RichMenu.objects.update_or_create(
            name=rich_menu_name, defaults={"rich_menu_id": rich_menu_id}
        )

        logger.info(f"Rich menu '{rich_menu_name}' is created")
