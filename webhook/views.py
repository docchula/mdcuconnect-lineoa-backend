from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from linebot.v3.exceptions import InvalidSignatureError
from .handlers import handler


class Callback(APIView):
    def post(self, request):
        signature = request.headers["X-Line-Signature"]
        body = request.body.decode("utf-8")

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return Response(
                {"message": "invalid signature"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_200_OK)
