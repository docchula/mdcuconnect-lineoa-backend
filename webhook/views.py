from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import handle_webhook


X_LINE_SIGNATURE_KEY = "x-line-signature"


class Callback(APIView):
    def post(self, request):
        signature = request.headers.get(X_LINE_SIGNATURE_KEY, "")
        body = request.body.decode("utf-8")

        handle_webhook.delay(body, signature)

        return Response(status=status.HTTP_200_OK)
