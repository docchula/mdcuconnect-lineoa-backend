from django.db import models


class Profile(models.Model):
    line_user_id = models.CharField(max_length=64)
    student_id = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)
