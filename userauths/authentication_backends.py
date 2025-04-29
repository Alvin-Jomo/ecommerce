from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrPhoneOrUsernameBackend(BaseBackend):
    def authenticate(self, request, identifier=None, password=None, **kwargs):
        try:
            # Check identifier: username, email, or phone
            user = User.objects.get(username=identifier) if User.objects.filter(username=identifier).exists() else (
                   User.objects.get(email=identifier) if User.objects.filter(email=identifier).exists() else (
                   User.objects.get(phone=identifier) if User.objects.filter(phone=identifier).exists() else None))
            if user and user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
