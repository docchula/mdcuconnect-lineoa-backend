from django.urls import path

from .views import VerifyProfileView

urlpatterns = [
    path("verify", VerifyProfileView.as_view(), name="verify-profile"),
]
