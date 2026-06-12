import json
import logging
import urllib.request
import uuid
from urllib.error import HTTPError

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile


class VerifyProfileView(APIView):
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = Profile.objects.filter(verification_token=token).first()
        if not profile:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if the token has expired
        if (
            profile.verification_token_expires_at
            and timezone.now() > profile.verification_token_expires_at
        ):
            return Response(
                {"error": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update profile status to VERIFIED and clear verification token
        profile.status = Profile.Status.VERIFIED
        profile.verification_token = None
        profile.verification_token_expires_at = None
        profile.save()

        return Response(
            {"message": "Profile verified successfully."},
            status=status.HTTP_200_OK,
        )


logger = logging.getLogger(__name__)


class RegisterProfileView(APIView):
    def post(self, request):
        access_token = request.data.get("accessToken")
        student_id = request.data.get("studentId")
        email = request.data.get("email")

        # Validate fields
        if not access_token or not student_id or not email:
            return Response(
                {"error": "accessToken, studentId, and email are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Call LINE API to verify accessToken and retrieve profile
        url = "https://api.line.me/v2/profile"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {access_token}")

        try:
            with urllib.request.urlopen(req) as response:
                line_data = json.loads(response.read().decode("utf-8"))
                line_user_id = line_data.get("userId")
        except HTTPError as e:
            logger.error(f"LINE API Error verifying access token: {e}")
            return Response(
                {"error": "Invalid LINE access token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception(f"Unexpected error calling LINE API: {e}")
            return Response(
                {"error": "Failed to connect to LINE service."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not line_user_id:
            return Response(
                {"error": "Could not retrieve user ID from LINE."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create or update profile
        profile, created = Profile.objects.get_or_create(line_user_id=line_user_id)
        profile.student_id = student_id
        profile.email = email
        profile.status = Profile.Status.PENDING_VERIFICATION
        profile.verification_token = uuid.uuid4().hex
        profile.verification_token_expires_at = timezone.now() + timezone.timedelta(
            hours=24
        )
        profile.save()

        return Response(
            {"message": "Registration successful. Please verify your email."},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
