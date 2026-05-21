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
