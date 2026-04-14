from django.db import models


class RichMenu(models.Model):
    name = models.CharField(max_length=32)
    rich_menu_id = models.CharField(max_length=64)
