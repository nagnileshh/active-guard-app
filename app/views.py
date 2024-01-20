from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MstUser, Token

class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_mob = request.data.get('user_mob')
        pin = request.data.get('pin')
        user = authenticate(user_mob=user_mob, pin=pin)
        if user:
            # Create or retrieve the token
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.token}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)