from django.contrib.auth.backends import BaseBackend
from .models import MstUser
from django.contrib.auth.hashers import check_password

class MobileAuthBackend(BaseBackend):
    def authenticate(self, request, user_mob=None, pin=None):
        try:
            user = MstUser.objects.get(user_mob=user_mob)
            if user and check_password(pin, user.pin):
                return user
            return None
        except MstUser.DoesNotExist:
            return None