from django.urls import path

from .views import VerifyProfileView, RegisterProfileView

urlpatterns = [
    path("verify", VerifyProfileView.as_view(), name="verify-profile"),
    path("register", RegisterProfileView.as_view(), name="register-profile"),
]
