from datetime import timedelta
from unittest.mock import patch, MagicMock
import urllib.error

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


class RegisterProfileViewTestCase(TestCase):
    def setUp(self):
        self.register_url = reverse("register-profile")

    def test_register_profile_missing_fields(self):
        """
        When required fields are missing from the body,
        the endpoint should return 400 Bad Request.
        """
        response = self.client.post(
            self.register_url, {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"error": "accessToken, studentId, and email are required."},
        )

    @patch("urllib.request.urlopen")
    def test_register_profile_invalid_line_token(self, mock_urlopen):
        """
        When LINE API returns an error for the access token,
        the endpoint should return 400 Bad Request.
        """
        # Mock HTTPError
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.line.me/v2/profile",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        )

        payload = {
            "accessToken": "invalid_token",
            "studentId": "6422781234",
            "email": "test@example.com",
        }
        response = self.client.post(
            self.register_url, payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid LINE access token."})

    @patch("urllib.request.urlopen")
    def test_register_profile_success_new_profile(self, mock_urlopen):
        """
        When the access token is valid and fields are complete,
        a new profile should be created in PENDING_VERIFICATION status.
        """
        # Mock successful LINE response
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"userId": "U_test_user_123", "displayName": "Test User"}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        payload = {
            "accessToken": "valid_token",
            "studentId": "6422781234",
            "email": "test@example.com",
        }
        response = self.client.post(
            self.register_url, payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json()["message"],
            "Registration successful. Please verify your email.",
        )

        # Check database
        profile = Profile.objects.get(line_user_id="U_test_user_123")
        self.assertEqual(profile.student_id, "6422781234")
        self.assertEqual(profile.email, "test@example.com")
        self.assertEqual(profile.status, Profile.Status.PENDING_VERIFICATION)
        self.assertIsNotNone(profile.verification_token)
        self.assertIsNotNone(profile.verification_token_expires_at)

    @patch("urllib.request.urlopen")
    def test_register_profile_success_existing_profile(self, mock_urlopen):
        """
        When the profile already exists, registration should update the details and return 200 OK.
        """
        # Arrange: create an existing profile
        existing_profile = Profile.objects.create(
            line_user_id="U_existing_user",
            student_id="old_id",
            email="old@example.com",
            status=Profile.Status.VERIFIED,
        )

        # Mock successful LINE response
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"userId": "U_existing_user", "displayName": "Existing User"}'
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        payload = {
            "accessToken": "valid_token",
            "studentId": "new_id",
            "email": "new@example.com",
        }
        response = self.client.post(
            self.register_url, payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check database
        existing_profile.refresh_from_db()
        self.assertEqual(existing_profile.student_id, "new_id")
        self.assertEqual(existing_profile.email, "new@example.com")
        self.assertEqual(existing_profile.status, Profile.Status.PENDING_VERIFICATION)
        self.assertIsNotNone(existing_profile.verification_token)
