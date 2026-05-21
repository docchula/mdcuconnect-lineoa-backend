from django.db import models


class Profile(models.Model):
    class Status(models.TextChoices):
        PENDING_VERIFICATION = "PENDING_VERIFICATION", "Pending Verification"
        VERIFIED = "VERIFIED", "Verified"

    line_user_id = models.CharField(max_length=64)
    student_id = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING_VERIFICATION,
    )
    verification_token = models.CharField(
        max_length=64, blank=True, null=True, db_index=True
    )
    verification_token_expires_at = models.DateTimeField(blank=True, null=True)
