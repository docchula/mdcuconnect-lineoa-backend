from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from profiles.models import Profile


class VerifyProfileViewTestCase(TestCase):
    def setUp(self):
        self.verify_url = reverse("verify-profile")

    def test_verify_profile_missing_token(self):
        """
        When token is missing from the query parameters,
        the endpoint should return 400 Bad Request.
        """
        # Act
        response = self.client.get(self.verify_url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Token is required."})

    def test_verify_profile_invalid_token(self):
        """
        When token does not exist in the database,
        the endpoint should return 404 Not Found.
        """
        # Act
        response = self.client.get(f"{self.verify_url}?token=non_existent_token")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {"error": "Invalid token."})

    def test_verify_profile_expired_token(self):
        """
        When token is expired (expiry time in the past),
        the endpoint should return 400 Bad Request and not verify the profile.
        """
        # Arrange
        profile = Profile.objects.create(
            line_user_id="U123456789",
            student_id="6422781234",
            email="test@example.com",
            verification_token="expired_token_123",
            verification_token_expires_at=timezone.now() - timedelta(seconds=1),
        )

        # Act
        response = self.client.get(f"{self.verify_url}?token=expired_token_123")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Token has expired."})

        # Verify status did not change and token remains active
        profile.refresh_from_db()
        self.assertEqual(profile.status, Profile.Status.PENDING_VERIFICATION)
        self.assertEqual(profile.verification_token, "expired_token_123")

    def test_verify_profile_success(self):
        """
        When token is valid and not expired,
        the profile should be marked as VERIFIED and token fields cleared.
        """
        # Arrange
        profile = Profile.objects.create(
            line_user_id="U987654321",
            student_id="6422789999",
            email="success@example.com",
            verification_token="valid_token_abc",
            verification_token_expires_at=timezone.now()
            + timedelta(hours=1),  # Expires in 1 hour
        )

        # Act
        response = self.client.get(f"{self.verify_url}?token=valid_token_abc")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "Profile verified successfully."})

        # Verify status is VERIFIED and token is cleared
        profile.refresh_from_db()
        self.assertEqual(profile.status, Profile.Status.VERIFIED)
        self.assertIsNone(profile.verification_token)
        self.assertIsNone(profile.verification_token_expires_at)
